from scrapers.rushing_scraper import scrape_rushing
from utils.teams import team_abb_to_full, team_full_to_abb
from scrapers.team_rushing_scraper import scrape_team_rushing
import pandas as pd
from scrapers.receiving_scraper import scrape_receiving
from utils.helpers import find_matchups
import numpy as np

def combine_rb_stats(rushing_stats, receiving_stats):
    all_columns = {
        "Player": "",
        "Team": "",
        "Att/G": 0, 
        "Carry %": 0.0,
        "Y/Carry": 0.0, 
        "TD %": 0.0,
        "Tgt/G": 0, 
        "Y/R": 0, 
        "R/G": 0, 
        "Y/G": 0, 
        "TD/G": 0
    }

    if isinstance(rushing_stats, tuple):
        rushing_stats = list(rushing_stats[0]) if rushing_stats else []
    rushing_dict = {stat['Player']: stat for stat in rushing_stats}
    receiving_dict = {stat['Player']: stat for stat in receiving_stats}

    team_rushing_stats = scrape_team_rushing()
    team_rushing_dict = {team_stat['Team']: team_stat['Att'] for team_stat in team_rushing_stats}

    combined_stats = []
    all_players = set(rushing_dict.keys()).union(set(receiving_dict.keys()))

    for player in all_players:
        combined_stat = all_columns.copy()
        combined_stat["Player"] = player  
        all_players = set(rushing_dict.keys()).union(set(receiving_dict.keys()))

        if player in rushing_dict:
            for key, value in rushing_dict[player].items():
                if key != "Att":  # 
                    combined_stat[key] = value if value is not None else 0

        if player in receiving_dict:
            for key, value in receiving_dict[player].items():
                combined_stat[key] = value if value is not None else 0

        if player in rushing_dict:
            player_team_abb = rushing_dict[player]["Team"]
            player_att = float(rushing_dict[player].get("Att", "0"))  

            full_team_name = team_abb_to_full.get(player_team_abb)

            if full_team_name and full_team_name in team_rushing_dict:
                team_att = float(team_rushing_dict.get(full_team_name, "0"))  

                if team_att > 0:  
                    carry_percentage = (player_att / team_att) * 100
                else:
                    carry_percentage = 0.0
                combined_stat["Carry %"] = f"{carry_percentage:.2f}"

        combined_stats.append(combined_stat)

    return combined_stats

def make_rb_sheet(opp_stats):
    #RB DATA
    rb_single_data = scrape_rushing()
    
    wr_te_stats, rb_stats = scrape_receiving()
    rb_data = combine_rb_stats(rb_single_data, rb_stats)
    df_rb = pd.DataFrame(rb_data)

    df_rb['Att/G'] = pd.to_numeric(df_rb['Att/G'], errors='coerce')
    df_rb['Carry %'] = pd.to_numeric(df_rb['Carry %'], errors='coerce')
    df_rb['Y/Carry'] = pd.to_numeric(df_rb['Y/Carry'], errors='coerce')
    df_rb['TD %'] = pd.to_numeric(df_rb['TD %'], errors='coerce')
    df_rb['Tgt/G'] = pd.to_numeric(df_rb['Tgt/G'], errors='coerce')
    df_rb['Y/R'] = pd.to_numeric(df_rb['Y/R'], errors='coerce')
    df_rb['R/G'] = pd.to_numeric(df_rb['R/G'], errors='coerce')
    df_rb['Y/G'] = pd.to_numeric(df_rb['Y/G'], errors='coerce')
    df_rb['TD/G'] = pd.to_numeric(df_rb['TD/G'], errors='coerce')

 
    df_rb.fillna(0, inplace=True)

    games_for_cur_round = find_matchups()

    df_rb = pd.merge(df_rb, games_for_cur_round[['Home Team abb', 'Away Team abb']], left_on='Team', right_on='Home Team abb', how='left')

    df_rb = pd.merge(df_rb, games_for_cur_round[['Home Team abb', 'Away Team abb']], left_on='Team', right_on='Away Team abb', how='left')

    df_rb['Home Team abb'] = df_rb['Home Team abb_x'].combine_first(df_rb['Home Team abb_y'])
    df_rb['Away Team abb'] = df_rb['Away Team abb_x'].combine_first(df_rb['Away Team abb_y'])

    df_rb.drop(columns=['Home Team abb_x', 'Home Team abb_y', 'Away Team abb_x', 'Away Team abb_y'], inplace=True)

    df_rb['Opponent Team abb'] = np.where(df_rb['Home Team abb'] == df_rb['Team'], df_rb['Away Team abb'], df_rb['Home Team abb'])

    df_rb.drop(columns=['Home Team abb', 'Away Team abb'], inplace=True)
    df_rb.rename(columns={'Opponent Team abb': 'Weekly Opponent'}, inplace=True)
    
    df_team = opp_stats

    df_team['Team'] = df_team['Team'].map(team_full_to_abb).fillna(df_team['Team'])

    df_final = pd.merge(df_rb, df_team, left_on='Weekly Opponent', right_on='Team', how='left')

    df_final.rename(columns={'Team_x': 'Team'}, inplace=True)
    df_final.drop(columns=['Team_y'], inplace=True)

    return df_final