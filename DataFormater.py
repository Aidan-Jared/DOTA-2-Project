import json
import time
import requests

if __name__ == "__main__":
    input_file = open("data/liquid_matches.json")
    matches = json.load(input_file)
    input_file.close()
    print('Loading {} matches\n'.format(len(matches)))

    with open('data/liquid_match_data.txt', 'w', encoding="utf-8") as f:
        i = 0
        for m in matches:
            if i == 100:
                break
            print('requseting match {}'.format(m["match_id"]))
            r = requests.get('https://api.opendota.com/api/matches/{}'.format(m['match_id']))
            f.write(r.text)
            f.write('\n')
            print(r.text)
            time.sleep(5)
            i += 1

        print('processed {} matches'.format(i))
    f.close()