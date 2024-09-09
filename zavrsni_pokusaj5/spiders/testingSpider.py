#Testing spider: collects data from May 2024
import scrapy
import pandas as pd
from datetime import datetime
from zavrsni_pokusaj5.items import GameItem, PlayerItem, TeamItem

class TestingspiderSpider(scrapy.Spider):
    name = "testingSpider"
    allowed_domains = ["www.basketball-reference.com"]
    start_urls = ["https://www.basketball-reference.com/leagues/NBA_2024_games-may.html"]
    collected_game_items = []
    collected_player_items = []
    collected_team_items = []

    def parse(self, response):
        games_table = response.css('#content #all_schedule #div_schedule table tbody tr')
        for game in games_table:
            game_item = self.parse_game_row(game)
            self.collected_game_items.append(game_item)

            player_stats_link = game.css('td[data-stat="box_score_text"] a').attrib['href']
            full_player_stats_url = response.urljoin(player_stats_link)

            # Request the player and team stats from the box score page
            yield scrapy.Request(
                full_player_stats_url,
                callback=self.parse_stats,
                cb_kwargs={'game_item': game_item}
            )

    def parse_game_row(self, game):
        """Parses a single game row to create a GameItem object."""
        game_item = GameItem()
        game_item['gameDate'] = game.css('th a::text').get()
        game_item['visitorsTeam'] = game.css('td[data-stat="visitor_team_name"] a::text').get()
        game_item['visitorsTeamPoints'] = game.css('td[data-stat="visitor_pts"] ::text').get()
        game_item['homeTeam'] = game.css('td[data-stat="home_team_name"] a::text').get()
        game_item['homeTeamPoints'] = game.css('td[data-stat="home_pts"] ::text').get()
        return game_item

    def parse_stats(self, response, game_item):
        # Parse team stats
        self.parse_team_stats(response, game_item)

        # Parse player stats
        self.parse_player_stats(response, game_item)

    def parse_team_stats(self, response, game_item):
        """Parses team statistics from the response."""
        team_stats = response.css('#content [id^="all_box-"][id$="-game-basic"] table tfoot tr')
        if len(team_stats) < 2:
            self.log(f"Error parsing team stats for game on {game_item['gameDate']}", level=scrapy.log.ERROR)
            return

        visitor_stats, home_stats = team_stats[0], team_stats[1]

        self.collected_team_items.append(self.create_team_item(visitor_stats, game_item, True))
        self.collected_team_items.append(self.create_team_item(home_stats, game_item, False))

    def create_team_item(self, team_stats, game_item, is_visitor):
        """Helper method to create a TeamItem object."""
        team_item = TeamItem()
        team_item['gameDate'] = game_item['gameDate']
        team_item['team'] = game_item['visitorsTeam'] if is_visitor else game_item['homeTeam']
        team_item['opponentTeam'] = game_item['homeTeam'] if is_visitor else game_item['visitorsTeam']
        team_item['minutesPlayed'] = team_stats.css('td[data-stat="mp"] ::text').get()
        team_item['points'] = team_stats.css('td[data-stat="pts"] ::text').get()
        team_item['fieldGoalsMade'] = team_stats.css('td[data-stat="fg"] ::text').get()
        team_item['fieldGoalsAttempted'] = team_stats.css('td[data-stat="fga"] ::text').get()
        team_item['threePointMade'] = team_stats.css('td[data-stat="fg3"] ::text').get()
        team_item['threePointAttempted'] = team_stats.css('td[data-stat="fg3a"] ::text').get()
        team_item['freeThrowsMade'] = team_stats.css('td[data-stat="ft"] ::text').get()
        team_item['freeThrowsAttempted'] = team_stats.css('td[data-stat="fta"] ::text').get()
        team_item['assists'] = team_stats.css('td[data-stat="ast"] ::text').get()
        team_item['rebounds'] = team_stats.css('td[data-stat="trb"] ::text').get()
        team_item['steals'] = team_stats.css('td[data-stat="stl"] ::text').get()
        team_item['blocks'] = team_stats.css('td[data-stat="blk"] ::text').get()
        team_item['turnovers'] = team_stats.css('td[data-stat="tov"] ::text').get()
        team_item['personalFouls'] = team_stats.css('td[data-stat="pf"] ::text').get()
        return team_item

    def parse_player_stats(self, response, game_item):
        """Parses player statistics from the response."""
        players_tables = response.css('#content [id^="all_box-"][id$="-game-basic"] table tbody')
        
        visitors_players = players_tables[0].css('tr:not(.thead)')
        for visitor_player in visitors_players:
            self.collected_player_items.append(
                self.create_player_item(visitor_player, game_item, True)
            )

        home_players = players_tables[1].css('tr:not(.thead)')
        for home_player in home_players:
            self.collected_player_items.append(
                self.create_player_item(home_player, game_item, False)
            )

    def create_player_item(self, player_row, game_item, is_visitor):
        """Helper method to create a PlayerItem object."""
        player_item = PlayerItem()
        player_item['gameDate'] = game_item['gameDate']
        player_item['team'] = game_item['visitorsTeam'] if is_visitor else game_item['homeTeam']
        player_item['opponentTeam'] = game_item['homeTeam'] if is_visitor else game_item['visitorsTeam']
        player_item['playerName'] = player_row.css('th a::text').get()
        player_item['minutesPlayed'] = player_row.css('td[data-stat="mp"] ::text').get()
        player_item['points'] = player_row.css('td[data-stat="pts"] ::text').get()
        player_item['fieldGoalsMade'] = player_row.css('td[data-stat="fg"] ::text').get()
        player_item['fieldGoalsAttempted'] = player_row.css('td[data-stat="fga"] ::text').get()
        player_item['threePointMade'] = player_row.css('td[data-stat="fg3"] ::text').get()
        player_item['threePointAttempted'] = player_row.css('td[data-stat="fg3a"] ::text').get()
        player_item['freeThrowsMade'] = player_row.css('td[data-stat="ft"] ::text').get()
        player_item['freeThrowsAttempted'] = player_row.css('td[data-stat="fta"] ::text').get()
        player_item['assists'] = player_row.css('td[data-stat="ast"] ::text').get()
        player_item['rebounds'] = player_row.css('td[data-stat="trb"] ::text').get()
        player_item['steals'] = player_row.css('td[data-stat="stl"] ::text').get()
        player_item['blocks'] = player_row.css('td[data-stat="blk"] ::text').get()
        player_item['turnovers'] = player_row.css('td[data-stat="tov"] ::text').get()
        player_item['personalFouls'] = player_row.css('td[data-stat="pf"] ::text').get()
        player_item['plusMinus'] = player_row.css('td[data-stat="plus_minus"] ::text').get()
        return player_item

    def closed(self, reason):
        self.save_to_csv('../scraped_data/may_games_data.csv', self.collected_game_items, "may_games_data.csv")
        self.save_to_csv('../scraped_data/may_teams_data.csv', self.collected_team_items, "may_teams_data.csv")
        self.save_to_csv('../scraped_data/may_players_data.csv', self.collected_player_items, "may_players_data.csv")

    def save_to_csv(self, filename, collected_items, log_message):
        """Helper method to save collected items to a CSV file."""
        if collected_items:
            data = [dict(item) for item in collected_items]
            df = pd.DataFrame(data)
            df['gameDate'] = pd.to_datetime(df['gameDate'], format='%a, %b %d, %Y')
            df.to_csv(filename, index=False)
            self.log(f"{log_message} file created successfully.")




        
