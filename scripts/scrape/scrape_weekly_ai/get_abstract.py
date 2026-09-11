import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import time

def get_abstract(url):
    """
    Attempts to scrape the abstract from the arXiv summary page.
    Returns the abstract text if found, or None if it fails.
    """
    try:
        # arXiv links can sometimes be /pdf/ links; we need the /abs/ version for HTML scraping
        clean_url = url.replace('/pdf/', '/abs/').replace('.pdf', '')
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(clean_url, timeout=10)
        res.raise_for_status()
        
        soup = BeautifulSoup(res.text, 'html.parser')
        abs_tag = soup.find('blockquote', class_='abstract')
        
        if abs_tag:
            # Clean up the "Abstract:" label and extra whitespace
            return abs_tag.get_text(strip=True).replace('Abstract:', '', 1).strip()
    except Exception:
        pass # If connection fails or URL is bad, we just return None
    
    return None


# --- Run the Script ---
df = pd.read_csv('ai_papers_top_ai_arixv.csv')

# Use a list to store rows that actually have abstracts
valid_rows = []

print(f"Starting extraction. Filtering out papers without abstracts...")

for index, row in tqdm(df.iterrows(), total=len(df), desc="Scraping arXiv"):
    abstract_text = get_abstract(row['paper_link'])
    
    if abstract_text:
        # Create a copy of the row data and add the new abstract column
        new_row = row.to_dict()
        new_row['abstract'] = abstract_text
        valid_rows.append(new_row)
    
    # Polite delay to stay under arXiv's radar
    time.sleep(1.0)

# Convert the list of successful dictionaries back into a DataFrame
df_final = pd.DataFrame(valid_rows)

# Save the results
df_final.to_csv('ai_papers_final_cleaned.csv', index=False)

print(f"\nDone! Processed {len(df)} papers and kept {len(df_final)} with valid abstracts.")