import json
import time
import requests
import pandas as pd

if __name__ == "__main__":
    # read in all matches from json
    input_file = open("data/liquid_matches.json")
    matches = json.load(input_file)
    input_file.close()
    print('Loading {} matches\n'.format(len(matches)))

    # save match data to local machine
    i = 0
    df = pd.DataFrame()
    for m in matches:
        if i == 100:
            # limmit number of matches read in
            break
        # get match data from api
        print('requseting match {}'.format(m["match_id"]))
        r = requests.get('https://api.opendota.com/api/matches/{}'.format(m['match_id']))
        match = r.json()
        picks_bans = match['picks_bans']
        df = df.append(picks_bans, ignore_index = True)

        # prevent request errors
        time.sleep(5)
        i += 1
    print('processed {} matches'.format(i))