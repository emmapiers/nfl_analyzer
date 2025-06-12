from utils.teams import team_full_to_abb
import pandas as pd
from utils.helpers import find_matchups, normalize_player_name, convert_tm_percentage
import numpy as np
from scrapers.receiving_scraper import scrape_receiving
from scrapers.target_percentage import scrape_target_percentage

def combine_wr_te_stats():
    wr_te_tm_data = scrape_target_percentage()
    wr_te_receiving_data, rb_receiving_stats = scrape_receiving()

    all_columns = {
        "Player": "",
        "Team": "",
        "Position": "",
        "Tgt/G": 0.0, 
        "Y/R": 0.0,
        "R/G": 0.0, 
        "Y/G": 0.0, 
        "TD/G": 0.0,
        "TM %": 0.0  
    }
 
    combined_stats = []

    tm_percentage_dict = {}
    for stat in wr_te_tm_data:
        normalized_name = normalize_player_name(stat['Player'])
        if normalized_name is not None:
            tm_percentage_dict[normalized_name] = stat
    
    receiving_dict = {}
    for stat in wr_te_receiving_data:
        normalized_name = normalize_player_name(stat['Player'])
        if normalized_name is not None:
            receiving_dict[normalized_name] = stat

    all_players = set(tm_percentage_dict.keys()).union(set(receiving_dict.keys()))
    
    for player in all_players:
        combined_stat = all_columns.copy()
        combined_stat["Player"] = player  

        if player in receiving_dict:
            for key, value in receiving_dict[player].items():
                combined_stat[key] = value if value is not None else 0

        if player in tm_percentage_dict:
            combined_stat["TM %"] = convert_tm_percentage(tm_percentage_dict[player].get("TM %", "N/A"))
            combined_stat["Position"] = tm_percentage_dict[player].get("Position", "")

        combined_stats.append(combined_stat)

    return combined_stats

def make_wr_sheet(opp_stats):
    wr_data = combine_wr_te_stats()
    df_wr = pd.DataFrame(wr_data)

    df_wr['TM %'] = pd.to_numeric(df_wr['TM %'], errors='coerce')
    df_wr['Tgt/G'] = pd.to_numeric(df_wr['Tgt/G'], errors='coerce')
    df_wr['Y/R'] = pd.to_numeric(df_wr['Y/R'], errors='coerce')
    df_wr['R/G'] = pd.to_numeric(df_wr['R/G'], errors='coerce')
    df_wr['Y/G'] = pd.to_numeric(df_wr['Y/G'], errors='coerce')
    df_wr['TD/G'] = pd.to_numeric(df_wr['TD/G'], errors='coerce')

    df_wr.fillna(0, inplace=True)

    games_for_cur_round = find_matchups()

    df_wr = pd.merge(df_wr, games_for_cur_round[['Home Team abb', 'Away Team abb']], left_on='Team', right_on='Home Team abb', how='left')
    df_wr = pd.merge(df_wr, games_for_cur_round[['Home Team abb', 'Away Team abb']], left_on='Team', right_on='Away Team abb', how='left')

    df_wr['Home Team abb'] = df_wr['Home Team abb_x'].combine_first(df_wr['Home Team abb_y'])
    df_wr['Away Team abb'] = df_wr['Away Team abb_x'].combine_first(df_wr['Away Team abb_y'])

    df_wr.drop(columns=['Home Team abb_x', 'Home Team abb_y','Away Team abb_x', 'Away Team abb_y'], inplace=True)
    df_wr['Opponent Team abb'] = np.where(df_wr['Home Team abb'] == df_wr['Team'], df_wr['Away Team abb'], df_wr['Home Team abb'])

    df_wr.drop(columns=['Home Team abb', 'Away Team abb'], inplace=True)
    df_wr.rename(columns={'Opponent Team abb': 'Weekly Opponent'}, inplace=True)
    
    df_team = opp_stats
    
    df_team['Team'] = df_team['Team'].map(team_full_to_abb).fillna(df_team['Team'])

    df_final = pd.merge(df_wr, df_team, left_on='Weekly Opponent', right_on='Team', how='left')
    df_final.rename(columns={'Team_x': 'Team'}, inplace=True)
    df_final.drop(columns=['Team_y'], inplace=True)

    return df_final