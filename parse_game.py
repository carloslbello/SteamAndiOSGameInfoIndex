import os
import json

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
        steam_dlc_names = set()
        if 'dlc' in games_json[game]['steam']:
            for dlc in games_json[game]['steam']['dlc']:
                steam_dlc_names.add(dlc)
                game_obj['steam']['dlc'][dlc] = {
                    'id': games_json[game]['steam']['dlc'][dlc],
                    'link': f'https://store.steampowered.com/app/{games_json[game]["steam"]["dlc"][dlc]}'
                }
        game_obj['ios'] = []
        ios_games = []
        ios_dlc_sets = []
        if type(games_json[game]['ios']) is dict:
            ios_games.append(games_json[game]['ios'])
        else:
            ios_games = games_json[game]['ios']
        for ios_game in ios_games:
            ios_game_obj = {
                'id': ios_game['id'],
                'link': f'https://apps.apple.com/us/app/id{ios_game["id"]}',
                'dlc_available': [] if 'dlc_available' not in ios_game else ios_game['dlc_available'],
                'dlc_included': [] if 'dlc_included' not in ios_game else ios_game['dlc_included']
            }
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
        game_obj['notes'] = '' if 'notes' not in games_json[game] else games_json[game]['notes']
        games[game] = game_obj
    return games

# print(get_games())

def write_md(filename, games):
    checkmark_key = {
        True: '\u2713',
        False: '\u2717',
        None: '?'
    }
    with open(filename, 'w') as mdfile:
        mdfile.write('Game|Steam|iOS|Cloud Save|Game Parity|DLC Parity|Save Compatibility|Notes\n')
        mdfile.write('-|-|-|-|-|-|-|-\n')
        for game in sorted(list(games.keys())):
            game_obj = games[game]
            game_row = f'{game}|'
            game_row += f'[{game}]({game_obj["steam"]["link"]})'
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
                        ios_cell += f' + {dlc} '
                    ios_cell += 'DLC' + ('s' if len(ios_game['dlc_included']) > 1 else '')
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
            game_row += ios_cell
            game_row += '|' + checkmark_key[game_obj['cloud']]
            game_row += '|' + checkmark_key[game_obj['game_parity']]
            game_row += '|' + checkmark_key[game_obj['dlc_parity']]
            game_row += '|' + checkmark_key[game_obj['save_compatibility']]
            game_row += '|' + game_obj['notes'] + '\n'
            mdfile.write(game_row)

games = get_games()
write_md('Games.md', games)
write_md('Compatible Games.md', {k: v for k, v in games.items() if v['cloud'] and v['game_parity'] and v['dlc_parity'] and v['save_compatibility']})
