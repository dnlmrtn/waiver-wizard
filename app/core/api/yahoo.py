from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa

YEAR = '2023'

file_path = '/app/core/api/token.json'


class YahooFantasyAPIService:
    def __init__(self):
        sc = OAuth2(None, None, from_file=file_path)
        self.gm = yfa.Game(sc, 'nba')
        

    def get_leagues(self):
        leagues = self.gm.league_ids(YEAR)
        return leagues

    def to_league(self, league_id):
        return self.gm.to_league(league_id)

    def get_free_agents(self, league_id):
        pass

    def get_all_players(self, league_id):
        lg = self.gm.to_league(league_id=league_id)
        return lg.free_agents("Util") + lg.taken_players()

    def get_player_stats(self, league_id, player_ids):
        lg = self.gm.to_league(league_id=league_id)
        return lg.player_stats(player_ids, 'average_season', season=YEAR)
