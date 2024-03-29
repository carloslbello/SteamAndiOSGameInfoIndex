import os
import json
from datetime import date

def slashed_date_string_to_date(string):
    split_date_string = split_last_updated = list(
        map(int, string.split('/')))
    return date(2000 + split_date_string[2], split_date_string[0], split_date_string[1])


def get_games():
    path = os.path.dirname(os.path.realpath(__file__))
    games_json = {}
    for entry in os.scandir(os.path.join(path, 'games')):
        if entry.name.endswith('.json') and entry.is_file():
            games_json[entry.name[:-5]] = json.load(open(entry.path))
    games = {}
    for game in games_json:
        game_obj = {}
        game_obj['steam'] = {
            'id': games_json[game]['steam']['id'],
            'link': f'https://store.steampowered.com/app/{games_json[game]["steam"]["id"]}'
        }
        game_obj['steam']['dlc'] = {}
        game_obj['steam']['dlc_included'] = []
        steam_dlc_names = set()
        if 'dlc' in games_json[game]['steam']:
            for dlc in games_json[game]['steam']['dlc']:
                steam_dlc_names.add(dlc)
                game_obj['steam']['dlc'][dlc] = {
                    'id': games_json[game]['steam']['dlc'][dlc],
                    'link': f'https://store.steampowered.com/app/{games_json[game]["steam"]["dlc"][dlc]}'
                }
        if 'dlc_included' in games_json[game]['steam']:
            game_obj['steam']['dlc_included'] = games_json[game]['steam']['dlc_included']            
            for dlc in games_json[game]['steam']['dlc_included']:
                steam_dlc_names.add(dlc)
        game_obj['ios'] = []
        ios_games = []
        ios_dlc_sets = []
        most_recent_update = date(1970, 1, 1)
        if type(games_json[game]['ios']) is dict:
            ios_games.append(games_json[game]['ios'])
        else:
            ios_games = games_json[game]['ios']
        for ios_game in ios_games:
            ios_game_obj = {
                'id': ios_game['id'],
                'link': f'https://apps.apple.com/us/app/id{ios_game["id"]}',
                'dlc_available': [] if 'dlc_available' not in ios_game else ios_game['dlc_available'],
                'dlc_included': [] if 'dlc_included' not in ios_game else ios_game['dlc_included'],
                'last_updated': ios_game['last_updated']
            }
            if '/' in ios_game['last_updated']:
                last_updated_date = slashed_date_string_to_date(
                    ios_game['last_updated'])
                if most_recent_update < last_updated_date:
                    most_recent_update = last_updated_date
            game_obj['ios'].append(ios_game_obj)
            ios_dlc_sets.append(set(ios_game_obj['dlc_available']).union(ios_game_obj['dlc_included']))
        calculated_dlc_parity = False
        for ios_dlc_set in ios_dlc_sets:
            if ios_dlc_set == steam_dlc_names:
                calculated_dlc_parity = True
                break
        game_obj['cloud'] = games_json[game]['cloud']
        game_obj['game_parity'] = games_json[game]['game_parity']
        game_obj['dlc_parity'] = calculated_dlc_parity if 'dlc_parity' not in games_json[game] else games_json[game]['dlc_parity']
        game_obj['save_compatibility'] = games_json[game]['save_compatibility']
        game_obj['notes'] = ('' if 'notes' not in games_json[game] else games_json[game]['notes'] + '<br>') + ('\u26a0 ' if slashed_date_string_to_date(games_json[game]['last_updated']) < most_recent_update else '') + f'_Last updated: {games_json[game]["last_updated"]}_'
        games[game] = game_obj
    return games

def write_md(filename, games, compat_columns=True):
    checkmark_key = {
        True: '\u2713',
        False: '\u2717',
        None: '?'
    }
    with open(filename, 'w') as mdfile:
        if compat_columns:
            mdfile.write('Game|Steam|iOS|Cloud Save|Game Parity|DLC Parity|Save Compatibility|Notes\n')
            mdfile.write('-|-|-|-|-|-|-|-\n')
        else:
            mdfile.write('Game|Steam|iOS|Notes\n')
            mdfile.write('-|-|-|-\n')
        for game in sorted(list(games.keys())):
            game_obj = games[game]
            game_row = f'{game}|[{game}'
            if game_obj['steam']['dlc_included'] != []:
                for dlc in game_obj['steam']['dlc_included']:
                    game_row += f' + {dlc}'
                game_row += ' DLC' + ('s' if len(game_obj['steam']['dlc_included']) > 1 else '')
            game_row += f']({game_obj["steam"]["link"]})'
            for dlc in game_obj['steam']['dlc']:
                game_row += f', [{dlc} DLC]({game_obj["steam"]["dlc"][dlc]["link"]})'
            game_row += '|'
            ios_cell = ''
            for ios_game in game_obj['ios']:
                if ios_cell != '':
                    ios_cell += ', '
                ios_cell += '[' + game
                if ios_game['dlc_included'] != []:
                    for dlc in ios_game['dlc_included']:
                        ios_cell += f' + {dlc}'
                    ios_cell += ' DLC' + ('s' if len(ios_game['dlc_included']) > 1 else '')
                ios_cell += f']({ios_game["link"]})'
                if ios_game['dlc_available'] != []:
                    ios_cell += ' _('
                    previous_dlc = False
                    for dlc in ios_game['dlc_available']:
                        if previous_dlc:
                            ios_cell += ', '
                        ios_cell += dlc
                        previous_dlc = True
                    ios_cell += ' DLC' + ('s' if len(ios_game['dlc_available']) > 1 else '') + ' available as IAP)_'
                ios_cell += ' (last updated: ' + ios_game['last_updated'] + ')'
            game_row += ios_cell
            if compat_columns:
                game_row += '|' + checkmark_key[game_obj['cloud']]
                game_row += '|' + checkmark_key[game_obj['game_parity']]
                game_row += '|' + checkmark_key[game_obj['dlc_parity']]
                game_row += '|' + checkmark_key[game_obj['save_compatibility']]
            game_row += '|' + game_obj['notes'] + '\n'
            mdfile.write(game_row)

def write_files():
    games = get_games()
    write_md('Games.md', games)
    write_md('Compatible Games.md', {k: v for k, v in games.items() if v['cloud'] and v['game_parity'] and v['dlc_parity'] and v['save_compatibility']}, False)

if __name__ == '__main__':
    write_files()