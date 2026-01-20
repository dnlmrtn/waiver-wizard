import json
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
from datetime import datetime

from django.test import TestCase
from django.conf import settings

from core.models import Player, Endpoint
from core.usecases import UpdatePlayerDataUseCase, UpdateBenefittingPlayersEndpointUseCase


class UpdatePlayerDataUseCaseTest(TestCase):
    """Tests for UpdatePlayerDataUseCase"""

    def setUp(self):
        """Set up test fixtures"""
        self.use_case = UpdatePlayerDataUseCase()
        
        # Sample player data from Yahoo API
        self.sample_player_data = {
            'player_id': '12345',
            'name': {'full': 'LeBron James'},
            'headshot': {'url': 'http://example.com/lebron.jpg'},
            'editorial_team_abbr': 'LAL',
            'eligible_positions': [
                {'position': 'PG'},
                {'position': 'SF'},
                {'position': 'G'},  # Should be filtered out
                {'position': 'Util'}  # Should be filtered out
            ]
        }
        
        self.sample_stats = {
            'player_id': '12345',
            'PTS': '25.5',
            'REB': '8.2',
            'AST': '7.8',
            'ST': '1.5',
            'BLK': '0.8',
            'TO': '3.2'
        }

    @patch.object(UpdatePlayerDataUseCase, 'update_player_status')
    @patch('core.usecases.UpdateBenefittingPlayersEndpointUseCase')
    @patch.object(UpdatePlayerDataUseCase, '_fetch_all_player_details_and_stats')
    def test_update_player_stats_success(self, mock_fetch, mock_endpoint_usecase, mock_update_status):
        """Test successful player stats update"""
        # Setup mocks
        mock_fetch.return_value = None
        self.use_case.player_ids = ['12345']
        self.use_case.player_details_indexed_by_id = {
            12345: {
                'name': 'LeBron James',
                'headshot_url': 'http://example.com/lebron.jpg',
                'team': 'LAL',
                'positions': 'PG, SF'
            }
        }
        self.use_case.stats_indexed_by_id = {
            12345: {
                'PTS': 25.5,
                'REB': 8.2,
                'AST': 7.8,
                'STL': 1.5,
                'BLK': 0.8,
                'TO': 3.2
            }
        }
        
        # Execute
        self.use_case.update_player_stats()
        
        # Verify player was saved
        player = Player.objects.get(yahoo_id='12345')
        self.assertEqual(player.name, 'LeBron James')
        self.assertEqual(player.team, 'LAL')
        self.assertEqual(player.positions, 'PG, SF')
        self.assertEqual(float(player.points_per_game), 25.5)
        self.assertEqual(float(player.rebounds_per_game), 8.2)
        
        # Verify fan_pts calculation
        expected_fan_pts = 25.5 + 1.2*8.2 + 1.5*7.8 + 3*1.5 + 3*0.8 - 1.5*3.2
        self.assertAlmostEqual(float(player.fan_pts), expected_fan_pts, places=2)
        
        # Verify endpoint update was called
        mock_endpoint_usecase.return_value.execute.assert_called_once()

    def test_get_stat_or_zero_with_dash(self):
        """Test that dash values are converted to zero"""
        result = self.use_case._get_stat_or_zero('-')
        self.assertEqual(result, 0)

    def test_get_stat_or_zero_with_number(self):
        """Test that numeric values are preserved"""
        result = self.use_case._get_stat_or_zero(10.5)
        self.assertEqual(result, 10.5)

    def test_extract_player_details(self):
        """Test extraction of player details"""
        player_data = {
            'details': {
                'name': 'LeBron James',
                'team': 'LAL',
                'headshot_url': 'http://example.com/lebron.jpg',
                'positions': 'PG, SF'
            }
        }
        
        result = self.use_case._extract_player_details(player_data)
        
        self.assertEqual(result['name'], 'LeBron James')
        self.assertEqual(result['team'], 'LAL')
        self.assertEqual(result['positions'], 'PG, SF')

    def test_calculate_player_stats(self):
        """Test fantasy points calculation"""
        player_data = {
            'stats': {
                'PTS': 20,
                'REB': 10,
                'AST': 5,
                'STL': 2,
                'BLK': 1,
                'TO': 3
            }
        }
        
        result = self.use_case._calculate_player_stats(player_data)
        
        # fan_pts = 20 + 1.2*10 + 1.5*5 + 3*2 + 3*1 - 1.5*3
        expected_fan_pts = 20 + 12 + 7.5 + 6 + 3 - 4.5
        self.assertEqual(result['fan_pts'], expected_fan_pts)

    @patch('core.usecases.YahooFantasyAPIService')
    @patch('core.usecases.UpdateBenefittingPlayersEndpointUseCase')
    def test_update_player_status(self, mock_endpoint_usecase, mock_yahoo_service):
        """Test updating player injury status"""
        # Create test player
        Player.objects.create(
            yahoo_id='12345',
            name='LeBron James',
            status='H'
        )
        
        # Mock Yahoo API response
        mock_yahoo_instance = mock_yahoo_service.return_value
        mock_yahoo_instance.get_all_players.return_value = [
            {
                'player_id': '12345',
                'status': 'INJ'
            }
        ]
        
        # Execute
        use_case = UpdatePlayerDataUseCase()
        use_case.update_player_status()
        
        # Verify status was updated
        player = Player.objects.get(yahoo_id='12345')
        self.assertEqual(player.status, 'INJ')


