# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class ZavrsniPokusaj5Item(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    pass

class GameItem(scrapy.Item):
  gameDate = scrapy.Field()
  visitorsTeam = scrapy.Field()
  visitorsTeamPoints = scrapy.Field()
  homeTeam = scrapy.Field()
  homeTeamPoints = scrapy.Field()

class BaseStatsItem(scrapy.Item):
  minutesPlayed = scrapy.Field() 
  points = scrapy.Field() 
  fieldGoalsMade = scrapy.Field() 
  fieldGoalsAttempted = scrapy.Field()
  threePointMade = scrapy.Field()
  threePointAttempted = scrapy.Field()
  freeThrowsMade = scrapy.Field()
  freeThrowsAttempted = scrapy.Field()
  assists = scrapy.Field()
  rebounds = scrapy.Field()
  steals = scrapy.Field()
  blocks = scrapy.Field()
  turnovers = scrapy.Field()
  personalFouls = scrapy.Field()

class TeamItem(BaseStatsItem):
  gameDate = scrapy.Field()
  team = scrapy.Field()
  opponentTeam = scrapy.Field()

class PlayerItem(BaseStatsItem):
    gameDate = scrapy.Field() 
    playerName = scrapy.Field()
    team = scrapy.Field() 
    opponentTeam = scrapy.Field()
    plusMinus = scrapy.Field()
