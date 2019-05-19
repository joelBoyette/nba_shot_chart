import pandas as pd
import json
import requests
import time
import pymongo


# Initialize PyMongo to work with MongoDBs
conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)

#creates db (nba_shots) and collection (shot_data) to hold data
db = client.nba_shots
collection = db.shot_data


#Documentation for connecting to NBA.com API
#https://github.com/swar/nba_api/tree/master/docs/nba_api/stats/endpoints
#https://github.com/seemethere/nba_py/wiki/stats.nba.com-Endpoint-Documentation

#create url for json request
#Player Game Data for Kemba Walker for 2018-19 season
base_url = 'https://stats.nba.com/stats/'
endpoint = 'playergamelog/?'
chart_params = { "DateFrom":'',
                "DateTo":'',
                "LeagueID":'00',
                "PlayerID":'202689',
                "Season":'2018-19',
                "SeasonType":'Regular Season'
                }
user_agent = {'User-agent': 
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}
full_url = base_url + endpoint


#Return json data from api to pandas dataframe
#https://stackoverflow.com/questions/17782142/why-doesnt-requests-get-return-what-is-the-default-timeout-that-requests-get
response = requests.get(full_url,headers=user_agent,params=chart_params,timeout=5)
games_played = response.json()
games_played_headers = games_played['resultSets'][0]['headers']
games_played = games_played['resultSets'][0]['rowSet']
games_played_df = pd.DataFrame(columns=games_played_headers)

for i,data in enumerate(games_played):
    games_played_df.loc[i,'SEASON_ID'] = data[0]
    games_played_df.loc[i,'Player_ID'] = data[1]
    games_played_df.loc[i,'Game_ID'] = data[2]
    games_played_df.loc[i,'GAME_DATE'] = data[3]
    games_played_df.loc[i,'MATCHUP'] = data[4]
    
games_played_df = games_played_df[['SEASON_ID','Player_ID','Game_ID','GAME_DATE','MATCHUP']]
games_played_df['GAME_DATE'] = pd.to_datetime(games_played_df['GAME_DATE'], format='%b %d, %Y').dt.strftime('%m/%d/%Y')
games_played_df['opponent_id'] = ''


#Use Player Game Data to get opponent_id (required for shot chart endpoint)
endpoint = 'scoreboard/?'
full_url = base_url + endpoint
for i,row in games_played_df.iterrows():
    game_date = games_played_df.loc[i,'GAME_DATE']
    game_id = games_played_df.loc[i,'Game_ID']
    chart_params ={'GameDate':game_date,
                  'LeagueID':'00',
                  'DayOffset':'0'}
    response = requests.get(full_url,headers=user_agent,params=chart_params,timeout=5)
    data = response.json()
    
    if data['resultSets'][0]['rowSet'][0][2]== game_id:
        games_played_df.loc[i,'opponent_id'] = data['resultSets'][0]['rowSet'][0][7]


#now get shot detail for each game
base_url = 'https://stats.nba.com/stats/'
endpoint = 'shotchartdetail/?'
user_agent = {'User-agent': 
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
             }
full_url = base_url + endpoint
shot_headers = ['GRID_TYPE', 'GAME_ID', 'GAME_EVENT_ID', 'PLAYER_ID', 'PLAYER_NAME',
       'TEAM_ID', 'TEAM_NAME', 'PERIOD', 'MINUTES_REMAINING',
       'SECONDS_REMAINING', 'EVENT_TYPE', 'ACTION_TYPE', 'SHOT_TYPE',
       'SHOT_ZONE_BASIC', 'SHOT_ZONE_AREA', 'SHOT_ZONE_RANGE', 'SHOT_DISTANCE',
       'LOC_X', 'LOC_Y', 'SHOT_ATTEMPTED_FLAG', 'SHOT_MADE_FLAG', 'GAME_DATE',
       'HTM', 'VTM']
shot_df = pd.DataFrame(columns=shot_headers)
all_shot_df = shot_df
count=1

