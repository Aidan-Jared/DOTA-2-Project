import json
import torch
import pandas as pd
import numpy as np

if __name__ == "__main__":
    names = dict()
    with open('data/heroes.json') as f:
        data = json.load(f)
        for i in data:
            names[i["id"]] = i['localized_name']
    df_heroes = pd.DataFrame.from_dict(names, orient='index', columns=['name'])
    df = pd.read_csv("data/liquid_picks_bans.csv")
    
    df['is_pick'] = df['is_pick'].astype(int)
    grouped = df.groupby('match_id')
    df_updated = pd.DataFrame()
    for i in grouped:
        i[1]['p_hero_id'] = i[1]['hero_id'].shift(1)
        i[1].fillna(0, inplace = True)
        i[1]['p_hero_id'] = i[1]['p_hero_id'].astype(int)
        df_updated = df_updated.append(i[1], ignore_index = True)

    train_target = torch.tensor(df_updated['hero_id'].values)
    train = torch.tensor(df_updated.drop(['Unnamed: 0', 'hero_id', 'ord', 'team', 'match_id'], axis=1).values)
    train_tensor = torch.utils.data.TensorDataset(train, train_target)
    trainloader = torch.utils.data.DataLoader(
        train_tensor,
        batch_size=22,
        shuffle=True,
        num_workers=2
    )
    dataiter = iter(trainloader)
    # data, target = dataiter.next()