class UpdateBenefittingPlayersEndpointUseCaseTest(TestCase):
    """Tests for UpdateBenefittingPlayersEndpointUseCase"""

    def setUp(self):
        """Set up test fixtures"""
        self.use_case = UpdateBenefittingPlayersEndpointUseCase()
        
        # Create test players
        self.injured_player = Player.objects.create(
            yahoo_id='11111',
            name='Steph Curry',
            team='GSW',
            positions='PG, SG',
            status='INJ',
            fan_pts=35.0,
            points_per_game=28.0,
            rebounds_per_game=5.0,
            assists_per_game=6.5,
            steals_per_game=1.2,
            blocks_per_game=0.3,
            to_per_game=2.8,
            photo_url='http://example.com/curry.jpg'
        )
        
        self.backup_player = Player.objects.create(
            yahoo_id='22222',
            name='Chris Paul',
            team='GSW',
            positions='PG',
            status='H',
            fan_pts=28.0,
            points_per_game=15.0,
            rebounds_per_game=4.0,
            assists_per_game=8.0,
            steals_per_game=1.5,
            blocks_per_game=0.2,
            to_per_game=2.0,
            photo_url='http://example.com/cp3.jpg'
        )

    def test_clear_existing_endpoint(self):
        """Test clearing existing endpoint data"""
        # Create existing endpoint
        Endpoint.objects.create(page='players', data={'test': 'data'})
        
        self.use_case._clear_existing_endpoint()
        
        self.assertEqual(Endpoint.objects.filter(page='players').count(), 0)

    def test_get_injured_players(self):
        """Test fetching injured players above threshold"""
        # Create another injured player below threshold
        Player.objects.create(
            yahoo_id='33333',
            name='Low Scorer',
            status='INJ',
            fan_pts=20.0
        )
        
        injured = self.use_case._get_injured_players()
        
        # Should only get player above 25 fan_pts
        self.assertEqual(len(injured), 1)
        self.assertEqual(injured[0].name, 'Steph Curry')

    def test_get_benefiting_players(self):
        """Test finding benefiting players"""
        # Create another backup on different team (shouldn't match)
        Player.objects.create(
            yahoo_id='44444',
            name='Different Team PG',
            team='LAL',
            positions='PG',
            status='H',
            fan_pts=25.0
        )
        
        benefiting = self.use_case._get_benefiting_players(self.injured_player)
        
        # Should only get same-team player
        self.assertEqual(len(benefiting), 1)
        self.assertEqual(benefiting[0].name, 'Chris Paul')

    def test_extract_player_stats(self):
        """Test extracting player stats array"""
        stats = self.use_case._extract_player_stats(self.injured_player)
        
        self.assertEqual(stats, [28.0, 5.0, 6.5, 1.2, 0.3, 2.8])

    @patch('core.usecases.requests.post')
    def test_analyze_benefitting_player_success(self, mock_post):
        """Test LLM analysis with successful API response"""
        # Mock OpenRouter response
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': '{"benefitting_score": 75, "message": "CP3 will see increased usage with Curry out."}'
                }
            }]
        }
        mock_post.return_value = mock_response
        
        # Set API key
        self.use_case.openrouter_api_key = 'test_key'
        
        result = self.use_case._analyze_benefitting_player(
            self.injured_player,
            self.backup_player
        )
        
        self.assertEqual(result['benefitting_score'], 75)
        self.assertIn('CP3', result['message'])
        
        # Verify API was called correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertIn('Bearer test_key', call_args[1]['headers']['Authorization'])

    @patch('core.usecases.requests.post')
    def test_analyze_benefitting_player_with_markdown(self, mock_post):
        """Test LLM analysis handles markdown code fences"""
        # Mock response with markdown
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': '```json\n{"benefitting_score": 80, "message": "Great opportunity"}\n```'
                }
            }]
        }
        mock_post.return_value = mock_response
        
        self.use_case.openrouter_api_key = 'test_key'
        
        result = self.use_case._analyze_benefitting_player(
            self.injured_player,
            self.backup_player
        )
        
        self.assertEqual(result['benefitting_score'], 80)

    @patch('core.usecases.requests.post')
    def test_analyze_benefitting_player_api_error(self, mock_post):
        """Test LLM analysis falls back on API error"""
        mock_post.side_effect = Exception("API Error")
        
        self.use_case.openrouter_api_key = 'test_key'
        
        result = self.use_case._analyze_benefitting_player(
            self.injured_player,
            self.backup_player
        )
        
        # Should return fallback values
        self.assertEqual(result['benefitting_score'], 50)
        self.assertIn('Backup option', result['message'])

    def test_analyze_benefitting_player_no_api_key(self):
        """Test LLM analysis without API key"""
        self.use_case.openrouter_api_key = ''
        
        result = self.use_case._analyze_benefitting_player(
            self.injured_player,
            self.backup_player
        )
        
        # Should return fallback values
        self.assertEqual(result['benefitting_score'], 50)
        self.assertIn('likely to see increased minutes', result['message'])

    @patch.object(UpdateBenefittingPlayersEndpointUseCase, '_analyze_benefitting_player')
    @patch('core.usecases.YahooFantasyAPIService')
    def test_process_injured_players(self, mock_yahoo_service, mock_analyze):
        """Test processing injured players and their beneficiaries"""
        # Mock LLM analysis
        mock_analyze.return_value = {
            'benefitting_score': 85,
            'message': 'Strong pickup opportunity'
        }
        
        # Mock percent owned
        mock_yahoo_instance = mock_yahoo_service.return_value
        mock_yahoo_instance.percent_owned.return_value = [
            {'player_id': '11111', 'percent_owned': '95.5'},
            {'player_id': '22222', 'percent_owned': '45.2'}
        ]
        
        injured_players = [self.injured_player]
        result = self.use_case._process_injured_players(injured_players)
        
        # Verify structure
        self.assertIn('Steph Curry', result)
        injured_data = result['Steph Curry']
        
        self.assertEqual(injured_data['status'], 'INJ')
        self.assertEqual(injured_data['percent_owned'], 95.5)
        self.assertIn('Chris Paul', injured_data['benefiting_players'])
        
        # Verify benefiting player data
        cp3_data = injured_data['benefiting_players']['Chris Paul']
        self.assertEqual(cp3_data['benefitting_score'], 85)
        self.assertEqual(cp3_data['message'], 'Strong pickup opportunity')
        self.assertEqual(cp3_data['percent_owned'], 45.2)

    @patch.object(UpdateBenefittingPlayersEndpointUseCase, '_process_injured_players')
    @patch.object(UpdateBenefittingPlayersEndpointUseCase, '_get_injured_players')
    def test_execute_full_flow(self, mock_get_injured, mock_process):
        """Test complete execution flow"""
        mock_get_injured.return_value = [self.injured_player]
        mock_process.return_value = {'test': 'data'}
        
        # Create existing endpoint to verify clearing
        Endpoint.objects.create(page='players', data={'old': 'data'})
        
        self.use_case.execute()
        
        # Verify old endpoint was cleared
        endpoints = Endpoint.objects.filter(page='players')
        self.assertEqual(endpoints.count(), 1)
        self.assertEqual(endpoints.first().data, {'test': 'data'})

    def test_save_endpoint(self):
        """Test saving endpoint data"""
        test_data = {
            'Steph Curry': {
                'status': 'INJ',
                'benefiting_players': {}
            }
        }
        
        self.use_case._save_endpoint(test_data)
        
        endpoint = Endpoint.objects.get(page='players')
        self.assertEqual(endpoint.data, test_data)


