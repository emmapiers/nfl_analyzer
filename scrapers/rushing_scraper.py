from .urls import player_rushing_url
from .base_scraper import get_headers_and_rows, get_soup
from utils.helpers import clean, per_game

def scrape_rushing():
    soup = get_soup(player_rushing_url)
    headers, rows = get_headers_and_rows(soup, "rushing", False)

    rb_stats = []
    qb_stats = []

    for row in rows[:-1]:
        columns = row.find_all('td')
        column_offset = len(columns) - len(headers)

        rb_stats = []
        qb_stats = []

        if columns:
            player = clean(columns[headers.index("Player")+column_offset]).rstrip('*+')
            position = clean(columns[headers.index("Pos")+column_offset])

            team = str(clean(columns[headers.index("Team")+column_offset]))
            attempts = int(clean(columns[headers.index("Att")+column_offset]))
            yards_per_att = clean(columns[headers.index("Y/A")+column_offset])

            stats = {
                "Player": player, 
                "Team": str(team), 
                "Att": str(attempts), 
                "Yds/Carry": str(yards_per_att)
            }

            if position == "RB":
                games_played = int(clean(columns[headers.index("G")+column_offset]))
                td = int(clean(columns[headers.index("TD")+column_offset]))

                if (td == 0):
                    tds_per_game = 0.0
                else:
                    tds_per_game = per_game(attempts, td)

                stats["Att/G"] = str(per_game(attempts, games_played))
                stats["TD%"] = str(tds_per_game)
                rb_stats.append(stats)
            elif position == "QB":
                rb_stats.append(stats)
            
    return rb_stats, qb_stats