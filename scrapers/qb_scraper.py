from .urls import qb_passing_url
from .base_scraper import get_soup, get_headers_and_rows
from utils.helpers import clean, per_game

def scrape_qb():
    soup = get_soup(qb_passing_url)
    headers, rows = get_headers_and_rows(soup, "passing", False)

    position_index = headers.index("Pos")

    stats = []
    
    for row in rows[:-1]:
        columns = row.find_all('td')
        column_offset = len(columns) - len(headers)

        if columns:
            position = clean(columns[position_index+column_offset])
            if position != 'QB':
                continue

            games_played = int(clean(columns[headers.index("G")+column_offset]))
            team = str(clean(columns[headers.index("Team")+column_offset]))
            player = clean(columns[headers.index("Player")+column_offset])
            completions = int(clean(columns[headers.index("Cmp")+column_offset]))
            attempts = int(clean(columns[headers.index("Att")+column_offset]))
            yards = int(clean(columns[headers.index("Yds")+column_offset]))
            td = int(clean(columns[headers.index("TD")+column_offset]))
            td_percent = clean(columns[headers.index("TD%")+column_offset])
            yards_per_attempt = clean(columns[headers.index("Y/A")+column_offset])

            stats.append({
                "Player": player, 
                "Team": team,
                "Cmp/G": str(per_game(completions, games_played)), 
                "Att/G": str(per_game(attempts, games_played)), 
                "Yds/G": str(per_game(yards, games_played)), 
                "TD/G": str(per_game(td, games_played)), 
                "TD%": str(td_percent), 
                "Y/A": str(yards_per_attempt)
            })
            
    return stats
