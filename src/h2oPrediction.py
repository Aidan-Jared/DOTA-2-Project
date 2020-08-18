import json
import pandas as pd
import h2o
from h2o.estimators import H2ORandomForestEstimator
h2o.init()

if __name__ == "__main__":
    names = dict()
    with open('data/heroes.json') as f:
        data = json.load(f)
        for i in data:
            names[i["id"]] = i['localized_name']
    df_heroes = pd.DataFrame.from_dict(names, orient='index', columns=['name'])

    hf = h2o.import_file("data/liquid_picks_bans.csv")
    hf['hero_id'] = hf['hero_id'].asfactor()
    predictors = ['is_pick', 'order']
    response = 'hero_id'

    pick_ban_model = H2ORandomForestEstimator(
        ntrees = 10,
        max_depth = 5,
        min_rows = 10,
        nfolds = 10,
    )

    pick_ban_model.train(
        x = predictors,
        y = response,
        training_frame = hf,
    )