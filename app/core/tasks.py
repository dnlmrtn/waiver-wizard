import os
from celery import shared_task, Celery, task
from datetime import datetime
from celery.schedules import crontab
import logging

from core.api.yahoo import YahooFantasyAPIService
from yahoo_oauth import OAuth2

from django.core.exceptions import ObjectDoesNotExist
from .models import Players

import os

LEAGUE_ID = os.getenv('LEAGUE_ID')

@shared_task
def update_players():
    sc = OAuth2(None, None, from_file='core/api/token.json')
    yahoo_service = YahooFantasyAPIService(sc, league_id=LEAGUE_ID)
    
    # Fetch all players and stats
    all_players = yahoo_service.get_all_players()
    player_stats_season = yahoo_service.get_player_stats_season([player["player_id"] for player in all_players])
    player_details = yahoo_service.get_player_details([player["player_id"] for player in all_players])

    # Mapping stats by player_id for easy access
    stats_by_player_id = {stat['player_id']: stat for stat in player_stats_season}
    details_by_player_id = {detail['player_id']: detail for detail in player_details}

    player_data = []
    for player in all_players:
        player_id = player['player_id']
        stats = stats_by_player_id.get(player_id, {})
        details = details_by_player_id.get(str(player_id), {})
        print("details", details)

        if '-' in [stats.get('PTS', 0), stats.get('AST', 0), stats.get('REB', 0), stats.get('ST', 0), stats.get('BLK', 0), stats.get('TO', 0)]:
            continue

        points = stats.get('PTS', 0)
        assists = stats.get('AST', 0)
        rebounds = stats.get('REB', 0)
        steals = stats.get('STL', 0)
        blocks = stats.get('BLK', 0)
        turnovers = stats.get('TO', 0)
        fan_pts = points +  1.2*rebounds + 1.5*assists + 3*steals + 3* blocks - 1.5*turnovers
        
        player_model, created = Players.objects.update_or_create(
            yahoo_id=player_id,
            defaults={
                'name': player['name'],
                'team': details['editorial_team_abbr'],
                'positions': ','.join(player['eligible_positions']).strip(",Util"),
                'status': 'H' if not player.get('status') else player['status'],
                'points_per_game': points,
                'assists_per_game': assists,
                'rebounds_per_game': rebounds,
                'steals_per_game': steals,
                'blocks_per_game': blocks,
                'to_per_game': turnovers,
                'fan_pts':fan_pts
            }
        )
