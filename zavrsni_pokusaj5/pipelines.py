# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class ZavrsniPokusaj5Pipeline:
    def process_item(self, item, spider):
        return item


'''import mysql.connector

class SaveToMySQLPipeline:
  def __init__(self):
      self.conn = mysql.connector.connect(
          host = 'localhost',
          user = 'root',
          password = 'Zavrsn1_rad',
          database = 'nba',
          port = 3306
      )

      ## Create cursor, used to execute commands
      self.cur = self.conn.cursor()
      
      ## Create books table if none exists
      self.cur.execute("""
      CREATE TABLE IF NOT EXISTS nbaTeams(
          id int NOT NULL auto_increment, 
          name text,
          PRIMARY KEY (id)
      )
      """)

  def process_item(self, item, spider):
      self.cur.execute(""" insert into nbaTeams (
        name,
        ) values (
          %s
        )""", (
          item["name"],
        ))
      self.conn.commit()
  
  def close_spider(self, spider):

        ## Close cursor & connection to database 
        self.cur.close()
        self.conn.close()

import mysql.connector
from mysql.connector import errorcode

try:
    connection = mysql.connector.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='Zavrsn1_rad',
        database='nba'
    )

    if connection.is_connected():
        print("Successfully connected to the database")

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Invalid username or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(f"Error: {err}")
finally:
    if connection.is_connected():
        connection.close()
        print("MySQL connection is closed")'''







