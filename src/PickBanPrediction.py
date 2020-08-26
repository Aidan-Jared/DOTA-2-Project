import json
import time
import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import numpy as np
from RNNmodel import RNN

def heroes_import(path):
    names_api = dict()
    names_model = dict()
    names_2_index = dict()
    with open(path) as f:
        data = json.load(f)
        for index, i in enumerate(data):
            names_api[i["id"]] = i['localized_name']
            names_model[index] = i['localized_name']
            names_2_index[i['localized_name']] = index
    return names_api, names_model, names_2_index

def data_prep(path):
    df = pd.read_csv(path)

    df['is_pick'] = df['is_pick'].astype(int)
    df.replace({'hero_id' : names_api}, inplace = True)
    df.replace({'hero_id' : names_2_index}, inplace = True)
    grouped = df.groupby('match_id')
    df_updated = pd.DataFrame()
    for i in grouped:

        i[1]['p_hero_id'] = i[1]['hero_id'].shift(1)
        i[1].fillna(0, inplace = True)
        i[1]['p_hero_id']= i[1]['p_hero_id'].astype(int)
        df_updated = df_updated.append(i[1], ignore_index = True)
    return df_updated

# train function

# eval function

if __name__ == "__main__":

    names_api, names_model, names_2_index = heroes_import('data/heroes.json')
    df_train = data_prep("data/liquid_picks_bans.csv")

    train_target = torch.tensor(df_train ['hero_id'].values)
    train = torch.tensor(df_train .drop(['Unnamed: 0', 'hero_id', 'ord', 'team', 'match_id'], axis=1).values)
    
    train_tensor = torch.utils.data.TensorDataset(train, train_target)
    trainloader = torch.utils.data.DataLoader(
        train_tensor,
        batch_size=22,
        shuffle=False,
        num_workers=2
    )
    
    input_size = train.size()[1]
    hidden_size = 55
    output_size = len(names_model) # temp solution
    model = RNN(input_size, hidden_size, output_size)
    
    
    criterion = nn.CrossEntropyLoss()
    learning_rate = .005
    optimizer = optim.SGD(model.parameters(), lr = learning_rate, momentum=.9)
    epochs = 2
    print_every = 1

    for epoch in range(epochs):
        for i, data in enumerate(trainloader,0):
            running_loss = 0
            hidden = model.initHidden()
            optimizer.zero_grad()
            inputs, targets = data
            # remove for loop
            for j in range(inputs.size()[0]):
                output, hidden = model(inputs[j], hidden)
                loss = criterion(output, targets[j].unsqueeze(0))
                running_loss += loss
            running_loss.backward()
            optimizer.step()
            print('[%d, %5d] loss: %.3f' %(epoch + 1, i + 1, running_loss.item() / 22))