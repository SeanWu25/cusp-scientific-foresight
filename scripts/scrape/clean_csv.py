import pandas as pd
import glob
import os

def clean_all_in_folder():
    # Find all CSV files in the current directory
    csv_files = glob.glob("*.csv")
    
    if not csv_files:
        print("No CSV files found in this folder.")
        return

    print(f"Found {len(csv_files)} files. Starting cleanup...\n")

    for file_path in csv_files:
        try:
            # Load the CSV
            df = pd.read_csv(file_path)
            initial_count = len(df)

            # Check if 'abstract' column exists
            if 'abstract' in df.columns:
              #  print(f"Skipping {file_path}: No 'abstract' column found.")
                
                # Remove rows where abstract is NaN or empty/whitespace
                df_cleaned = df.dropna(subset=['abstract'])
                df_cleaned = df_cleaned[df_cleaned['abstract'].astype(str).str.strip() != '']
            #also filter out all the abstracts that are less than 100 characters
                df_cleaned = df_cleaned[df_cleaned['abstract'].astype(str).str.len() >= 100]
          
          
            if 'paper_link' in df.columns:
                df_cleaned = df.dropna(subset=['paper_link'])
                df_cleaned = df_cleaned[df_cleaned['paper_link'].astype(str).str.strip() != '']
#help make this more robust for 'link' column name
            if 'link' in df.columns:
                df_cleaned = df.dropna(subset=['link'])
                df_cleaned = df_cleaned[df_cleaned['link'].astype(str).str.strip() != '']
            if 'date_published' in df.columns:
                df_cleaned = df.dropna(subset=['date_published'])
                df_cleaned = df_cleaned[df_cleaned['date_published'].astype(str).str.strip() != '']

            if 'Date Published' in df.columns:
                print("reached")
                df_cleaned = df.dropna(subset=['Date Published'])
                df_cleaned = df_cleaned[df_cleaned['Date Published'].astype(str).str.strip() != '']
            final_count = len(df_cleaned)
            
            # Save back to the same path
            df_cleaned.to_csv(file_path, index=False)

            print(f"Processed: {file_path}")
            print(f"  - Removed {initial_count - final_count} rows.")
            print(f"  - Remaining: {final_count} rows.\n")

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    clean_all_in_folder()
    print("All files processed.")
