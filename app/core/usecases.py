from django.db.models import Q
from django.conf import settings

from core.api.yahoo import YahooFantasyAPIService
from yahoo_oauth import OAuth2

from .models import Player, Endpoint


class UpdatePlayerDataUseCase:
    def __init__(self):
        self.league_id = settings.LEAGUE_ID
        self.sc = OAuth2(None, None, from_file='core/api/token.json')
        self.yahoo_service = YahooFantasyAPIService(self.sc, league_id=self.league_id)


    def _get_stat_or_zero(self, stat):
        return 0 if stat == '-' else stat

    def _fetch_all_player_details_and_stats(self):
        """Fetches initial data from Yahoo API and indexes it."""
        # Fetch all players and stats
        all_players = self.yahoo_service.get_all_players()
        self.player_ids = [player['player_id'] for player in all_players]
        
        stats = self.yahoo_service.get_player_stats_season(self.player_ids)

        details = self.yahoo_service.get_player_details(self.player_ids)

        # Convert results to dict indexed by player ID 
        self.player_details_indexed_by_id = {
            int(player['player_id']): {
                'name': player['name']['full'],
                'headshot_url': player['headshot']['url'],
                'team': player['editorial_team_abbr'],
                'positions': ", ".join([p['position'] for p in player['eligible_positions'] 
                                      if p['position'] not in ["G", "F", "IL+", "IL", "Util"]])
            }
            for player in details
        }

        self.stats_indexed_by_id = {
            int(player['player_id']): {
                'PTS': player['PTS'],
                'REB': player['REB'],
                'AST': player['AST'],
                'STL': player['ST'],
                'BLK': player['BLK'],
                'TO': player['TO'],
            }
            for player in stats
        }

    def _get_player_details_and_stats(self, player_id):
        """Retrieves and validates player details and stats."""

        return {
            'details': self.player_details_indexed_by_id[player_id],
            'stats': self.stats_indexed_by_id[player_id]
        }

    def _extract_player_details(self, player_data):
        """Extracts basic player information from player data."""
        details = player_data['details']
        return {
            'name': details['name'],
            'team': details['team'],
            'headshot_url': details['headshot_url'],
            'positions': details['positions']
        }

    def _extract_basic_stats(self, player_data):
        """Extracts and validates basic statistical values."""
        stats = player_data['stats']
        return {
            'pts': self._get_stat_or_zero(stats.get('PTS', 0)),
            'ast': self._get_stat_or_zero(stats.get('AST', 0)),
            'reb': self._get_stat_or_zero(stats.get('REB', 0)),
            'st': self._get_stat_or_zero(stats.get('STL', 0)),
            'blk': self._get_stat_or_zero(stats.get('BLK', 0)),
            'to': self._get_stat_or_zero(stats.get('TO', 0))
        }

    def _calculate_player_stats(self, player_data):
        """Calculates all player statistics including fantasy points."""
        basic_stats = self._extract_basic_stats(player_data)
        
        fan_pts = (
            basic_stats['pts'] +
            1.2 * basic_stats['reb'] +
            1.5 * basic_stats['ast'] +
            3 * basic_stats['st'] +
            3 * basic_stats['blk'] -
            1.5 * basic_stats['to']
        )
        
        return {**basic_stats, 'fan_pts': fan_pts}

    def _save_player_to_database(self, player_id, player_data, stats):
        """Saves or updates player information in the database."""
        details = self._extract_player_details(player_data)
        
        Player.objects.update_or_create(
            yahoo_id=player_id,
            defaults={
                'name': details['name'],
                'team': details['team'],
                'photo_url': details['headshot_url'],
                'positions': details['positions'],
                'points_per_game': stats['pts'],
                'assists_per_game': stats['ast'],
                'rebounds_per_game': stats['reb'],
                'steals_per_game': stats['st'],
                'blocks_per_game': stats['blk'],
                'to_per_game': stats['to'],
                'fan_pts': stats['fan_pts']
            }
        )

    def update_player_stats(self):
        """Main method that orchestrates the player stats update process."""
        self._fetch_all_player_details_and_stats()  # Fetch and index all data by player ID first
        for player_id in self.player_ids:
            try:
                player_data = self._get_player_details_and_stats(player_id)
                stats = self._calculate_player_stats(player_data)
                self._save_player_to_database(player_id, player_data, stats)
            except Exception as e:
                raise e
        self.update_player_status()

        # Update endpoint with new data
        UpdateBenefittingPlayersEndpointUseCase().execute()

    def update_player_status(self):
        """Updates player status in the database."""
        all_players = self.yahoo_service.get_all_players()

        for player in all_players:
            player_id = player['player_id']
            player_model, _ = Player.objects.update_or_create(
                yahoo_id=player_id,
            )
            if player.get('status'):
                player_model.status = player.get('status')
                player_model.save()
            else:
                player_model.status = 'H'
                player_model.save()

        # Update endpoint with new data
        UpdateBenefittingPlayersEndpointUseCase().execute()
    

