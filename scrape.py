from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
from pandas import DataFrame
import time


def create_raw_data(years):
    def result_type(df, *col):
        if df[col[0]] > df[col[1]]:
            if df['type'] == 'SO':
                return 4
            else:
                return 1
        elif df['type'] == 'OT':
            return 3
        return 2

    raw_data = DataFrame()

    for year in years:
        r = requests.get(f'https://www.hockey-reference.com/leagues/NHL_{year}_games.html')
        soup = BeautifulSoup(r.content, 'html.parser')

        raw_data = pd.concat([
            raw_data,
            DataFrame(np.array([ele.get_text() for ele in soup.select('#games > tbody > tr > .')]).reshape(-1, 9)) \
                .drop(columns=[0, 6, 7, 8], axis=1) \
                .rename(columns={1: 'away', 2: 'away_goals', 3: 'home', 4: 'home_goals', 5: 'type'}) \
                .assign(away_result=lambda x: x.apply(result_type, args=['away_goals', 'home_goals'], axis=1),
                        home_result=lambda x: x.apply(result_type, args=['home_goals', 'away_goals'], axis=1),
                        year=f'{year}') \
                .drop(columns=['type'])
        ])
        time.sleep(5)

    raw_data = raw_data \
        .loc[lambda x: x['away_goals'] != ''] \
        .reset_index(drop=True) \
        .reset_index() \
        .rename(columns={'index': 'id'}) \
        .assign(id=lambda x: x['id'] + 1)

    return raw_data


def create_points():
    points = DataFrame(data={'result': ['W', 'L', 'OTL', 'SOW'], 'points': [2, 0, 1, 2]}) \
        .reset_index() \
        .rename(columns={'index': 'id'}) \
        .assign(id=lambda x: x['id'] + 1)
    with open('data/points.csv', 'w') as writer:
        writer.write(points.to_csv(index=False))

    return points


def create_teams(df):
    teams = DataFrame(df['home'].str.split(' ').str[-1].unique(), columns=['team']) \
        .sort_values('team') \
        .reset_index(drop=True) \
        .reset_index() \
        .rename(columns={'index': 'id'}) \
        .assign(id=lambda x: x['id'] + 1)
    with open('data/teams.csv', 'w') as writer:
        writer.write(teams.to_csv(index=False))

    return teams


def create_playoffs(years, teams_df):
    playoffs = DataFrame()

    for year in years:
        r = requests.get(f'https://www.hockey-reference.com/leagues/NHL_{year}.html')
        soup = BeautifulSoup(r.content, 'html.parser')

        playoffs = pd.concat([
                     playoffs,
                     pd.concat([DataFrame([ele.get_text() for ele in soup.select('#standings_EAS > tbody > tr > th')]),
                                DataFrame([ele.get_text() for ele in soup.select('#standings_WES > tbody > tr > th')])
                                ]) \
                                .assign(playoffs=lambda x: x.iloc[:, 0].str.endswith('*').astype(int),
                                        year=f'{year}',
                                        team=lambda x: x.iloc[:, 0].str.split(' ').str[-1].str.replace('*', '')) \
                                .merge(teams_df, left_on='team', right_on='team') \
                                .drop(columns=[0, 'team']) \
                                [['id', 'year', 'playoffs']] \
                                .rename(columns={'id': 'team_id'})
                     ])
        time.sleep(5)

    playoffs = playoffs \
        .reset_index(drop=True) \
        .reset_index() \
        .rename(columns={'index': 'id'}) \
        .assign(id=lambda x: x['id'] + 1)

    with open('data/playoffs.csv', 'w') as writer:
        writer.write(playoffs.to_csv(index=False))

    return playoffs


def create_schedule(df, teams_df):
    schedule = df[['id', 'year', 'away', 'home']] \
        .assign(away=lambda x: x['away'].str.split(' ').str[-1],
                home=lambda x: x['home'].str.split(' ').str[-1]) \
        .merge(teams_df[['id', 'team']], left_on='away', right_on='team') \
        .merge(teams_df[['id', 'team']], left_on='home', right_on='team') \
        [['id_x', 'year', 'id_y', 'id']] \
        .rename(columns={'id_x': 'id', 'id_y': 'away_id', 'id': 'home_id'}) \
        .sort_values('id') \
        .reset_index(drop=True)

    with open('data/schedule.csv', 'w') as writer:
        writer.write(schedule.to_csv(index=False))

    return schedule


def create_results(df, teams_df):
    away = df.loc[:, ['id', 'year', 'away', 'away_goals', 'away_result']] \
        .rename(columns={'away': 'team', 'away_goals': 'goals', 'away_result': 'points_id'})
    home = df.loc[:, ['id', 'year', 'home', 'home_goals', 'home_result']] \
        .rename(columns={'home': 'team', 'home_goals': 'goals', 'home_result': 'points_id'})

    results = pd.concat([away, home]) \
        .assign(team=lambda x: x['team'].str.split(' ').str[-1]) \
        .merge(teams_df, left_on='team', right_on='team') \
        .drop(columns=['team']) \
        .rename(columns={'id_x': 'game_id', 'id_y': 'team_id'}) \
        .sort_values('game_id') \
        .reset_index() \
        .rename(columns={'index': 'id'}) \
        .assign(id=lambda x: x['id'] + 1) \
        [['id', 'game_id', 'year', 'team_id', 'goals', 'points_id']] \
        .sort_values('id')

    with open('data/results.csv', 'w') as writer:
        writer.write(results.to_csv(index=False))

    return results


if __name__ == '__main__':
    years = range(2008, 2019, 1)
    raw_data = create_raw_data(years)
    create_points()
    teams = create_teams(raw_data)
    create_results(raw_data, teams)
    create_schedule(raw_data, teams)
    create_playoffs(years, teams)