for i,row in games_played_df.iterrows():
    game = games_played_df.loc[i,'Game_ID']
    opponent = games_played_df.loc[i,'opponent_id']
    time.sleep(2)
    chart_params = {'Period':'0',
             'VsConference':'',
            'LeagueID':'00',
              'LastNGames':'0',
              'TeamID':'1610612766',
             'Position':'Guard',
             'Location':'',
             'Outcome':'',
             'ContextMeasure':'FGA',
              'DateFrom':'',
              'StartPeriod':'',
              'DateTo':'',
              'OpponentTeamID':opponent,
              'ContextFilter':'',
              'RangeType':'',
              'Season':'2018-19',
              'AheadBehind':'',
              'PlayerID':'202689',
              'EndRange':'',
              'VsDivision':'',
              'PointDiff':'',
              'RookieYear':'',
              'GameSegment':'',
              'Month':'0',
              'ClutchTime':'',
              'StartRange':'',
              'EndPeriod':'',
              'SeasonType':'Regular Season',
              'SeasonSegment':'',
              'GameID':game,
              'PlayerPosition':'',
             }
    response = requests.get(full_url,headers=user_agent,params=chart_params,timeout=5)
    try:
        shot_data = response.json()
        shot_data = shot_data['resultSets'][0]['rowSet']

        for i,data in enumerate(shot_data):
            shot_df.loc[i,'GRID_TYPE'] = data[0]
            shot_df.loc[i,'GAME_ID'] = data[1]
            shot_df.loc[i,'GAME_EVENT_ID'] = data[2]
            shot_df.loc[i,'PLAYER_ID'] = data[3]
            shot_df.loc[i,'PLAYER_NAME'] = data[4]
            shot_df.loc[i,'TEAM_ID'] = data[5]
            shot_df.loc[i,'TEAM_NAME'] = data[6]
            shot_df.loc[i,'PERIOD'] = data[7]
            shot_df.loc[i,'MINUTES_REMAINING'] = data[8]
            shot_df.loc[i,'SECONDS_REMAINING'] = data[9]
            shot_df.loc[i,'EVENT_TYPE'] = data[10]
            shot_df.loc[i,'ACTION_TYPE'] = data[11]
            shot_df.loc[i,'SHOT_TYPE'] = data[12]
            shot_df.loc[i,'SHOT_ZONE_BASIC'] = data[13]
            shot_df.loc[i,'SHOT_ZONE_AREA'] = data[14]
            shot_df.loc[i,'SHOT_ZONE_RANGE'] = data[15]
            shot_df.loc[i,'SHOT_DISTANCE'] = data[16]
            shot_df.loc[i,'LOC_X'] = data[17]
            shot_df.loc[i,'LOC_Y'] = data[18]
            shot_df.loc[i,'SHOT_ATTEMPTED_FLAG'] = data[19]
            shot_df.loc[i,'SHOT_MADE_FLAG'] = data[20]
            shot_df.loc[i,'GAME_DATE'] = data[21]
            shot_df.loc[i,'HTM'] = data[22]
            shot_df.loc[i,'VTM'] = data[23]

        all_shot_df = all_shot_df.append(shot_df,ignore_index=True)
        
    except:
        pass
        

# #seperate made and misses into seperate dfs for charting
# made_df = all_shot_df.loc[all_shot_df['SHOT_MADE_FLAG']==1]
# made_df['LOC_X'] = pd.to_numeric(made_df['LOC_X'])
# made_df['LOC_Y'] = pd.to_numeric(made_df['LOC_Y'])

# miss_df = all_shot_df.loc[all_shot_df['SHOT_MADE_FLAG']==0]
# miss_df['LOC_X'] = pd.to_numeric(miss_df['LOC_X'])
# miss_df['LOC_Y'] = pd.to_numeric(miss_df['LOC_Y'])

# made_chart_x = list(made_df['LOC_X'])
# made_chart_y = list(made_df['LOC_Y'])
# miss_chart_x = list(miss_df['LOC_X'])
# miss_chart_y = list(miss_df['LOC_Y'])


#turn df into a dictionary for processing into mongo
all_shot_dict = all_shot_df.to_dict('list')

#  Insert climae anamolies into mongo database
collection.insert_one(all_shot_dict)