class UpdateBenefittingPlayersEndpointUseCase:
   def __init__(self):
       self.league_id = settings.LEAGUE_ID
       self.sc = OAuth2(None, None, from_file='core/api/token.json')
       self.yahoo_service = YahooFantasyAPIService(self.sc, league_id=self.league_id)

   def execute(self):
       """Main method to update the players endpoint with injury and benefiting player data."""
       self._clear_existing_endpoint()
       injured_players = self._get_injured_players()
       injured_players_data = self._process_injured_players(injured_players)
       self._save_endpoint(injured_players_data)

   def _clear_existing_endpoint(self):
       """Removes existing players endpoint data."""
       Endpoint.objects.filter(page='players').delete()

   def _get_injured_players(self):
       """
       Fetches injured players above fantasy point threshold.
       """
       injured_players = Player.objects.filter(
           (Q(status='INJ') | Q(status='O')) & 
           Q(fan_pts__gte=25)
       ).order_by("team", "-fan_pts")
       print(injured_players)

       return injured_players 
   def _get_benefiting_players(self, player):
       """Finds players who might benefit from an injury based on position and team."""
       positions = player.positions.split(",")
       
       same_team_and_fantasy_points_query = Q(team=player.team) & \
           Q(fan_pts__lt=player.fan_pts) & \
           Q(fan_pts__lt=35) & \
           Q(status='H')

       overlapping_positions_query = Q()
       for position in positions:
           overlapping_positions_query |= Q(positions__contains=position)

       return Player.objects.filter(
           same_team_and_fantasy_points_query & overlapping_positions_query
       ).exclude(
           id=player.id
       ).order_by("-fan_pts")[0:7]

   def _extract_player_stats(self, player):
       """Extracts basic stats for a player."""
       return [
           float(player.points_per_game),
           float(player.rebounds_per_game),
           float(player.assists_per_game),
           float(player.steals_per_game),
           float(player.blocks_per_game),
           float(player.to_per_game)
       ]

   def _get_percent_owned_map_by_ids(self, player_ids):
       """Returns a mapping of yahoo_id -> percent owned (float) for given IDs."""
       ownership_list = []

       try:
           ownership_list = self.yahoo_service.percent_owned(player_ids)
           print(ownership_list)
       except:
           pass


       id_to_owned = {}
       for entry in ownership_list or []:
           raw_player_id = entry.get('player_id')
           try:
               player_id = int(raw_player_id) if raw_player_id is not None else None
           except ValueError:
               player_id = None

           percent_value = entry.get('percent_owned')
           percent_value = float(percent_value)

           if player_id is not None:
               id_to_owned[player_id] = percent_value

       return id_to_owned

   def _process_injured_players(self, injured_players):
       """Processes each injured player and their potential beneficiaries."""
       injured_players_data = {}
       
       for player in injured_players:
           benefiting_players = self._get_benefiting_players(player)
           # Build ownership map for both injured and benefiting players in one call
           yahoo_ids = [int(player.yahoo_id)] + [int(p.yahoo_id) for p in benefiting_players]
           id_to_owned = self._get_percent_owned_map_by_ids(yahoo_ids)

           # Build benefiting players detailed data
           benefiting_players_data = {
               p.name: {
                   'photo_url': p.photo_url,
                   'stats': self._extract_player_stats(p),
                   'percent_owned': id_to_owned.get(int(p.yahoo_id))
               }
               for p in benefiting_players
           }

           injured_players_data[player.name] = {
               'photo_url': player.photo_url,
               'stats': self._extract_player_stats(player),
               'percent_owned': id_to_owned.get(int(player.yahoo_id)),
               'benefiting_players': benefiting_players_data,
               'time_of_injury': player.time_of_last_update.isoformat(),
               'status': player.status,
           }

       return injured_players_data

   def _save_endpoint(self, injured_players_data):
       """Saves the processed data to the endpoint."""
       Endpoint.objects.create(
           page="players", 
           data=injured_players_data
       )

