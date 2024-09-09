import scrapy
import pandas as pd
import os
from zavrsni_pokusaj5.items import GameItem, PlayerItem, TeamItem

class NbadataSpider(scrapy.Spider):
    name = 'nbaData'
    allowed_domains = ['basketball-reference.com']
    start_urls = ['https://www.basketball-reference.com/']

    def __init__(self, *args, **kwargs):
        super(NbadataSpider, self).__init__(*args, **kwargs)
        self.collected_game_items = []
        self.collected_team_items = []
        self.collected_player_items = []
        self.current_season = None

    def parse(self, response):
        base_url = 'https://www.basketball-reference.com/leagues/NBA_{}_games.html'
        seasons = range(2022, 2023)
        for season in seasons:
            self.current_season = season
            url_games = base_url.format(season)
            yield scrapy.Request(url_games, callback=self.parse_season_games)

    def parse_season_games(self, response):
        month_picker = response.css('#content .filter div')
        for month_div in month_picker:
            games_by_month_url = month_div.css('a').attrib.get('href')
            if games_by_month_url:
                yield scrapy.Request(
                    response.urljoin(games_by_month_url),
                    callback=self.parse_games_by_month
                )

    def parse_games_by_month(self, response):
        games_table = response.css('#content #all_schedule #div_schedule table tbody tr')
        for game in games_table:
            game_item = self.extract_game_item(game)
            if game_item:
                self.collected_game_items.append(game_item)
                player_stats_link = game.css('td[data-stat="box_score_text"] a').attrib.get('href')
                if player_stats_link:
                    yield scrapy.Request(
                        response.urljoin(player_stats_link),
                        callback=self.parse_player_stats,
                        cb_kwargs={'game_item': game_item}
                    )

    def extract_game_item(self, game):
        # Extracts game information into a GameItem object.
        game_item = GameItem()
        game_item['gameDate'] = game.css('th a::text').get()
        game_item['visitorsTeam'] = game.css('td[data-stat="visitor_team_name"] a::text').get()
        game_item['visitorsTeamPoints'] = game.css('td[data-stat="visitor_pts"] ::text').get()
        game_item['homeTeam'] = game.css('td[data-stat="home_team_name"] a::text').get()
        game_item['homeTeamPoints'] = game.css('td[data-stat="home_pts"] ::text').get()

        if all(game_item.values()):
            return game_item
        return None

    def parse_player_stats(self, response, game_item):
        team_stats = response.css('#content [id^="all_box-"][id$="-game-basic"] table tfoot tr')
        visitors_stats = team_stats[0] if len(team_stats) > 0 else None
        home_stats = team_stats[1] if len(team_stats) > 1 else None

        if visitors_stats and home_stats:
            self.collected_team_items.append(self.extract_team_stats(visitors_stats, game_item, True))
            self.collected_team_items.append(self.extract_team_stats(home_stats, game_item, False))

        players_tables = response.css('#content [id^="all_box-"][id$="-game-basic"] table tbody')
        if players_tables:
            self.extract_players_stats(players_tables[0], game_item, True)
            self.extract_players_stats(players_tables[1], game_item, False)

    def extract_team_stats(self, stats, game_item, is_visitors):
        # Extracts team statistics into a TeamItem object.
        team_item = TeamItem()
        team_item['gameDate'] = game_item['gameDate']
        team_item['team'] = game_item['visitorsTeam'] if is_visitors else game_item['homeTeam']
        team_item['opponentTeam'] = game_item['homeTeam'] if is_visitors else game_item['visitorsTeam']
        team_item.update(self.extract_stats(stats))

        return team_item

    def extract_players_stats(self, players, game_item, is_visitors):
        # Extracts statistics for all players in a given team.
        for player in players.css('tr:not(.thead)'):
            player_item = PlayerItem()
            player_item['gameDate'] = game_item['gameDate']
            player_item['team'] = game_item['visitorsTeam'] if is_visitors else game_item['homeTeam']
            player_item['opponentTeam'] = game_item['homeTeam'] if is_visitors else game_item['visitorsTeam']
            player_item['playerName'] = player.css('th a::text').get()
            player_item['plusMinus']: player.css('td[data-stat="plus_minus"] ::text').get() if 'plus_minus' in player.css('td[data-stat]::attr(data-stat)').get() else None

            player_item.update(self.extract_stats(player))

            self.collected_player_items.append(player_item)

    def extract_stats(self, element):
        # Extracts statistics into a dictionary based on BaseStatsItem fields.
        return {
            'minutesPlayed': element.css('td[data-stat="mp"] ::text').get(),
            'points': element.css('td[data-stat="pts"] ::text').get(),
            'fieldGoalsMade': element.css('td[data-stat="fg"] ::text').get(),
            'fieldGoalsAttempted': element.css('td[data-stat="fga"] ::text').get(),
            'threePointMade': element.css('td[data-stat="fg3"] ::text').get(),
            'threePointAttempted': element.css('td[data-stat="fg3a"] ::text').get(),
            'freeThrowsMade': element.css('td[data-stat="ft"] ::text').get(),
            'freeThrowsAttempted': element.css('td[data-stat="fta"] ::text').get(),
            'assists': element.css('td[data-stat="ast"] ::text').get(),
            'rebounds': element.css('td[data-stat="trb"] ::text').get(),
            'steals': element.css('td[data-stat="stl"] ::text').get(),
            'blocks': element.css('td[data-stat="blk"] ::text').get(),
            'turnovers': element.css('td[data-stat="tov"] ::text').get(),
            'personalFouls': element.css('td[data-stat="pf"] ::text').get(),
        }

    def closed(self, reason):
        # Handles saving of collected items when the spider is closed.
        if self.current_season:
            season_folder = os.path.join('scraped_data', f'Season_{self.current_season}')
            os.makedirs(season_folder, exist_ok=True)
            
            self.save_to_csv(self.collected_game_items, os.path.join(season_folder, 'games_data.csv'))
            self.save_to_csv(self.collected_team_items, os.path.join(season_folder, 'teams_data.csv'))
            self.save_to_csv(self.collected_player_items, os.path.join(season_folder, 'players_data.csv'))

    def save_to_csv(self, items, filename):
        # Converts a list of items to a DataFrame and saves it to a CSV file.
        if items:
            df = pd.DataFrame([dict(item) for item in items])
            df['gameDate'] = pd.to_datetime(df['gameDate'], format='%a, %b %d, %Y')
            df.to_csv(filename, index=False)
            self.log(f"{filename} file created successfully.")
