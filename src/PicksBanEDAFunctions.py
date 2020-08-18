import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def bar_plot(df, title, figsize=(5,15), number_col = None):
    df.value_counts().iloc[:number_col].plot(kind = 'barh', figsize=figsize, title = title)

def windelta_pressence(df_picks, df_win, team, heroes):
    # merge win data frame with the picks for the match and isolate a team
    df_picks_wins = df_picks.merge(df_win, how='left', left_on='match_id', right_on='match_id')
    df_team_picks = df_picks_wins[df_picks_wins['team'] == team]

    # get number of wins and losses
    team_loss = df_team_picks[df_team_picks.winner != team].hero_id.value_counts().rename('number_of_losses')
    team_win = df_team_picks[df_team_picks.winner == team].hero_id.value_counts().rename('number_of_wins')

    # merge wins and losses to all the heroes in the game
    df_win_loss = heroes.merge(team_loss.to_frame(), how='left', left_on='name', right_index=True, ).merge(team_win.to_frame(), how='left', left_on='name', right_index=True).fillna(0)

    # calculate win delta and pressence, remove characters that where never played
    df_win_loss['win_delta'] = (df_win_loss['number_of_wins'] - df_win_loss['number_of_losses']) / len(df_win)
    df_win_loss['pressence'] = (df_win_loss['number_of_wins'] + df_win_loss['number_of_losses']) / len(df_win)
    df_win_loss = df_win_loss[df_win_loss['pressence'] > 0]
    return df_win_loss