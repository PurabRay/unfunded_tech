import requests
from bs4 import BeautifulSoup
import json
import time
import random
import pandas as pd
import os
import ast

def get_article_excerpt(link):
    """
    Given an article URL, fetch the page and try to extract its excerpt.
    First, look for a meta description. If not found, try grabbing the first paragraph
    from a container with class "article-content".
    """
    try:
        print(f"Fetching excerpt from: {link}")
        response = requests.get(link)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
       
        meta_desc = soup.find("meta", {"name": "description"})
        if meta_desc and meta_desc.get("content"):
            return meta_desc["content"].strip()
        
        article_body = soup.find("div", class_="article-content")
        if article_body:
            p_tag = article_body.find("p")
            if p_tag:
                return p_tag.get_text(strip=True)
        return ""
    except Exception as e:
        print(f"Error fetching excerpt from {link}: {e}")
        return ""

def scrape_techcrunch(query):
    """
    Scrape TechCrunch for articles related to the given query.
    """
    url = f"https://techcrunch.com/?s={query}"
    print(f"Scraping URL: {url}")
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    results_ul = soup.find('ul', class_='wp-block-post-template')
    if not results_ul:
        print(f"No results found for query: {query}")
        return []
    
    results = []
    for li in results_ul.find_all('li', recursive=False):
        card = li.find('div', class_='wp-block-techcrunch-card')
        if not card:
            continue
        
        loop_card = card.find('div', class_='loop-card')
        if not loop_card:
            continue
        
        image_url = "N/A"
        figure = loop_card.find('figure', class_='loop-card__figure')
        if figure:
            img = figure.find('img')
            if img and img.get('src'):
                image_url = img.get('src')
        
        content_div = loop_card.find('div', class_='loop-card__content')
        if not content_div:
            continue
        
        category = "N/A"
        cat_group = content_div.find('div', class_='loop-card__cat-group')
        if cat_group:
            cat_tag = cat_group.find(['a', 'span'], class_='loop-card__cat')
            if cat_tag:
                category = cat_tag.get_text(strip=True)
        
        title = "N/A"
        link = "N/A"
        h3 = content_div.find('h3', class_='loop-card__title')
        if h3:
            a_tag = h3.find('a', class_='loop-card__title-link')
            if a_tag:
                title = a_tag.get_text(strip=True)
                link = a_tag.get('href')
        
        author = "N/A"
        meta_div = content_div.find('div', class_='loop-card__meta')
        if meta_div:
            author_list = meta_div.find('ul', class_='loop-card__meta-item')
            if author_list:
                author_links = author_list.find_all('a', class_='loop-card__author')
                if author_links:
                    authors = [a.get_text(strip=True) for a in author_links]
                    author = ", ".join(authors)
        
        date = "N/A"
        time_tag = content_div.find('time')
        if time_tag:
            date = time_tag.get_text(strip=True)
        
        excerpt = ""
        if link != "N/A":
            excerpt = get_article_excerpt(link)
            
        article_data = {
            "title": title,
            "link": link,
            "date": date,
            "category": category,
            "author": author,
            "image": image_url,
            "excerpt": excerpt
        }
        results.append(article_data)
    
    return results

def load_json_data(json_filepath):
    """
    Load JSON data from the given filepath.
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
    checkpoint_filename = "techcrunch_articles_checkpoint.json"
    try:
        with open(checkpoint_filename, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        print(f"Checkpoint updated: {checkpoint_filename}")
    except Exception as e:
        print(f"Error saving checkpoint: {e}")

def is_relevant(article, query):
    """
    Determine if an article is relevant to the query.
    Checks if the query appears in the title or excerpt (case-insensitive).
    """
    query_lower = query.lower()
    title = article.get("title", "").lower()
    excerpt = article.get("excerpt", "").lower()
    return query_lower in title or query_lower in excerpt

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
    
   
    if 'Company' in df.columns:
        companies = df['Company'].dropna().unique().tolist()
        queries.update([company.strip() for company in companies if company.strip()])
    else:
        print("Column 'Company' not found in JSON data.")
    
    queries = [q for q in queries if q]
    print(f"Total unique queries to search (Founders & Companies): {len(queries)}")

    all_results = {}
    processed_count = 0

    
    save_checkpoint(all_results)

    for query in queries:
        print(f"\n--- Scraping results for query: '{query}' ---")
        try:
            articles = scrape_techcrunch(query)
            if articles:
                relevant_articles = [article for article in articles if is_relevant(article, query)]
                if relevant_articles:
                    all_results[query] = relevant_articles
        except Exception as e:
            print(f"Error processing query '{query}': {e}")
        
        processed_count += 1
        
        
        if processed_count % 2 == 0:
            save_checkpoint(all_results)
        
        
    
    
    save_checkpoint(all_results)
    
    articles_json_filepath = "techcrunch_articles_checkpoint.json"
    try:
        with open(articles_json_filepath, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=4)
        print(f"Articles results saved to {articles_json_filepath}")
    except Exception as e:
        print(f"Error saving final results: {e}")

if __name__ == "__main__":
    main()
