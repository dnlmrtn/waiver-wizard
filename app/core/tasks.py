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
    # Initialize Yahoo Fantasy API service
    sc = OAuth2(None, None, from_file='core/api/token.json')
    yahoo_service = YahooFantasyAPIService(sc, league_id=LEAGUE_ID)
    
    # Fetch all players
    all_players = yahoo_service.get_all_players()
    
    # Loop through each player to get details and update the database
    for player in all_players:
        player_id = player['player_id']
        
        # Fetch player details and stats
        player_details = yahoo_service.get_player_details([player_id])[0]
        player_stats = yahoo_service.get_player_stats_last_month([player_id])[0]
        
        # Update or Create player entry in the database
        Players.objects.update_or_create(
        yahoo_id=player_id,
        defaults={
            'name': player_details['name']['full'],
            'team': player_details['editorial_team_abbr'],
            'positions': ','.join([pos['position'] for pos in player_details['eligible_positions']]),
            'status': player_details.get('status', 'H'),  # If 'status' is not present, set it to 'H'
            'percent_owned': 0,
            'points_per_game': player_stats.get('PTS', 0),
            'assists_per_game': player_stats.get('AST', 0),
            'rebounds_per_game': player_stats.get('REB', 0),
            'steals_per_game': player_stats.get('ST', 0),
            'blocks_per_game': player_stats.get('BLK', 0),
            'to_per_game': player_stats.get('TO', 0)
        }
    )
