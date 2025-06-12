from .urls import team_rushing_url
from .base_scraper import get_headers_and_rows, get_soup
from utils.helpers import clean

def scrape_team_rushing():
    soup = get_soup(team_rushing_url)
    headers, rows = get_headers_and_rows(soup, "all_rushing", False)

    stats = []
    for row in rows[:-1]:
        columns = row.find_all('td')
        column_offset = len(columns) - len(headers)
   
        if columns:
            team = str(clean(columns[headers.index("Tm")+column_offset]))
            attempts = int(clean(columns[headers.index("Att")+column_offset]))
            
            stats.append({
                "Team": team, 
                "Att": int(attempts)
            })
            
    return stats
