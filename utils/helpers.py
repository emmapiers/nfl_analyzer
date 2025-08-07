import os 
from datetime import datetime
from .dates import round_to_date
from .teams import team_full_to_abb
import pandas as pd

def clean(value):
    '''Strip value'''
    return value.getText().strip()

def per_game(num, denom):
    '''Return per game stat'''
    return round(int(num) / denom, 1)

def percentage(num, denom):
    '''Convert stat to a percentage'''
    return round((num / denom) *100, 1)

def get_round_by_date(date_str):
    '''Get the nfl round based on current date'''
    input_date = datetime.strptime(date_str, '%Y-%m-%d')
    for round_num, (start_date_str, end_date_str) in round_to_date.items():
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        if start_date <= input_date <= end_date:
            return round_num
        
    #if before the first round
    return 0

def get_output_path(filename):
    '''Get the absolute path for the output file in the program's directory'''
    program_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(program_dir, "output")
    
    #make sure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    return os.path.join(output_dir, filename)

def find_matchups():
    '''Get matchup for this week based on current date'''
    relative_path = os.path.join('data', 'nfl-2025-UTC.xlsx')
    base_path = os.path.abspath(".")
    schedule_file = os.path.join(base_path, relative_path)

    try:
        schedule = pd.read_excel(schedule_file)
    except FileNotFoundError as e:
        print(f"Error: {e}")

    schedule['Home Team abb'] = schedule['Home Team'].map(team_full_to_abb)
    schedule['Away Team abb'] = schedule['Away Team'].map(team_full_to_abb)

    current_date = datetime.now().strftime('%Y-%m-%d')
    current_round = get_round_by_date(current_date)
  
    games_for_cur_round = schedule[schedule['Round Number'] == current_round]

    return games_for_cur_round

def normalize_player_name(player_name):
    '''Standardize specific player names that differ across web pages'''
    name_corrections = {
        "DJ Chark Jr.": "DJ Chark",
        "Scotty Miller": "Scott Miller",
        "Deebo Samuel Sr.": "Deebo Samuel",
        "Mecole Hardman Jr.": "Mecole Hardman",
        "Steven Sims Jr.": "Steven Sims",
        "Trent Sherfield Sr.": "Trent Sherfield",
        "James Proche II": "James Proche",
        "Gabe Davis": "Gabriel Davis",
        "Ray-Ray McCloud III": "Ray-Ray McCloud",
        "DeMario Douglas": "Demario Douglas",
        "Andrew Beck": None,
        "DK Metcalf": "D.K. Metcalf",
        "Chig Okonkwo": "Chigoziem Okonkwo",
        "Donald Parham Jr.": "Donald Parham",
        "Calvin Austin III": "Calvin Austin",
        "Taysom Hill": None,
        "John Metchie III": "John Metchie",
        "Allen Robinson II": "Allen Robinson",
        "Marvin Mims Jr.": "Marvin Mims",
        "Drew Ogletree": "Andrew Ogletree",
        "DJ Moore": "David Moore", 
        "Richie James Jr.": "Richie James", 
        "Marvin Jones Jr.": "Marvin Jones", 
        "Joshua Palmer": "Josh Palmer"
    }
    if player_name in name_corrections:
        normalized_name = name_corrections[player_name]
    else:
        normalized_name = player_name

    return normalized_name

def convert_tm_percentage(value):
    '''Error check value before trying to convert to float'''
    if not value or value == 'N/A':
        return 0.0 
    try:
        return float(value.replace("%", "").strip()) 
    except ValueError:
        return 0.0 
