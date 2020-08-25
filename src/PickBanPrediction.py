import json
import time
import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import numpy as np
from RNNmodel import RNN

if __name__ == "__main__":
    names = dict()
    with open('data/heroes.json') as f:
        data = json.load(f)
        for i in data:
            names[i["id"]] = i['localized_name'] # need to fix since length != highest key
    # df_heroes = pd.DataFrame.from_dict(names, orient='index', columns=['name'])
    df = pd.read_csv("data/liquid_picks_bans.csv")
    
    df['is_pick'] = df['is_pick'].astype(int)
    grouped = df.groupby('match_id')
    df_updated = pd.DataFrame()
    for i in grouped:
        i[1]['p_hero_id'] = i[1]['hero_id'].shift(1)
        i[1].fillna(0, inplace = True)
        i[1]['p_hero_id'] = i[1]['p_hero_id'].astype(int)
        df_updated = df_updated.append(i[1], ignore_index = True)

    train_target = torch.tensor(df_updated['hero_id'].values) - 1 # minus 1 is to move targets to 0 indexed start
    train = torch.tensor(df_updated.drop(['Unnamed: 0', 'hero_id', 'ord', 'team', 'match_id'], axis=1).values)
    train_tensor = torch.utils.data.TensorDataset(train, train_target)
    trainloader = torch.utils.data.DataLoader(
        train_tensor,
        batch_size=22,
        shuffle=False,
        num_workers=2
    )
    
    input_size = train.size()[1]
    hidden_size = 55
    output_size = max(names.keys()) # temp solution
    model = RNN(input_size, hidden_size, output_size)
    
    
    criterion = nn.NLLLoss()
    learning_rate = .005
    optimizer = optim.SGD(model.parameters(), lr = learning_rate, momentum=.9)
    epochs = 2
    print_every = 1

    for epoch in range(epochs):
        running_loss = 0
        for i, data in enumerate(trainloader,0):
            hidden = model.initHidden()
            optimizer.zero_grad()
            inputs, targets = data
            # remove for loop
            for j in range(inputs.size()[0]):
                output, hidden = model(inputs[j], hidden)
                loss = criterion(output, targets[j].unsqueeze(0))
                loss.backward()
                optimizer.step()

                running_loss += loss.item()
            if i % print_every == 0:
                print(i, loss)