class IntegrationTest(TestCase):
    """Integration tests for the full workflow"""

    @patch('core.usecases.requests.post')
    @patch('core.usecases.YahooFantasyAPIService')
    def test_full_injury_analysis_workflow(self, mock_yahoo_service, mock_llm):
        """Test complete workflow from injury to benefiting player analysis"""
        # Setup mock Yahoo API
        mock_yahoo_instance = mock_yahoo_service.return_value
        mock_yahoo_instance.get_all_players.return_value = [
            {'player_id': '12345', 'status': 'INJ'},
            {'player_id': '67890', 'status': 'H'}
        ]
        
        # Create test players
        injured = Player.objects.create(
            yahoo_id='12345',
            name='Star Player',
            team='LAL',
            positions='SG, SF',
            status='H',  # Will be updated to INJ
            fan_pts=30.0,
            points_per_game=25.0,
            rebounds_per_game=6.0,
            assists_per_game=5.0,
            steals_per_game=1.0,
            blocks_per_game=0.5,
            to_per_game=2.0
        )
        
        backup = Player.objects.create(
            yahoo_id='67890',
            name='Backup Player',
            team='LAL',
            positions='SG',
            status='H',
            fan_pts=20.0,
            points_per_game=12.0,
            rebounds_per_game=3.0,
            assists_per_game=3.0,
            steals_per_game=0.8,
            blocks_per_game=0.3,
            to_per_game=1.5
        )
        
        # Mock LLM response
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': '{"benefitting_score": 90, "message": "Excellent streming option with star out."}'
                }
            }]
        }
        mock_llm.return_value = mock_response
        
        # Mock percent owned
        mock_yahoo_instance.percent_owned.return_value = [
            {'player_id': '12345', 'percent_owned': '98.0'},
            {'player_id': '67890', 'percent_owned': '25.0'}
        ]
        
        # Execute update
        use_case = UpdatePlayerDataUseCase()
        use_case.openrouter_api_key = 'test_key'
        use_case.update_player_status()
        
        # Verify injury status was updated
        injured.refresh_from_db()
        self.assertEqual(injured.status, 'INJ')
        
        # Verify endpoint was created with benefiting player data
        endpoint = Endpoint.objects.get(page='players')
        self.assertIn('Star Player', endpoint.data)
        
        injured_data = endpoint.data['Star Player']
        self.assertIn('Backup Player', injured_data['benefiting_players'])
        
        backup_data = injured_data['benefiting_players']['Backup Player']
        self.assertEqual(backup_data['benefitting_score'], 90)
        self.assertIn('streaming option', backup_data['message'])
