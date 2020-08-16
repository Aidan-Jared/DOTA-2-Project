import json
import time
import requests
import pandas as pd

def pull_picks_bans(matches, number = 100):
    if type(matches) != list:
        matches = [matches]
    i = 0
    df = pd.DataFrame()
    for m in matches:
        if i == number:
            # limmit number of matches read in
            break
        # get match data from api
        print('requseting match {}'.format(m["match_id"]))
        r = requests.get('https://api.opendota.com/api/matches/{}'.format(m['match_id']))
        match = r.json()
        picks_bans = match['picks_bans']
        dire_team = match['dire_team']
        radiant_team = match['radiant_team']
        df = df.append(picks_bans, ignore_index = True)
        df = df.replace({"team" : {0:radiant_team['name'], 1:dire_team['name']}})
        print('processed {} matches'.format(i + 1))

        # prevent request errors
        time.sleep(5)
        i += 1
    return df

if __name__ == "__main__":
    # read in all matches from json
    input_file = open("data/liquid_matches.json")
    matches = json.load(input_file)
    input_file.close()
    print('Loading {} matches\n'.format(len(matches)))
    df = pull_picks_bans(matches)

    # save match data to local machine

    df.to_csv("data/liquid_picks_bans.csv")