from scrapers.team_offense_scraper import scrape_team_offense
from scrapers.team_defense_scraper import scrape_team_defense
from scrapers.urls import team_against_rb_fantasy_url, team_against_qb_fantasy_url, team_against_wr_fantasy_url, team_against_te_fantasy_url
from utils.teams import team_full_to_abb
from scrapers.base_scraper import get_soup, get_headers_and_rows
import pandas as pd
from utils.helpers import find_matchups
import numpy as np

def combine_team_stats(offense_data, defense_data, dk_points_data):
    combined_list = []
    
    for dk_item in dk_points_data:
        full_name = dk_item['Team']
        dk_item['Team'] = team_full_to_abb.get(full_name, full_name)

    for offense_item in offense_data:
        team_name = offense_item['Team']
        
        matching_defense_item = next((item for item in defense_data if item['Team'] == team_name), None)
        matching_dk_points_item = next((item for item in dk_points_data if item['Team'] == team_name), None)
        
        combined_item = {**offense_item}
        if matching_defense_item:
            combined_item.update(matching_defense_item)
        
        if matching_dk_points_item:
            combined_item.update(matching_dk_points_item)
        
        combined_list.append(combined_item)
    
    return combined_list

def scrape_dk_points(url, position):
    soup = get_soup(url)
    headers, rows = get_headers_and_rows(soup, "fantasy_def", False)

    dk_points_stats = []

    for row in rows:
        headers = row.find_all('th', {'data-stat': 'team'})
        if headers:  
            team = headers[0].text.strip()  
            cols = row.find_all('td')
            if cols:
                dkpt = cols[-2].text.strip()  
                
                dk_points_stats.append({
                    "Team": team,
                    f"DKPt Against {position}": dkpt
                })


    return dk_points_stats

def merge_dk_team_data(rb_url, qb_url, wr_url, te_url):
    rb_data = scrape_dk_points(rb_url, 'RB')
    qb_data = scrape_dk_points(qb_url, 'QB')
    wr_data = scrape_dk_points(wr_url, 'WR')
    te_data = scrape_dk_points(te_url, 'TE')
    merged_data = {}

    for entry in rb_data:
        team = entry["Team"]
        merged_data[team] = {"Team": team, "DKPt Against RB": entry["DKPt Against RB"]}

    for data, pos in [(qb_data, "DKPt Against QB"), (wr_data, "DKPt Against WR"), (te_data, "DKPt Against TE")]:
        for entry in data:
            team = entry["Team"]
            if team in merged_data:
                merged_data[team][pos] = entry[pos]
            else:
                merged_data[team] = {"Team": team, pos: entry[pos]}

    return list(merged_data.values())

def make_opp_stats():
    offense_data = scrape_team_offense()
    defense_data = scrape_team_defense()
    dk_points_data = merge_dk_team_data(team_against_rb_fantasy_url, team_against_qb_fantasy_url, team_against_wr_fantasy_url, team_against_te_fantasy_url)

    team_data = combine_team_stats(offense_data, defense_data, dk_points_data)
    
    df_t = pd.DataFrame(team_data)
    
    df_t['Plays/G'] = pd.to_numeric(df_t['Plays/G'], errors='coerce')
    df_t['Pass %/G'] = pd.to_numeric(df_t['Pass %/G'], errors='coerce')
    df_t['Rush %/G'] = pd.to_numeric(df_t['Rush %/G'], errors='coerce')
    df_t['Plays/G AG'] = pd.to_numeric(df_t['Plays/G AG'], errors='coerce')
    df_t['Pass %/G AG'] = pd.to_numeric(df_t['Pass %/G AG'], errors='coerce')
    df_t['Rush %/G AG'] = pd.to_numeric(df_t['Rush %/G AG'], errors='coerce')
    df_t['Rush %/G AG'] = pd.to_numeric(df_t['Rush %/G AG'], errors='coerce')
    df_t['DKPt Against RB'] = pd.to_numeric(df_t['DKPt Against RB'], errors='coerce')
    df_t['DKPt Against WR'] = pd.to_numeric(df_t['DKPt Against WR'], errors='coerce')
    df_t['DKPt Against QB'] = pd.to_numeric(df_t['DKPt Against QB'], errors='coerce')
    df_t['DKPt Against TE'] = pd.to_numeric(df_t['DKPt Against TE'], errors='coerce')

    df_t.fillna(0, inplace=True)

    return df_t

def make_team_sheet(opp_stats):
    df_t = opp_stats
    games_for_cur_round = find_matchups()

    df_team = df_t.copy()

    df_t = pd.merge(df_t, games_for_cur_round[['Home Team abb', 'Away Team abb']], left_on='Team', right_on='Home Team abb', how='left')

    df_t = pd.merge(df_t, games_for_cur_round[['Home Team abb', 'Away Team abb']], left_on='Team', right_on='Away Team abb', how='left')

    df_t['Home Team abb'] = df_t['Home Team abb_x'].combine_first(df_t['Home Team abb_y'])
    df_t['Away Team abb'] = df_t['Away Team abb_x'].combine_first(df_t['Away Team abb_y'])

    df_t.drop(columns=['Home Team abb_x', 'Home Team abb_y', 'Away Team abb_x', 'Away Team abb_y'], inplace=True)

    df_t['Opponent Team abb'] = np.where(df_t['Home Team abb'] == df_t['Team'], df_t['Away Team abb'], df_t['Home Team abb'])

    df_t.drop(columns=['Home Team abb', 'Away Team abb'], inplace=True)
    df_t.rename(columns={'Opponent Team abb': 'Weekly Opponent'}, inplace=True)
    
    df_team['Team'] = df_team['Team'].map(team_full_to_abb).fillna(df_team['Team'])

    df_final = pd.merge(df_t, df_team, left_on='Weekly Opponent', right_on='Team', how='left')

    df_final.rename(columns={'Team_x': 'Team'}, inplace=True)
    df_final.drop(columns=['Team_y'], inplace=True)

    for col in df_final.columns:
        if '_x' in col:
            df_final.rename(columns={col: col.replace('_x', '')}, inplace=True)
        if '_y' in col:
            df_final.rename(columns={col: col.replace('_y', '')}, inplace=True)
    return df_final