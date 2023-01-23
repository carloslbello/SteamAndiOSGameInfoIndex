import os
import json
from datetime import datetime
import aiohttp
import feedparser
import asyncio

path = os.path.dirname(os.path.realpath(__file__))

def get_games_dict():
    path = os.path.dirname(os.path.realpath(__file__))
    games_json = {}
    for entry in os.scandir(os.path.join(path, 'games')):
        if entry.name.endswith('.json') and entry.is_file():
            games_json[entry.name[:-5]] = json.load(open(entry.path))
    return games_json
    
async def get_ios_update_times(session, app_ids):
    url = 'https://itunes.apple.com/lookup?id=' + ','.join(map(str, app_ids))
    result = {}
    resp = await session.get(url)
    objs = (await resp.json())['results']
    for obj in objs:
        result[obj['trackId']] = datetime.fromisoformat(obj['currentVersionReleaseDate'])
    return result
    

async def update_times():
    games_dict = get_games_dict()
    ios_app_ids = []
    ios_old_update_times = {}
    steam_app_ids = []
    for game in games_dict:
        game_obj = games_dict[game]
        ios_games = []
        if type(game_obj['ios']) is dict:
            ios_games.append(game_obj['ios'])
        else:
            ios_games = game_obj['ios']
        for ios_game in ios_games:
            ios_app_ids.append(ios_game['id'])
            ios_old_update_times[ios_game['id']] = None if 'last_updated' not in ios_game else ios_game['last_updated']
            if ' ' in ios_old_update_times[ios_game['id']]:
                ios_old_update_times[ios_game['id']] = ios_old_update_times[ios_game['id']][:ios_old_update_times[ios_game['id']].index(' ')]
    ios_update_times = await get_ios_update_times(ios_app_ids)
    for game in games_dict:
        game_obj = games_dict[game]
        if type(game_obj['ios']) is dict:
            if game_obj['ios']['id'] in ios_update_times:
                game_obj['ios']['last_updated'] = ios_update_times[game_obj['ios']['id']].strftime('%m/%d/%y')
            else:
                game_obj['ios']['last_updated'] = (ios_old_update_times[game_obj['ios']['id']] or 'Unknown') + ' (delisted)'
        else:
            for ios_game in game_obj['ios']:
                if ios_game['id'] in ios_update_times:
                    ios_game['last_updated'] = ios_update_times[ios_game['id']].strftime(
                        '%m/%d/%y')
                else:
                    ios_game['last_updated'] = (
                        ios_old_update_times[ios_game['id']] or 'Unknown') + ' (delisted)'
                ios_game['last_updated'] = ios_update_times[ios_game['id']].strftime('%m/%d/%y')
        json.dump(game_obj, open(os.path.join(path, 'games', game + '.json'), 'w'), indent=2)        

asyncio.run(update_times())

