import json
import time
import requests
import pandas as pd
import plotly.express as px

def getTeam(team_name, teams):
    team = teams.loc[teams['name'] == team_name]
    return team

def getMatches(team):
    r = requests.get('https://api.opendota.com/api/teams/{}/matches'.format(team['team_id'][0]))
    matches = r.json()
    return matches

def getPickBans(match, df):
    picks_bans = match['picks_bans']
    if picks_bans == None:
        return df
    dire_team = match['dire_team']
    radiant_team = match['radiant_team']
    for j in picks_bans:
        j['team_id'] = j['team']
    df = df.append(picks_bans, ignore_index = True)
    df = df.replace({"team" : {0:radiant_team['name'], 1:dire_team['name']}, 'team_id' : {0:radiant_team['team_id'], 1: dire_team['team_id']}})
    return df

def getWinner(match, df):
    radiant_win = match['radiant_win']
    dire_team = match['dire_team']
    radiant_team = match['radiant_team']
    if radiant_win == True:
        win = {"winner" : radiant_team['name'], "match_id" : str(match['match_id'])} # turn to string to prevent from turining into scientific notation
    elif radiant_win == False:
        win = {"winner" : dire_team['name'], "match_id" : str(match['match_id'])}
    df = df.append(win, ignore_index = True)
    return df

def windeltaPressence(df, df_win, team, heroes):
    # merge win data frame with the picks for the match and isolate a team
    df_picks_wins = df.merge(df_win, how='left', left_on='match_id', right_on='match_id')
    df_team_picks = df_picks_wins[df_picks_wins['team'] == team]

    # get number of wins and losses
    team_loss = df_team_picks[df_team_picks.winner != team].hero_id.value_counts().rename('number_of_losses').to_frame()
    team_win = df_team_picks[df_team_picks.winner == team].hero_id.value_counts().rename('number_of_wins').to_frame()
    df_bans = df[df['is_pick'] == False]['hero_id'].value_counts().rename('number_of_bans').to_frame()

    # merge wins, losses, and bans to all the heroes in the game
    df_win_loss = heroes.merge(team_loss, how='left', left_index=True, right_index=True).merge(team_win, how='left', left_index=True, right_index=True).merge(df_bans, how='left', left_index=True, right_index=True).fillna(0)

    # calculate win delta and pressence, remove characters that were never played
    df_win_loss['win_delta'] = ((df_win_loss['number_of_wins'] - df_win_loss['number_of_losses']) / len(df_win)) * 100
    df_win_loss['pressence'] = ((df_win_loss['number_of_wins'] + df_win_loss['number_of_losses']) / len(df_win)) * 100
    df_win_loss['ban_rate'] = (df_win_loss['number_of_bans'] / len(df_win)) * 100
    df_win_loss = df_win_loss[df_win_loss['pressence'] > 0]
    return df_win_loss

def pullPicksBans(matches, number = 100):
    if type(matches) != list:
        matches = [matches]
    i = 0
    df_pb = pd.DataFrame()
    df_win = pd.DataFrame()
    for m in matches:
        if i == number:
            # limmit number of matches read in
            break
        # get match data from api
        print('requseting match {}'.format(m["match_id"]))
        r = requests.get('https://api.opendota.com/api/matches/{}'.format(m['match_id']))
        match = r.json()
        df_pb = getPickBans(match, df_pb)
        df_win = getWinner(match, df_win)
        print('processed {} matches'.format(i + 1))

        # prevent request errors
        time.sleep(5)
        i += 1
    df_pb['hero_name'] = df_pb['hero_id']
    df_pb = df_pb.replace({'hero_name' : names})
    df_win['match_id'] = df_win['match_id'].astype('int64')
    df_winD = windeltaPressence(df_pb, df_win, team_name, df_heroes)
    return df_pb, df_win, df_winD

def plotBalance(df, team):
    fig = px.scatter(df, x = 'pressence', y = 'win_delta', hover_data=['name'], size='ban_rate',
                    title= 'Pressence vs Win Delta for {}'.format(team))
    fig.update_layout(shapes=[
        dict(
            type= 'line',
            yref= 'paper', y0=0, y1=1,
            xref='x', x0=(10/len(df_heroes)) * 100, x1=(10/len(df_heroes)) * 100
        ),
        dict(
            type= 'line',
            yref= 'y', y0=0, y1=0,
            xref='paper', x0=0, x1=1
        )
    ])
    fig.show()

if __name__ == "__main__":
    names = dict()
    with open('data/heroes.json') as f:
        data = json.load(f)
        for i in data:
            names[i["id"]] = i['localized_name']
    df_heroes = pd.DataFrame.from_dict(names, orient='index', columns=['name'])

    input_file = open('data/teams.json', encoding='utf-8')
    teams = json.load(input_file)
    input_file.close()

    df_teams = pd.DataFrame(teams)

    team_name = "Team Secret"
    team = getTeam(team_name, df_teams)
    matches = getMatches(team)

    # rename df's
    df_pb, df_win, df_winD = pullPicksBans(matches, 20)
    plotBalance(df_winD, team_name)