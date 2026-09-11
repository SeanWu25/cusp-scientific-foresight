import requests
import pandas as pd
import time
import xml.etree.ElementTree as ET

def fetch_full_cell_articles():
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    # We use a strict query to target 'Journal Article' and exclude 'Editorial'
    # This filters out most previews at the API level
    query = ('"Cell"[Journal] AND "journal article"[Publication Type] '
             'NOT "editorial"[Publication Type] '
             'AND ("2024"[Date - Publication] : "3000"[Date - Publication])')
    
    search_url = f"{base_url}esearch.fcgi?db=pubmed&term={query}&retmax=1000&usehistory=y"
    response = requests.get(search_url)
    root = ET.fromstring(response.content)
    id_list = [id_elem.text for id_elem in root.findall(".//Id")]
    
    print(f"Found {len(id_list)} potential full articles. Verifying metadata...")
    
    articles_data = []
    
    for i in range(0, len(id_list), 100):
        batch = id_list[i:i+100]
        ids = ",".join(batch)
        fetch_url = f"{base_url}efetch.fcgi?db=pubmed&id={ids}&retmode=xml"
        
        max_retries = 5
        details_root = None
        for attempt in range(max_retries):
            try:
                details_resp = requests.get(fetch_url, timeout=30)
                details_root = ET.fromstring(details_resp.content)
                break
            except (requests.exceptions.ChunkedEncodingError, requests.exceptions.ConnectionError, ET.ParseError) as e:
                print(f"Error fetching batch (attempt {attempt+1}/{max_retries}): {e}")
                time.sleep(2)
        
        if details_root is None:
            print("Failed to fetch batch after all retries, skipping.")
            continue
        
        for article in details_root.findall(".//PubmedArticle"):
            # 1. CHECK PUBLICATION TYPE
            # We look for 'Journal Article' and ensure it's not a 'Review' or 'Editorial' if you want pure research
            pub_types = [pt.text for pt in article.findall(".//PublicationType")]
            
            # If it's a preview or news piece, we skip it
            print(pub_types)

            #this should be if its anything other than JUST 'Journal Article' skip it
            if len(pub_types) != 1 or pub_types[0] != "Journal Article":
                continue

            # 2. EXTRACT FULL ABSTRACT
            # This logic captures all segments of a multi-part research abstract
            abstract_parts = []
            for elem in article.findall(".//AbstractText"):
                label = elem.get('Label')
                text = elem.text if elem.text else ""
                abstract_parts.append(f"{label}: {text}" if label else text)
            
            full_abstract = " ".join(abstract_parts).strip()
            
            # 3. VERIFY IT ISN'T A SNIPPET
            # Full research articles in Cell almost always have abstracts > 500 chars
            if len(full_abstract) < 200: 
                continue

            # 4. EXTRACT DATE & DOI
            year = article.find(".//PubDate/Year")
            month = article.find(".//PubDate/Month")
            date_str = f"{year.text if year is not None else ''}-{month.text if month is not None else ''}"
            
            doi_elem = article.find(".//ArticleId[@IdType='doi']")
            if doi_elem is None:
                continue # Skip if no DOI (usually means it's not a full paper)
                
            link = f"https://doi.org/{doi_elem.text}"
            
            articles_data.append({
                "date_published": date_str,
                "abstract": full_abstract,
                "link": link
            })
        
        time.sleep(0.5) # API Safety

    df = pd.DataFrame(articles_data)
    df.to_csv("cell_full_research_only.csv", index=False)
    print(f"Success! Saved {len(df)} full research articles.")

if __name__ == "__main__":
    fetch_full_cell_articles()