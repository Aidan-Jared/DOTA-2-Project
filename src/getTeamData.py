import json
import time
import requests
import pandas as pd
import plotly.express as px

def getTeam(team_name, teams):
    if type(team_name) == list:
        team = pd.DataFrame()
        for i in team_name:
            team = team.append(teams.loc[teams['name'] == i], ignore_index = True)
    else:
        team = teams.loc[teams['name'] == team_name]
    return team

def getMatches(team):
    if len(team) > 1:
        matches = []
        for i in team['team_id']:
            r = requests.get('https://api.opendota.com/api/teams/{}/matches'.format(i))
            matches.append(r.json())
    else:
        r = requests.get('https://api.opendota.com/api/teams/{}/matches'.format(team['team_id'][0]))
        matches = r.json()
    return matches

def getPickBans(match, df):
    picks_bans = match['picks_bans']
    if picks_bans == None or picks_bans[0]['match_id'] in df:
        # prevent duplicate matches and none types
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
    if radiant_win == None or match['match_id'] in df:
        # prevent duplicate matches and none types
        return df
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
    if type(team) == list:
        df_team_picks = pd.DataFrame()
        team_loss = pd.DataFrame()
        team_win = pd.DataFrame()
        df_bans = pd.DataFrame()
        df_win_loss = pd.DataFrame()
        for i in team:
            # need to reset index and prevent overwriting of all data for team name
            df_team_picks = df_team_picks.append(df_picks_wins.loc[df_picks_wins['team'] == i], ignore_index = True)
            team_loss = team_loss.append(df_team_picks[df_team_picks.winner != i].hero_id.value_counts().to_frame('number_of_losses'))
            team_win = team_win.append(df_team_picks[df_team_picks.winner == i].hero_id.value_counts().to_frame('number_of_wins'))
            temp = df[df['is_pick'] == False]['hero_id'].value_counts().to_frame('number_of_bans')
            temp['team'] = i
            df_bans = df_bans.append(temp)
            temp = heroes.merge(team_loss, how='left', left_index=True, right_index=True).merge(team_win, how='left', left_index=True, right_index=True).merge(df_bans, how='left', left_index=True, right_index=True).fillna(0)
            temp['win_delta'] = ((temp['number_of_wins'] - temp['number_of_losses']) / len(df_win)) * 100
            temp['pressence'] = ((temp['number_of_wins'] + temp['number_of_losses']) / len(df_win)) * 100
            temp['ban_rate'] = (temp['number_of_bans'] / len(df_win)) * 100
            temp = temp[temp['pressence'] > 0]
            df_win_loss = df_win_loss.append(temp)
    else:
        # get number of wins and losses
        df_team_picks = df_picks_wins[df_picks_wins['team'] == team]
        team_loss = df_team_picks[df_team_picks.winner != team].hero_id.value_counts().rename('number_of_losses').to_frame()
        team_win = df_team_picks[df_team_picks.winner == team].hero_id.value_counts().rename('number_of_wins').to_frame()
        df_bans = df[df['is_pick'] == False]['hero_id'].value_counts().rename('number_of_bans').to_frame()
        df_bans['team'] = team

        # merge wins, losses, and bans to all the heroes in the game
        df_win_loss = heroes.merge(team_loss, how='left', left_index=True, right_index=True).merge(team_win, how='left', left_index=True, right_index=True).merge(df_bans, how='left', left_index=True, right_index=True).fillna(0)

        # calculate win delta and pressence, remove characters that were never played
        df_win_loss['win_delta'] = ((df_win_loss['number_of_wins'] - df_win_loss['number_of_losses']) / len(df_win)) * 100
        df_win_loss['pressence'] = ((df_win_loss['number_of_wins'] + df_win_loss['number_of_losses']) / len(df_win)) * 100
        df_win_loss['ban_rate'] = (df_win_loss['number_of_bans'] / len(df_win)) * 100
        df_win_loss = df_win_loss[df_win_loss['pressence'] > 0]
    return df_win_loss

def getMatch(matches, number, df_pb, df_win):
    i = 0
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
    return df_pb, df_win

def pullPicksBans(matches, number = 100):
    if type(matches) != list:
        matches = [matches]
    df_pb = pd.DataFrame()
    df_win = pd.DataFrame()
    if type(matches[0]) == list:
        for i in matches:
            df_pb, df_win = getMatch(i, number, df_pb, df_win)
    else:
        df_pb, df_win = getMatch(matches, number, df_pb, df_win)
    df_pb['hero_name'] = df_pb['hero_id']
    df_pb = df_pb.replace({'hero_name' : names})
    df_win['match_id'] = df_win['match_id'].astype('int64')
    df_winD = windeltaPressence(df_pb, df_win, team_name, df_heroes)
    return df_pb, df_win, df_winD

def plotBalance(df, team):
    fig = px.scatter(df, x = 'pressence', y = 'win_delta', hover_data=['name'], size='ban_rate', color= 'team',
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

    team_name = ["Team Secret", "Team Liquid"]
    # team_name = "Team Secret"
    team = getTeam(team_name, df_teams)
    matches = getMatches(team)

    # rename df's
    df_pb, df_win, df_winD = pullPicksBans(matches, 5)
    plotBalance(df_winD, team_name)