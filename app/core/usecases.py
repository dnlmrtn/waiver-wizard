import requests
import json
import os
import asyncio
import aiohttp

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
                    'percent_owned': self.yahoo_service.get_percent_owned(player['player_id']),
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
                'positions': details['positions'],
                'percent_owned': details['percent_owned'],
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
                    'fan_pts': stats['fan_pts'],
                    'percent_owned': details['percent_owned'],
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
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY', '')
        self.openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
        self.openrouter_model = "meta-llama/llama-3.2-3b-instruct"  # Fast, cheap model


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
                    ).order_by("-fan_pts")[0:2]


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


    async def _llm_analysis(self, injured_player, backup_player, session):
        """Use LLM to generate benefitting score and message for a backup player."""
        if not self.openrouter_api_key:
            return {
                    'benefitting_score': 50,
                    'message': f"Backup at {backup_player.positions} - likely to see increased minutes."
                    }

        prompt = f"""Analyze this fantasy basketball injury situation:
        INJURED: {injured_player.name}
        - Positions: {injured_player.positions}
        - Stats: {injured_player.fan_pts} fantasy pts/game
        - Status: {injured_player.status}
        BACKUP: {backup_player.name}
        - Positions: {backup_player.positions}
        - Stats: {backup_player.fan_pts} fantasy pts/game
        Respond ONLY with valid JSON (no markdown):
        {{
          "benefitting_score": <number 0-100 based on opportunity>,
          "message": "<1-2 sentences on why to add them>"
        }}"""

        try:
            async with session.post(
                    self.openrouter_url,
                    headers={
                        "Authorization": f"Bearer {self.openrouter_api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://yoursite.com",
                        "X-Title": "Fantasy Basketball Analyzer"
                        },
                    json={
                        "model": self.openrouter_model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a fantasy basketball analyst. Be concise and actionable."
                                },
                            {
                                "role": "user",
                                "content": prompt
                                }
                            ],
                        "temperature": 0.3,
                        "max_tokens": 150
                        },
                    timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                result = await response.json()
                content = result['choices'][0]['message']['content']

                # Clean up markdown fences if present
                content = content.replace("```json", "").replace("```", "").strip()
                analysis = json.loads(content)

                print({
                    'benefitting_score': analysis.get('benefitting_score', 50),
                    'message': analysis.get('message', 'Potential streaming option.')
                    })

                return {
                        'benefitting_score': analysis.get('benefitting_score', 50),
                        'message': analysis.get('message', 'Potential streaming option.')
                        }

        except Exception as e:
            print(f"LLM analysis error for {backup_player.name}: {e}")
            return {
                    'benefitting_score': 50,
                    'message': f"Backup option at {backup_player.positions}."
                    }


    async def _analyze_all_benefiting_players(self, injured_player, benefiting_players, max_concurrent=50):
        """
        Analyze all benefiting players for a single injured player concurrently.
        
        Args:
            injured_player: The injured Player model instance
            benefiting_players: QuerySet of potential benefiting players
            max_concurrent: Maximum concurrent API requests (default 50 for free tier)
            
        Returns:
            List of analysis results in same order as benefiting_players
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def limited_analyze(backup_player, session):
            async with semaphore:
                return await self._llm_analysis(injured_player, backup_player, session)
        
        async with aiohttp.ClientSession() as session:
            tasks = [
                limited_analyze(backup_player, session)
                for backup_player in benefiting_players
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any exceptions in results
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    backup_player = benefiting_players[i]
                    print(f"Error analyzing {backup_player.name}: {result}")
                    processed_results.append({
                        'benefitting_score': 50,
                        'message': f"Backup option at {backup_player.positions}."
                    })
                else:
                    processed_results.append(result)
            
            return processed_results


    def _process_injured_players(self, injured_players):
        """Processes each injured player and their potential beneficiaries."""
        injured_players_data = {}

        for player in injured_players:
            benefiting_players = self._get_benefiting_players(player)

            # Build ownership map for both injured and benefiting players in one call
            yahoo_ids = [int(player.yahoo_id)] + [int(p.yahoo_id) for p in benefiting_players]
            id_to_owned = self._get_percent_owned_map_by_ids(yahoo_ids)

            # Run async LLM analysis for all benefiting players concurrently
            llm_analyses = asyncio.run(
                self._analyze_all_benefiting_players(player, benefiting_players)
            )

            benefiting_players_data = {}
            for p, llm_analysis in zip(benefiting_players, llm_analyses):
                benefiting_players_data[p.name] = {
                        'photo_url': p.photo_url,
                        'stats': self._extract_player_stats(p),
                        'percent_owned': id_to_owned.get(int(p.yahoo_id)),
                        'benefitting_score': llm_analysis['benefitting_score'],
                        'message': llm_analysis['message']
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
