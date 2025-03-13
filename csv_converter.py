import pandas as pd
import json

json_files = {
    "reddit_scraped_data.json": "reddit.csv",
    "techcrunch_articles_checkpoint.json": "techcrunch.csv",
    "inc42_results.json": "inc42.csv",
    "yourstory_funders_companies_results.json": "YourStory.csv",
    "factordaily_results.json": "factordaily.csv"
}

for json_file, csv_file in json_files.items():
    try:
        
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        
        df = pd.json_normalize(data)

        
        df.to_csv(csv_file, index=False)
        print(f"CSV file saved as {csv_file}")

    except Exception as e:
        print(f"Error processing {json_file}: {e}")
