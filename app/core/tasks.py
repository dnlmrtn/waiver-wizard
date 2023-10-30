import os
from celery import shared_task, Celery, task
from datetime import datetime
from celery.schedules import crontab

from core.api.yahoo import YahooFantasyAPIService
from yahoo_oauth import OAuth2

from django.core.exceptions import ObjectDoesNotExist
from .models import Players


@shared_task
def update_players():
    # Initialize Yahoo Fantasy API service
    sc = OAuth2(None, None, from_file='core/api/token.json')
    yahoo_service = YahooFantasyAPIService(sc)

    # Fetch all players and their statistics
    all_players = yahoo_service.get_all_players('418.l.101921')

    player_ids = [player['player_id'] for player in all_players]
    player_stats = yahoo_service.get_player_stats('418.l.101921', player_ids)

    # Create a mapping of player_id to stats for quick look-up
    player_stats_mapping = {stats['player_id']: stats for stats in player_stats}

    # Loop through all players and update the Player model
    for player_data in all_players:
        player_id = player_data['player_id']
        stats = player_stats_mapping.get(player_id, {})

        # Create or update the Player model
        defaults = {
            'name': player_data['name'],
            'team': '',  # Yahoo API doesn't seem to provide team info in the example
            'positions': ', '.join(player_data.get('eligible_positions', [])),
            'status': player_data.get('status', 'active'),
            'percent_owned': player_data.get('percent_owned', 0),
            'minutes_per_game': 0,  # Yahoo API doesn't seem to provide this info in the example
            'points_per_game': stats.get('PTS', 0),
            'assists_per_game': stats.get('AST', 0),
            'rebounds_per_game': stats.get('REB', 0),
            'steals_per_game': stats.get('ST', 0),
            'blocks_per_game': stats.get('BLK', 0),
            'threes_per_game': 0,  # Yahoo API doesn't seem to provide this info in the example
            'fg': 0,  # Yahoo API doesn't seem to provide this info in the example
            'ft': 0,  # Yahoo API doesn't seem to provide this info in the example
            'to_per_game': stats.get('TO', 0),
        }
        try:
            player, created = Players.objects.update_or_create(
                yahoo_id=str(player_id), defaults=defaults)
            if created:
                print(f"Created new player: {player.name}")
            else:
                print(f"Updated existing player: {player.name}")
        except ObjectDoesNotExist:
            print(
                f"Could not find or create a Player with Yahoo ID {player_id}")

'''
@app.task
def update_players():
    print(all_players)
    # Initialize Yahoo Fantasy API service
    sc = OAuth2(None, None, from_file='./api/token.json')
    yahoo_service = YahooFantasyAPIService(sc)

    # Fetch all players and their statistics
    all_players = yahoo_service.get_all_players('418.l.101921')

    player_ids = [player['player_id'] for player in all_players]
    player_stats = yahoo_service.get_player_stats('418.l.101921', player_ids)

    # Create a mapping of player_id to stats for quick look-up
    player_stats_mapping = {stats['player_id']: stats for stats in player_stats}

    # Loop through all players and update the Player model
    for player_data in all_players:
        player_id = player_data['player_id']
        stats = player_stats_mapping.get(player_id, {})

        # Create or update the Player model
        defaults = {
            'name': player_data['name'],
            'team': '',  # Yahoo API doesn't seem to provide team info in the example
            'positions': ', '.join(player_data.get('eligible_positions', [])),
            'status': player_data.get('status', 'active'),
            'percent_owned': player_data.get('percent_owned', 0),
            'minutes_per_game': 0,  # Yahoo API doesn't seem to provide this info in the example
            'points_per_game': stats.get('PTS', 0),
            'assists_per_game': stats.get('AST', 0),
            'rebounds_per_game': stats.get('REB', 0),
            'steals_per_game': stats.get('ST', 0),
            'blocks_per_game': stats.get('BLK', 0),
            'threes_per_game': 0,  # Yahoo API doesn't seem to provide this info in the example
            'fg': 0,  # Yahoo API doesn't seem to provide this info in the example
            'ft': 0,  # Yahoo API doesn't seem to provide this info in the example
            'to_per_game': stats.get('TO', 0),
        }
        try:
            player, created = Players.objects.update_or_create(
                yahoo_id=str(player_id), defaults=defaults)
            if created:
                print(f"Created new player: {player.name}")
            else:
                print(f"Updated existing player: {player.name}")
        except ObjectDoesNotExist:
            print(
                f"Could not find or create a Player with Yahoo ID {player_id}")'''
