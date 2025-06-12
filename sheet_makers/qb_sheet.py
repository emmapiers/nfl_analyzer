from scrapers.qb_scraper import scrape_qb
from scrapers.rushing_scraper import scrape_rushing
from scrapers.team_rushing_scraper import scrape_team_rushing
from utils.teams import team_full_to_abb, team_abb_to_full
import pandas as pd
import numpy as np
from utils.helpers import find_matchups

def combine_qb_stats(qb_rushing_stats, qb_passing_stats, team_rushing_stats):
    all_columns = {
        "Player": "",
        "Team": "",
        "Cmp/G": 0,
        "Att/G": 0, 
        "Yds/G": 0,
        "TD/G": 0.0,
        "TD%": 0.0,
        "Y/A": 0.0, 
        "Carry %": 0.0, 
        "Yds/Carry": 0,
    }
    combined_stats = []

    rushing_dict =  {stat['Player']: stat for stat in qb_rushing_stats}
    passing_dict = {stat['Player']: stat for stat in qb_passing_stats}

    team_rushing_dict = {team_stat['Team']: team_stat['Att'] for team_stat in team_rushing_stats}
    
    all_players = set(rushing_dict.keys()).union(set(passing_dict.keys()))

    for player in all_players:
        combined_stat = all_columns.copy()
        combined_stat["Player"] = player 

        if player in rushing_dict:
            for key, value in rushing_dict[player].items():
                if key != "Att":
                    combined_stat[key] = value if value is not None else "0"

        if player in passing_dict:
            for key, value in passing_dict[player].items():
                combined_stat[key] = value if value is not None else "0"

        if player in rushing_dict:
            player_team_abb = rushing_dict[player]["Team"] 
            player_att = float(rushing_dict[player]["Att"])
            
            full_team_name = team_abb_to_full.get(player_team_abb)

            if full_team_name and full_team_name in team_rushing_dict:
                team_att = float(team_rushing_dict[full_team_name])  

                carry_percentage = (player_att / team_att) * 100
                combined_stat["Carry %"] = f"{carry_percentage:.2f}"  

        combined_stats.append(combined_stat)

    return combined_stats


def make_qb_sheet(opp_stats):
    qb_passing_stats = scrape_qb()
    rb_stats, qb_rushing_stats = scrape_rushing()
    team_rushing_stats = scrape_team_rushing()
    
    qb_data = combine_qb_stats(qb_rushing_stats, qb_passing_stats, team_rushing_stats)

    df_qb = pd.DataFrame(qb_data)
    df_qb['Cmp/G'] = pd.to_numeric(df_qb['TD%'], errors='coerce')
    df_qb['Att/G'] = pd.to_numeric(df_qb['Y/A'], errors='coerce')
    df_qb['Yds/G'] = pd.to_numeric(df_qb['Carry %'], errors='coerce')
    df_qb['TD/G'] = pd.to_numeric(df_qb['Yds/Carry'], errors='coerce')
    df_qb['TD%'] = pd.to_numeric(df_qb['TD%'], errors='coerce')
    df_qb['Y/A'] = pd.to_numeric(df_qb['Y/A'], errors='coerce')
    df_qb['Carry %'] = pd.to_numeric(df_qb['Carry %'], errors='coerce')
    df_qb['Yds/Carry'] = pd.to_numeric(df_qb['Yds/Carry'], errors='coerce')
    
    df_qb.fillna(0, inplace=True)

    games_for_cur_round = find_matchups()

    df_qb = pd.merge(df_qb, games_for_cur_round[['Home Team abb', 'Away Team abb']], left_on='Team', right_on='Home Team abb', how='left')

    df_qb = pd.merge(df_qb, games_for_cur_round[['Home Team abb', 'Away Team abb']], left_on='Team', right_on='Away Team abb', how='left')

    df_qb['Home Team abb'] = df_qb['Home Team abb_x'].combine_first(df_qb['Home Team abb_y'])
    df_qb['Away Team abb'] = df_qb['Away Team abb_x'].combine_first(df_qb['Away Team abb_y'])

    df_qb.drop(columns=['Home Team abb_x', 'Home Team abb_y', 'Away Team abb_x', 'Away Team abb_y'], inplace=True)

    df_qb['Opponent Team abb'] = np.where(df_qb['Home Team abb'] == df_qb['Team'], df_qb['Away Team abb'], df_qb['Home Team abb'])

    df_qb.drop(columns=['Home Team abb', 'Away Team abb'], inplace=True)
    df_qb.rename(columns={'Opponent Team abb': 'Weekly Opponent'}, inplace=True)
    
    df_team = opp_stats
    
    df_team['Team'] = df_team['Team'].map(team_full_to_abb).fillna(df_team['Team'])

    df_final = pd.merge(df_qb, df_team, left_on='Weekly Opponent', right_on='Team', how='left')

    df_final.rename(columns={'Team_x': 'Team'}, inplace=True)
    df_final.drop(columns=['Team_y'], inplace=True)

    return df_final
    