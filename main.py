import discord
import os
import requests
import json
from datetime import datetime, timedelta
 
client = discord.Client()

# dev - does not make api calls
# prod - makes api calls
mode = "dev"

#Valid League list
leagues = ["NFL", "NBA", "NHL","MLB", "NCAAF", "NCAAB"]

#Game window set for 2 weeks
game_window = 14

#Gets games for league value
def get_league(value):
  for x in leagues:
    league_index = value.upper().find(x)
    if(league_index != -1):
      return value[league_index:]

# Create new game object
def new_game(game_data):
  game = {}
  #Add summary
  game['summary'] = game_data['summary']
  #Add status
  game['status'] = game_data['status']
  #Add game id
  game['gameId'] = game_data['gameId']

  return game
  
#Changes date to yyyy/mm/dd only and validate that it falls in the correct window
def valid_date(game_date_time):
  month = game_date_time.strftime("%m")
  year = game_date_time.strftime("%Y")
  day = game_date_time.strftime("%d")
  str_date = year + "-" +month+"-"+day
  game_date = datetime.strptime(str_date,'%Y-%m-%d')

  future_day_thresh = datetime.today() + timedelta(days=14)
  yesterday = datetime.today() - timedelta(days=1)

  return ((future_day_thresh.date() > game_date.date()) and (game_date.date() > yesterday.date()))

# This only returns games for the 2 weeks including today
def filter_by_date(obj):
  input_dict = obj
  output_list = []

  for key in input_dict:
    #Extract date for comparison
    game_date_time = datetime.strptime(key['schedule']['date'],'%Y-%m-%dT%H: %M: %S.%f%z')
    
  #Add games within the next 14 days to the output list
    if valid_date(game_date_time):
      print('Game Matched!')
      if not key['status'] == 'canceled':
        output_list.append(new_game(key))

  return output_list

# This returns games for specified league
def filter_by_league(obj,league):
  # Transform json input to python objects
  input_dict = obj['results']

  # Filter python objects with list comprehensions for league
  league_dict = [x for x in input_dict if x['details']['league'] == league.upper()]

  # Filter for upcoming games
  output_dict = filter_by_date(league_dict)

  # Transform python object back into json
  return json.dumps(output_dict)      


def get_games(league):
  print("getting games")
  url = "https://sportspage-feeds.p.rapidapi.com/games"

  headers = {
      'x-rapidapi-host': "sportspage-feeds.p.rapidapi.com",
      'x-rapidapi-key': os.getenv('x-rapidapi-key')
      }
  if(mode == 'dev'):
    # Get data from file
    f = open('results.json')
    results = json.load(f)

    f.close()
  else:
    # Get data from api
    response = requests.request("GET", url, headers=headers)
  
    json_data = json.loads(response.text)

    if(json_data['status'] == 200):
      print("Request was successful")

  return filter_by_league(results,league)

  # else:
      # print("Request failed with status: " + json_data.status)

# Build formatted game list string
def str_game_list(games):
  game_str = "**Choose a game by it's number (EX: $game 1)**"
  index = 1
  #Add each game lead by index+1
  for games in games:
    game_str += "\n" + str(index) + ": " + games["summary"]

  return game_str


@client.event
async def on_ready():
  print("we have logged in as {0.user}'.format(client)"
  +"\n"
  +"Mode: " + mode)

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if message.content.startswith('$game'):
    index = message.content
    await message.channel.send("Ok, lets do " + index)

  if message.content.startswith('$games'):
    league = get_league(message.content)
      
    games = json.loads(get_games(league))

    # Check for empty Games object
    if(not bool(games)):
      print("No games match")
      await message.channel.send("Sorry, no upcoming games match your input. Make sure to mention the League! Valid options are `" + str(leagues) + "`."
      + "\n" + "\n"
      + "Only games occuring in the next 2 weeks are able to be bet upon.")
    else:
      #Report number of games found
      await message.channel.send("Game(s) available to bet on:\n`" + str(len(games)) + "`")
      
      # Select a game
      await message.channel.send(str_game_list(games))

client.run(os.getenv('TOKEN'))