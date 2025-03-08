import praw
import json
import os
import ast
import time
import random


with open("founders_companies.json", "r", encoding="utf-8") as f:
    startup_data = json.load(f)


search_queries = []

for entry in startup_data:
    # Add company name if present
    if "Company" in entry:
        company = entry["Company"].strip()
        if company:
            search_queries.append(company)
    
    
    if "Founders" in entry:
        founders_field = entry["Founders"].strip()
        # If the field looks like a list (e.g., "['Alice', 'Bob']")
        if founders_field.startswith('[') and founders_field.endswith(']'):
            try:
                founders = ast.literal_eval(founders_field)
                if isinstance(founders, list):
                    for founder in founders:
                        if founder and isinstance(founder, str):
                            search_queries.append(founder.strip())
                        elif founder:
                            search_queries.append(str(founder).strip())
                else:
                    search_queries.append(str(founders).strip())
            except Exception as e:
                print(f"Error parsing Founders for entry {entry}: {e}")
                
                for founder in founders_field.split(','):
                    if founder.strip():
                        search_queries.append(founder.strip())
        else:
            
            for founder in founders_field.split(','):
                if founder.strip():
                    search_queries.append(founder.strip())


search_queries = list(set(search_queries))
print(f"Total unique queries to search: {len(search_queries)}")


reddit = praw.Reddit(
    client_id="beTKjKraeFN1liBYyCg9-Q",
    client_secret="HFRJS0_0Hgx7FnNG8MFunNkQcyJJUA",
    user_agent="MyRedditScraper/1.0"
)


def scrape_reddit(queries, limit=3):
    scraped_results = []
    processed_count = 0
    total_queries = len(queries)
    checkpoint_file = "reddit_scraped_data.json"
    
    for query in queries:
        print(f"Scraping Reddit for: {query} ({processed_count+1}/{total_queries})")
        search_results = []
        try:
            for submission in reddit.subreddit("all").search(query, limit=limit):
                search_results.append({
                    "title": submission.title,
                    "url": submission.url,
                    "score": submission.score,
                    "comments": submission.num_comments
                })
        except Exception as e:
            print(f"Error scraping query '{query}': {e}")
        
        scraped_results.append({"query": query, "results": search_results})
        processed_count += 1
        
        
        if processed_count % 5 == 0:
            with open(checkpoint_file, "w", encoding="utf-8") as f:
                json.dump(scraped_results, f, ensure_ascii=False, indent=4)
            print(f"Checkpoint saved after {processed_count} queries.")
            
            
    
    return scraped_results

# Run Reddit scraper with a limit of 5 submissions per query
scraped_data = scrape_reddit(search_queries, limit=5)

# Save final results to a JSON file
with open("reddit_scraped_data.json", "w", encoding="utf-8") as f:
    json.dump(scraped_data, f, ensure_ascii=False, indent=4)

print("Scraping complete. Data saved in 'reddit_scraped_data.json'.")
