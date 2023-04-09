# modifies data from faceit api to reusable form to analysys 
import sys
sys.path.append("..")
from data_fetch_api.main import Data_fetcher as df 
from data_fetch_api.config import api_key as api 

def derive_data(match_list, player_id):
    
    return list(map(lambda x : data_extractor(x, player_id), match_list))

def data_extractor(x, player_id):
    match_id = x['match_id']
    game_mode = x['game_mode']
    max_players = x['max_players']
    started_at = x['started_at']
    finished_at = x['finished_at']
    winner_team = x['results']['winner'] # faction1 or faction2
    faction1 = list(map(lambda x: x['player_id'],x['teams']['faction1']['players']))
    faction2 = list(map(lambda x: x['player_id'],x['teams']['faction2']['players']))
    player_team = 'faction1' if player_id in faction1 else 'faction2'
    result = 1 if player_team == winner_team else 0

    return [match_id, game_mode, max_players, started_at, finished_at, result]

