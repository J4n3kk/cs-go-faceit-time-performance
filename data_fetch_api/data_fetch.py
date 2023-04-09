import requests
import json
import time
import datetime
from .config import api_key as api 

class Data_fetcher:
    
    def __init__(self, api, nickname):
        
        self.get_game_id = 'csgo'
        self.get_api = api
        self.get_nickname = nickname
        self.get_player_id = None
        self.get_avatar_url = None
        self.get_friends = None
        self.get_faceit_elo = None
        self.get_faceit_url = None
        self.get_avg_kd = None
        self.get_win_ratio = None
        self.get_matches_number = None
        self.get_registration_date = None
        self.get_registration_date_unix = None
        self.match_list = []
        print('Instance init, data fetching started')
        self.request_player_details()
        self.request_player_statistics()
        self.request_player_reg_date()
        self.utc_to_unix()
        print('Fetching game history')
        self.request_match_history()
        self.test_data_integrity()
  
    def request_player_details(self):  

        headers = {
          'accept': 'application/json',
          'Authorization': f'Bearer {self.get_api}',
        }
        params = {
          'nickname': f'{self.get_nickname}',
        }
    
        response = requests.get('https://open.faceit.com/data/v4/players', params=params, headers=headers)
        response = json.loads(response.content)
        
        self.get_player_id = response['player_id']
        self.get_avatar_url = response['avatar']
        self.get_friends = response['friends_ids']
        self.get_faceit_elo = response['games']['csgo']['faceit_elo']
        self.get_faceit_url = response['faceit_url']
        return response
    
    def request_player_statistics(self):

        headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {self.get_api}',
        }

        response = requests.get(
            f'https://open.faceit.com/data/v4/players/{self.get_player_id}/stats/csgo',
            headers=headers,
        )
        response = json.loads(response.content)

        self.get_avg_kd = response['lifetime']["Average K/D Ratio"]
        self.get_win_ratio = response['lifetime']['Win Rate %']
        self.get_matches_number = response['lifetime']['Matches']
        return response
    
    def request_player_reg_date(self):

        headers = {
            'accept': 'application/json',
        }
        response = requests.get(f'https://api.faceit.com/users/v1/nicknames/{self.get_nickname}', headers=headers)    
        response = json.loads(response.content)

        self.get_registration_date = response['payload']['created_at'][:10].split('-')

    def utc_to_unix(self):
        date_time = datetime.datetime(int(self.get_registration_date[0]), int(self.get_registration_date[1]), int(self.get_registration_date[2]))
        self.get_registration_date_unix = round(time.mktime(date_time.timetuple()))

    def request_match_history(self, timeframe=None):
        # request data from the appi, baseline time period starts from account time registration
        # then after each request, it changes the from header to be based on the last match that is stored in the list
        if (timeframe==None):
            timeframe=round((time.time()//1))
            self.match_list = []
            print(f'time initialized: {timeframe}')
        if (len(self.match_list) >= int(self.get_matches_number)):
            print('Recursion end activated')
            print(f'Lenght of match list: {len(self.match_list)}')
            return
        # print(f'Normal run with timeframe start at: {timeframe}')
        # print(f'Lenght of match list: {len(self.match_list)}')
        
        headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {self.get_api}',
        }

        params = {
            'game': 'csgo',
            'from': f'{self.get_registration_date_unix}',
            'to': f'{timeframe}',
            'offset': '0',
            'limit': '100',
        }

        response = requests.get(
            f'https://open.faceit.com/data/v4/players/{self.get_player_id}/history',
            params=params,
            headers=headers,
        )
        content = json.loads(response.content)['items']
        
        timeframe = content[-1]['started_at']
        # print(f'Update timeframe for recursive call is {timeframe}')
        self.match_list = self.match_list + content
        #time.sleep(MS / )
        self.request_match_history(timeframe)
        
    def test_data_integrity(self):
        test_list = list(map(lambda x : x['match_id'], self.match_list))
        if (len(test_list) == len(set(test_list))):
            print('Data test integrity passed \n Match list does not contain any duplicated match ids')
            return
        print('Test integrity has failed, \n duplicates have been found')
                        