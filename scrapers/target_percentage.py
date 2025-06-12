import requests 
from bs4 import BeautifulSoup as bs
import re
from .urls import wr_fantasy_url, te_fantasy_url

def get_tp(url, position):
    response = requests.get(url)
    soup = bs(response.content, 'html.parser')

    table = soup.find('table', {'id': 'data'})

    stats = []

    if table:
        headers = [th.get_text(strip=True) for th in table.find_all('th')]

        for row in table.find_all('tr')[1:]: 
            columns = row.find_all('td')

            if columns:
                player = columns[1].get_text(strip=True)
                cleaned_player = re.sub(r'\(.*?\)', '', player).strip() 
                tm_percentage = columns[headers.index("% TM")].get_text(strip=True)
                
                stats.append({
                    "Player": cleaned_player,
                    "Position": position,
                    "TM %": tm_percentage
                })
    return stats

def scrape_target_percentage():
    wr_stats = get_tp(wr_fantasy_url, "WR")
    te_stats = get_tp(te_fantasy_url, "TE")
    return wr_stats + te_stats