import json
import time
import requests
import pandas as pd

def winner(matches, number = 100):
    if type(matches) != list:
        matches = [matches]
    i = 0
    df = pd.DataFrame()
    for m in matches:
        if i == number:
            # limmit number of matches read in
            break
        print('requseting match {}'.format(m["match_id"]))
        r = requests.get('https://api.opendota.com/api/matches/{}'.format(m['match_id']))
        match = r.json()
        radiant_win = match['radiant_win']
        dire_team = match['dire_team']
        radiant_team = match['radiant_team']
        if radiant_win == True:
            win = {"winner" : radiant_team['name'], "match_id" : str(match['match_id'])}
        elif radiant_win == False:
            win = {"winner" : dire_team['name'], "match_id" : str(match['match_id'])}
        df = df.append(win, ignore_index = True)
        print('processed {} matches'.format(i + 1))
        time.sleep(5)
        i += 1
    return df

if __name__ == "__main__":
    input_file = open("data/liquid_matches.json")
    matches = json.load(input_file)
    input_file.close()
    print('Loading {} matches\n'.format(len(matches)))
    df_win = winner(matches)
    df_win.to_csv("data/liquid_wins.csv")