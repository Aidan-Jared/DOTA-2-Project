import json
import numpy as np
import pandas as pd

if __name__ == "__main__":
    df = pd.DataFrame.from_csv("data/liquid_picks_bans.csv")
    
    names = dict()
    with open('data/heroes.json') as f:
        data = json.load(f)
        for i in data:
            names[i["id"]] = i['localized_name']

    