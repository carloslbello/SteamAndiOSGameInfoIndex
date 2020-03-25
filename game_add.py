import os

def convertBoolAnswer(boolAnswer):
    value = 'null'
    if boolAnswer == 'y':
        value = 'true'
    if boolAnswer == 'n':
        value = 'false'
    return value

def add_game():
    path = os.path.dirname(os.path.realpath(__file__))
    game_name = input('Name of game (including any "edition" updates): ')
    steam_link = input('Link to game on Steam store: ')
    steam_id = steam_link.split('/')[4]
    print(f'Steam ID: {steam_id}')
    appstore_link = input('Link to game on App Store: ')
    appstore_id = appstore_link.split('/')[6][2:]
    print(f'App Store ID: {appstore_id}')
    cloud = convertBoolAnswer(input('Cloud save on both platforms? (y/n/?) [?]: '))
    parity = convertBoolAnswer(input('Game parity on both platforms? (y/n/?) [?]: '))
    save_compatibility = 'false'
    if parity == 'false':
        print('Assuming save compatibility is no, since game parity is no')
    else:
        save_compatibility = convertBoolAnswer(input('Save compatibility between platforms? (y/n/?) [?]: '))
    notes = input('Notes: ')
    json_to_save = f'''{{
  "steam": {{
    "id": {steam_id}
  }},
  "ios": {{
    "id": {appstore_id}
  }},
  "cloud": {cloud},
  "game_parity": {parity},
  "save_compatibility": {save_compatibility}'''
    if notes:
        json_to_save += f',\n  "notes": "{notes}"'
    json_to_save += '\n}\n'
    print(json_to_save[:-1])
    with open(os.path.join(path, 'games', game_name + '.json'), 'w') as file:
        file.write(json_to_save)
    print(f'To add DLC information, edit the new file (games/{game_name}.json).')

while True:
    add_game()
    if input('Add another game? (y/n) [n]: ') != 'y':
        break
