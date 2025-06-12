from .urls import wr_te_receiving_url
from .base_scraper import get_headers_and_rows, get_soup
from utils.helpers import clean, per_game

def scrape_receiving():
    soup = get_soup(wr_te_receiving_url)
    headers, rows = get_headers_and_rows(soup, "receiving", False)

    wr_te_stats = []
    rb_stats = []

    for row in rows[:-1]:
        columns = row.find_all('td')
        column_offset = len(columns) - len(headers)

        if columns:
            player = clean(columns[headers.index("Player")+column_offset]).rstrip('*+')
            position = clean(columns[headers.index("Pos")+column_offset])

            team = str(clean(columns[headers.index("Team")+column_offset]))
            games_played = int(clean(columns[headers.index("G")+column_offset]))
            targets = int(clean(columns[headers.index("Tgt")+column_offset]))
            yards_per_target = clean(columns[headers.index("Y/R") + column_offset])
            receptions_per_game = clean(columns[headers.index("R/G") + column_offset])
            yards_per_game = clean(columns[headers.index("Y/G") + column_offset])
            tds = int(clean(columns[headers.index("TD") + column_offset]))

            stats = {
                "Player": player, 
                "Team": str(team),
                "Tgt/G": str(per_game(targets, games_played)),
                "Y/R": str(yards_per_target), 
                "R/G": str(receptions_per_game), 
                "Y/G": str(yards_per_game), 
                "TD/G": str(round(tds / games_played, 3))
            }
            
            if position in ["WR", "TE"]:
                stats["Position"] = str(position)  
                wr_te_stats.append(stats)
            elif position in ["RB"]:
                rb_stats.append(stats)

    return wr_te_stats, rb_stats
