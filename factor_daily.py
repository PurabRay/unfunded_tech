import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import os
import ast
import time
import random

def scrape_factordaily(query, page=1):
    """
    Scrape Factordaily for articles related to the given query.
    """
    if page == 1:
        url = f"https://factordaily.com/?s={query}"
    else:
        url = f"https://factordaily.com/page/{page}/?s={query}"
    
    print(f"Scraping URL: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch {url}: Status code {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    search_post_list = soup.find("div", class_="search-post-list")
    if not search_post_list:
        print("No search post list found on the page.")
        return []
    
    posts = search_post_list.find_all("div", class_="single")
    results = []
    
    for post in posts:
        image = None
        img_div = post.find("div", class_="img-div")
        if img_div:
            a_img = img_div.find("a")
            if a_img:
                img_tag = a_img.find("img")
                if img_tag and img_tag.has_attr("src"):
                    image = img_tag["src"]
        
        category = None
        cat_div = post.find("div", class_="category-div")
        if cat_div:
            a_cat = cat_div.find("a")
            if a_cat:
                category = a_cat.get_text(strip=True)
        
        title = None
        link = None
        h3 = post.find("h3")
        if h3:
            a_title = h3.find("a")
            if a_title:
                title = a_title.get_text(strip=True)
                link = a_title.get("href")
        
        date = None
        date_div = post.find("div", class_="date")
        if date_div:
            date = date_div.get_text(strip=True)
        
        excerpt = None
        excerpt_div = post.find("div", class_="excerpt")
        if excerpt_div:
            excerpt = excerpt_div.get_text(strip=True)
        
        author = None
        author_div = post.find("div", class_="author-div")
        if author_div:
            a_author = author_div.find("a")
            if a_author:
                author = a_author.get_text(strip=True)
        
        results.append({
            "title": title,
            "link": link,
            "image": image,
            "category": category,
            "date": date,
            "excerpt": excerpt,
            "author": author
        })
    return results

def load_json_data(json_filepath):
    """
    Load JSON data from the specified filepath.
    """
    try:
        with open(json_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Loaded JSON data from {json_filepath}")
        return data
    except Exception as e:
        print(f"Error loading JSON file {json_filepath}: {e}")
        return None

def save_checkpoint(results):
    """
    Save/update a checkpoint file with the current results.
    """
    checkpoint_filename = "factordaily_results.json"
    try:
        with open(checkpoint_filename, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        print(f"Checkpoint updated: {checkpoint_filename}")
    except Exception as e:
        print(f"Error saving checkpoint: {e}")

def main():
    json_filepath = "founders_companies.json"
    
    if not os.path.exists(json_filepath):
        print(f"JSON file {json_filepath} does not exist. Please create it from your CSV first.")
        return
    
    data = load_json_data(json_filepath)
    if data is None:
        return
    
    df = pd.DataFrame(data)
    
    queries = set()
    # Process Founders column: separate out individual names if the entry is a list.
    if 'Founders' in df.columns:
        for entry in df['Founders'].dropna().unique().tolist():
            try:
                founder_list = ast.literal_eval(entry)
                if isinstance(founder_list, list):
                    for name in founder_list:
                        if name:
                            queries.add(name.strip())
                else:
                    queries.add(str(founder_list).strip())
            except Exception as e:
                print(f"Error parsing founders entry: {entry}. Error: {e}")
                queries.add(entry.strip())
    else:
        print("Column 'Founders' not found in JSON data.")
    
    # Process Company column: add each company name as a query.
    if 'Company' in df.columns:
        companies = df['Company'].dropna().unique().tolist()
        for company in companies:
            if company and company.strip():
                queries.add(company.strip())
    else:
        print("Column 'Company' not found in JSON data.")
    
    queries = [q for q in queries if q]
    print(f"Total unique queries to search (Founders & Companies): {len(queries)}")
    
    all_results = {}
    processed_count = 0
    
   
    save_checkpoint(all_results)
    
    for query in queries:
        print(f"\n--- Scraping results for query: '{query}' ---")
        posts = scrape_factordaily(query, page=1)
        if posts:
            all_results[query] = posts
        
        processed_count += 1
        
      
        if processed_count % 2 == 0:
            save_checkpoint(all_results)
            
            
    
    
    save_checkpoint(all_results)
    print("Scraping completed.")

if __name__ == "__main__":
    main()
