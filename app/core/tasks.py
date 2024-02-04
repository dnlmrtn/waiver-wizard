import os
from celery import shared_task, Celery, task
from datetime import datetime
from celery.signals import worker_ready

from django.db.models import Q

from core.api.yahoo import YahooFantasyAPIService
from yahoo_oauth import OAuth2

from .models import Player, Endpoint

import os
import json

LEAGUE_ID = os.getenv('LEAGUE_ID')


def get_stat_or_zero(stat):
    return 0 if stat == '-' else stat


@shared_task
def update_player_stats():
    sc = OAuth2(None, None, from_file='core/api/token.json')
    yahoo_service = YahooFantasyAPIService(sc, league_id=LEAGUE_ID)

    # Fetch all players and stats
    all_players = yahoo_service.get_all_players()
    player_stats_season = yahoo_service.get_player_stats_season(
        [player["player_id"] for player in all_players])
    player_details = yahoo_service.get_player_details(
        [player["player_id"] for player in all_players])

    # Mapping stats by player_id for easy access
    stats_by_player_id = {stat['player_id']: stat for stat in player_stats_season}
    details_by_player_id = {detail['player_id']: detail for detail in player_details}

    for player in all_players:

        player_id = player['player_id']
        stats = stats_by_player_id.get(player_id, {})
        details = details_by_player_id.get(str(player_id), {})
        pts = get_stat_or_zero(stats.get('PTS', 0))
        ast = get_stat_or_zero(stats.get('AST', 0))
        reb = get_stat_or_zero(stats.get('REB', 0))
        st = get_stat_or_zero(stats.get('ST', 0))
        blk = get_stat_or_zero(stats.get('BLK', 0))
        to = get_stat_or_zero(stats.get('TO', 0))

        fan_pts = pts + 1.2*reb + 1.5*ast + 3*st + 3*blk - 1.5*to

        player_model, created = Player.objects.update_or_create(
            yahoo_id=player_id,
            defaults={
                'name': player['name'],
                'team': details['editorial_team_abbr'],
                'photo_url': details["image_url"],
                'positions': ", ".join([p for p in player["eligible_positions"] if p not in ["G", "F", "IL+", "IL", "Util"]]),
                'status': 'H' if not player.get('status') else player['status'],
                'points_per_game': pts,
                'assists_per_game': ast,
                'rebounds_per_game': reb,
                'steals_per_game': st,
                'blocks_per_game': blk,
                'to_per_game': to,
                'fan_pts': fan_pts
            }
        )

    # Update the endpoins
    update_players_endpoint()


@shared_task
def update_player_status():
    sc = OAuth2(None, None, from_file='core/api/token.json')
    yahoo_service = YahooFantasyAPIService(sc, league_id=LEAGUE_ID)

    # Fetch all players and stats
    all_players = yahoo_service.get_all_players()

    for player in all_players:
        player_id = player['player_id']

        player_model, created = Player.objects.update_or_create(
            yahoo_id=player_id,
        )

        player_model.status = 'H' if not player.get(
            'status') else player['status']
        player_model.save()


def update_players_endpoint():
    # Clear existing players endpoint objects
    Endpoint.objects.filter(page='players').delete()

    # Update players endpoint
    injured = Player.objects.filter((Q(status='INJ') | Q(status='O')) & Q(
        fan_pts__gte=25)).order_by("team", "-fan_pts")

    injured_players = {}
    for player in injured:

        positions = player.positions.split(",")
        same_team_and_fantasy_points_query = Q(team=player.team) & Q(
            fan_pts__lt=player.fan_pts) & Q(fan_pts__lt=35) & Q(status='H')

        overlapping_positions_query = Q()
        for position in positions:
            overlapping_positions_query |= Q(positions__contains=position)

        benefiting_players = Player.objects.filter(
            same_team_and_fantasy_points_query & overlapping_positions_query
        ).exclude(
            id=player.id
        ).order_by("-fan_pts")[0:7]

        benefiting_players_with_stats = {
            benefiting_player.name: [
                float(benefiting_player.points_per_game),
                float(benefiting_player.rebounds_per_game),
                float(benefiting_player.assists_per_game),
                float(benefiting_player.steals_per_game),
                float(benefiting_player.blocks_per_game),
                float(benefiting_player.to_per_game)
            ] for benefiting_player in benefiting_players
        }

        injured_players[player.name] = {
            'photo_url': player.photo_url,
            'stats': [
                float(player.points_per_game),
                float(player.rebounds_per_game),
                float(player.assists_per_game),
                float(player.steals_per_game),
                float(player.blocks_per_game),
                float(player.to_per_game)
            ],
            'benefiting_players': benefiting_players_with_stats,
            # Convert datetime to ISO 8601 string
            'time_of_injury': player.time_of_last_update.isoformat(),
            'status': player.status,
        }

    Endpoint.objects.create(
        page="players", data=json.dumps(injured_players))


@worker_ready.connect
def at_start(sender, **kwargs):
    with sender.app.connection() as conn:
        sender.app.send_task('core.tasks.update_player_stats')
