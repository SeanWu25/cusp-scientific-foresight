import requests
import pandas as pd
from datetime import datetime, timedelta
import time

def get_science_research_articles(years=2):
    start_date = (datetime.now() - timedelta(days=years*365)).strftime('%Y-%m-%d')
    email = "your-email@example.com" 
    
    base_url = "https://api.openalex.org/works"
    
    # NEW FILTER ADDED: is_paratext:false 
    # This removes table of contents, covers, editorials, etc.
    params = {
        'filter': f'primary_location.source.issn:0036-8075,from_publication_date:{start_date},type:article,is_paratext:false',
        'select': 'display_name,publication_date,abstract_inverted_index,doi,type',
        'per_page': 200,
        'cursor': '*',
        'mailto': email
    }

    all_articles = []
    page_count = 1

    print(f"🚀 Extracting ORIGINAL RESEARCH from Science since {start_date}...")

    while True:
        try:
            response = requests.get(base_url, params=params)
            if response.status_code != 200:
                print(f"❌ Error {response.status_code}")
                break
            
            data = response.json()
            results = data.get('results', [])
            if not results: break

            for res in results:
                abstract_index = res.get('abstract_inverted_index')
                
                # RESEARCH FILTER: 
                # Original research almost ALWAYS has an abstract in OpenAlex for Science.
                # News and Editorials often do not.
                if not abstract_index:
                    continue

                # Reconstruct Abstract
                word_positions = []
                for word, pos_list in abstract_index.items():
                    for pos in pos_list:
                        word_positions.append((pos, word))
                word_positions.sort()
                abstract_text = " ".join([word for pos, word in word_positions])

                # Final check: Science Research Articles usually have longer abstracts.
                # This helps filter out short "In Brief" or "Summary" clips.
                if len(abstract_text.split()) < 50:
                    continue

                all_articles.append({
                    "Date Published": res.get('publication_date'),
                    "Title": res.get('display_name'),
                    "Abstract": abstract_text,
                    "Paper Link": f"https://doi.org/{res.get('doi')}" if res.get('doi') else "N/A"
                })

            print(f"✅ Page {page_count}: Found {len(all_articles)} research papers...")
            params['cursor'] = data.get('meta', {}).get('next_cursor')
            page_count += 1
            time.sleep(0.1) 

        except Exception as e:
            print(f"⚠️ Error: {e}")
            break

    if all_articles:
        df = pd.DataFrame(all_articles)
        df['Date Published'] = pd.to_datetime(df['Date Published'])
        df = df.sort_values(by="Date Published", ascending=False)
        df.to_csv(f"science_research_{datetime.now().year}.csv", index=False)
        print(f"🎉 Success! {len(df)} research articles saved.")

if __name__ == "__main__":
    get_science_research_articles()