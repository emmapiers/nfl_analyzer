from .urls import team_defense_url
from .base_scraper import get_headers_and_rows, get_soup
from utils.helpers import clean, per_game, percentage
from utils.teams import team_full_to_abb

def scrape_team_defense():
    soup = get_soup(team_defense_url)
    headers, rows = get_headers_and_rows(soup, 'team_stats', True)

    stats = []

    for row in rows[:-3]:
        columns = row.find_all('td')
        column_offset = len(columns) - len(headers)
        
        if columns:
            team = clean(columns[0])
            abb_name = team_full_to_abb.get(team, team)

            games_played = int(clean(columns[headers.index("G")+column_offset]))
            plays = int(clean(columns[headers.index("Ply")+column_offset]))
            passes = int(clean(columns[headers.index("Att")+column_offset]))
            rushes = int(clean(columns[headers.index("Att", headers.index("Att") + 1)+column_offset])) #second occurence

            plays_per_game = per_game(plays, games_played)
            passes_per_game = per_game(passes, games_played)
            pass_percentage_per_game = percentage(passes_per_game, plays_per_game) 
            rushes_per_game = per_game(rushes, games_played)
            rushes_percentage_per_game = percentage(rushes_per_game, plays_per_game)

            stats.append({
                "Team": abb_name, 
                "Plays/G AG": float(plays_per_game), 
                "Pass %/G AG": float(pass_percentage_per_game), 
                "Rush %/G AG": float(rushes_percentage_per_game)
                })
    return stats
