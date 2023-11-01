import yahoo_fantasy_api as yfa

YEAR = 2023


class YahooFantasyAPIService:
    def __init__(self, sc, league_id):
        self.gm = yfa.Game(sc, 'nba')
        self.lg = self.gm.to_league(league_id)

    def get_all_players(self) -> list:
        return self.lg.free_agents("Util") + self.lg.taken_players()
    
    def get_player_details(self, player_ids) -> list:
        return self.lg.player_details(player_ids)

    def get_player_stats_last_month(self, player_ids) -> list:
        return self.lg.player_stats(player_ids, 'lastmonth', season=YEAR)
    
    def get_player_stats_season(self, player_ids) -> list:
        return self.lg.player_stats(player_ids, 'average_season', season=YEAR)
    
    def percent_owned(self, player_ids) -> list:
        return self.lg.percent_owned(player_ids)
