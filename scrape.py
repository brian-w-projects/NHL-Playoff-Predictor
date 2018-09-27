from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
from pandas import DataFrame
import time


def result_type(df, *col):
    if df[col[0]] > df[col[1]]:
        if df['type'] == 'SO':
            return 4
        else:
            return 1
    elif df['type'] == 'OT':
        return 3
    return 2


def strength_calc(team, df, wins):
    return df \
        .loc[lambda x: (x['away_id'] == team) | (x['home_id'] == team)] \
        .assign(opponent=lambda x: x['away_id'] + x['home_id'] - team) \
        .drop(columns=['year', 'away_id', 'home_id']) \
        .sort_values('id') \
        .tail(n=41) \
        .merge(wins, left_on='opponent', right_on='team_id') \
        ['result'] \
        .sum()


points = DataFrame(data={'result': ['W', 'L', 'OTL', 'SOW'], 'points': [2, 0, 1, 2]}) \
    .reset_index() \
    .rename(columns={'index': 'id'}) \
    .assign(id=lambda x: x['id'] + 1)


def summary_year(par_year):
    r = requests.get(f'https://www.hockey-reference.com/leagues/NHL_{par_year}_games.html')
    soup = BeautifulSoup(r.content, 'html.parser')

    df = DataFrame(np.array([ele.get_text() for ele in soup.select('#games > tbody > tr > .')]).reshape(-1, 9)) \
        .drop(columns=[6, 7, 8], axis=1) \
        .rename(columns={0: 'date', 1: 'away', 2: 'away_goals', 3: 'home', 4: 'home_goals', 5: 'type'}) \
        .assign(away_result=lambda x: x.apply(result_type, args=['away_goals', 'home_goals'], axis=1)) \
        .assign(home_result=lambda x: x.apply(result_type, args=['home_goals', 'away_goals'], axis=1)) \
        .assign(year=par_year) \
        .reset_index() \
        .rename(columns={'index': 'id'}) \
        .assign(id=lambda x: x['id'] + 1) \
        .loc[lambda x: x['away_goals'] != '']

    teams = DataFrame(df['home'].unique(), columns=['team']) \
        .assign(team=lambda x: x['team'].str.split(' ').str[-1]) \
        .sort_values('team') \
        .reset_index(drop=True) \
        .reset_index() \
        .rename(columns={'index': 'id'}) \
        .assign(id=lambda x: x['id'] + 1)

    schedule = df[['id', 'year', 'away', 'home']] \
        .assign(away=lambda x: x['away'].str.split(' ').str[-1]) \
        .assign(home=lambda x: x['home'].str.split(' ').str[-1]) \
        .merge(teams[['id', 'team']], left_on='away', right_on='team') \
        .merge(teams[['id', 'team']], left_on='home', right_on='team') \
        [['id_x', 'year', 'id_y', 'id']] \
        .rename(columns={'id_x': 'id', 'id_y': 'away_id', 'id': 'home_id'}) \
        .sort_values('id') \
        .reset_index(drop=True)

    away = df.loc[:, ['id', 'year', 'away', 'away_goals', 'away_result']] \
        .rename(columns={'away': 'team', 'away_goals': 'goals', 'away_result': 'result_id'})
    home = df.loc[:, ['id', 'year', 'home', 'home_goals', 'home_result']] \
        .rename(columns={'home': 'team', 'home_goals': 'goals', 'home_result': 'result_id'})

    results = pd.concat([away, home]) \
        .assign(team=lambda x: x['team'].str.split(' ').str[-1]) \
        .merge(teams, left_on='team', right_on='team') \
        .drop(columns=['team']) \
        .rename(columns={'id_x': 'game_id', 'id_y': 'team_id'}) \
        .sort_values('game_id') \
        .reset_index() \
        .rename(columns={'index': 'id'}) \
        [['id', 'game_id', 'year', 'team_id', 'goals', 'result_id']]

    r = requests.get(f'https://www.hockey-reference.com/leagues/NHL_{par_year}.html')
    soup = BeautifulSoup(r.content, 'html.parser')

    df_2 = pd.concat([DataFrame([ele.get_text() for ele in soup.select('#standings_EAS > tbody > tr > th')]),
                      DataFrame([ele.get_text() for ele in soup.select('#standings_WES > tbody > tr > th')])
                     ])

    playoffs = df_2 \
        .assign(playoffs=lambda x: x.iloc[:, 0].str.endswith('*').astype(int),
                year=par_year,
                team=lambda x: x.iloc[:, 0].str.split(' ').str[-1].str.replace('*', '')) \
        .merge(teams, left_on='team', right_on='team') \
        .drop(columns=[0, 'team']) \
        [['id', 'year', 'playoffs']]

    wins = results \
        .merge(points[['id', 'result']], left_on='result_id', right_on='id') \
        .sort_values('game_id') \
        .drop(columns=['id_x', 'goals', 'result_id', 'id_y']) \
        .groupby('team_id') \
        .head(41) \
        .loc[lambda x: x['result'] == 'W'] \
        .groupby('team_id') \
        .count()

    goal_diff = results \
        .merge(results, left_on='game_id', right_on='game_id') \
        .loc[lambda x: x['team_id_x'] != x['team_id_y']] \
        .assign(diff = lambda x: x['goals_x'].astype(int) - x['goals_y'].astype(int)) \
        .drop(columns=['result_id_x', 'team_id_y', 'result_id_y', 'goals_x', 'goals_y']) \
        .groupby('team_id_x') \
        .head(41) \
        .groupby('team_id_x') \
        ['diff'] \
        .sum() \
        .reset_index()

    strength = teams \
        .assign(strength=lambda x: x['id'].apply(strength_calc, df=schedule, wins=wins))

    total_points = results \
        .merge(points[['id', 'points']], left_on='result_id', right_on='id') \
        .sort_values('game_id') \
        .drop(columns=['game_id', 'goals', 'result_id', 'id_y', 'id_x', 'year']) \
        .groupby('team_id') \
        .head(41) \
        .groupby('team_id') \
        .sum()

    summary = teams \
        .merge(wins, left_on='id', right_on='team_id') \
        .merge(goal_diff, left_on='id', right_on='team_id_x') \
        .merge(strength, left_on='id', right_on='id')  \
        .merge(total_points, left_on='id', right_on='team_id') \
        .merge(playoffs, left_on='id', right_on='id') \
        .drop(columns=['team_x', 'team_id_x', 'team_y', 'year_x', 'game_id']) \
        .rename(columns={'result': 'wins', 'year_y': 'year'})

    return summary


for i in range(2008, 2019):
    ret = summary_year(i)
    with open(f'summary{i}.csv', 'w') as writer:
        writer.write(ret.to_csv(index=False))
    time.sleep(5)