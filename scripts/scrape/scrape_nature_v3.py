"""
scrape_nature_v3.py — Fetch Nature research-article metadata via the Springer
Nature Meta API.

Requires a (free) Springer Nature API key: https://dev.springernature.com/
Set it as the SPRINGER_API_KEY environment variable (or in a .env file).
"""

import os

import requests
import pandas as pd
import time

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# --- CONFIGURATION ---
API_KEY = os.getenv("SPRINGER_API_KEY")
if not API_KEY:
    raise RuntimeError("Set SPRINGER_API_KEY in your environment or .env file")
JOURNAL = "Nature"
START_DATE = "2024-01-01"  # Adjust for past 2 years
END_DATE = "2026-02-27"
RESULTS_PER_PAGE = 50
# ---------------------

def fetch_nature_articles():
    base_url = "https://api.springernature.com/meta/v1/json"
    articles = []
    start_index = 1
    
    # Filter: journal:Nature + type:Article + date range
    query = f"journal:{JOURNAL} type:Article ondateafter:{START_DATE} ondatebefore:{END_DATE}"
    
    while True:
        params = {
            "q": query,
            "api_key": API_KEY,
            "p": RESULTS_PER_PAGE,
            "s": start_index
        }
        
        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            break
            
        data = response.json()
        records = data.get("records", [])
        
        if not records:
            break
            
        for rec in records:
            articles.append({
                "date_published": rec.get("publicationDate"),
                "title": rec.get("title"),
                "abstract": rec.get("abstract"),
                "doi": rec.get("doi"),
                "paper_link": rec.get("url")[0].get("value") if rec.get("url") else ""
            })
            
        print(f"Fetched {len(articles)} / {data['result'][0]['total']} articles...")
        
        # Check if we've reached the end
        if len(articles) >= int(data['result'][0]['total']):
            break
            
        start_index += RESULTS_PER_PAGE
        time.sleep(0.5)  # Respect rate limits
        
    return articles

# Run and save
data = fetch_nature_articles()
df = pd.DataFrame(data)
df.to_csv("nature_articles_2024_2026.csv", index=False)
print("Done! File saved as nature_articles_2024_2026.csv")