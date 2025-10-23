import yahoo_fantasy_api as yfa

YEAR = 2025


class YahooFantasyAPIService:
    def __init__(self, sc, league_id):
        self.gm = yfa.Game(sc, 'nba')

        print(self.gm.league_ids())
        print(league_id)
        self.lg = self.gm.to_league("466.l.24543")

        print(self.lg.current_week())
        print(self.lg.end_week())

    def get_all_players(self) -> list:
        return self.lg.free_agents("Util") + self.lg.taken_players()
    
    def get_player_details(self, player_ids) -> list:
        return self.lg.player_details(player_ids)

    def get_player_stats_last_month(self, player_ids) -> list:
        return self.lg.player_stats(player_ids, 'lastmonth', season=YEAR)
    
    def get_player_stats_season(self, player_ids) -> list:
        return self.lg.player_stats(player_ids, 'average_season', season=YEAR)
    
    def get_percent_owned(self, player_ids) -> list:
        return self.lg.percent_owned(player_ids)
    
    def details(self):
        return self.lg.player_details("LeBron James")
