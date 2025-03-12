import undetected_chromedriver as uc
import time
import pickle
import os
import json
import random
import ast
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

cookies_file = "cookies.pkl"

def login_and_save_cookies():
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options)
    driver.get("https://yourstory.com/login")
    print("Please log in manually within the next 40 seconds...")
    time.sleep(40)
    with open(cookies_file, "wb") as f:
        pickle.dump(driver.get_cookies(), f)
    print("Cookies saved successfully!")
    driver.quit()

if not os.path.exists(cookies_file):
    login_and_save_cookies()

def create_driver(headless=True):
    options = uc.ChromeOptions()
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = uc.Chrome(options=options)
    driver.get("https://yourstory.com")
    time.sleep(5)
    with open(cookies_file, "rb") as f:
        cookies = pickle.load(f)
        for cookie in cookies:
            if "sameSite" in cookie:
                cookie.pop("sameSite")
            driver.add_cookie(cookie)
    driver.refresh()
    time.sleep(5)
    return driver

def get_excerpt(driver, link):
    """Given an article URL, visit the page and return the excerpt text."""
    try:
        driver.get(link)
        time.sleep(random.uniform(2, 3))
        soup_article = BeautifulSoup(driver.page_source, "html.parser")
        meta_desc = soup_article.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            return meta_desc["content"].strip()
        article_tag = soup_article.find("article")
        if article_tag:
            p_tag = article_tag.find("p")
            if p_tag:
                return p_tag.get_text(strip=True)
        return ""
    except Exception as e:
        print(f"Error scraping excerpt from {link}: {e}")
        return ""

def scrape_yourstory(driver, query, page=1):
    results = []
    search_url = f"https://yourstory.com/search?q={query}&page={page}"
    print(f"\nScraping URL: {search_url}")
    try:
        driver.get(search_url)
        time.sleep(random.uniform(5, 8))
        # Scroll down to load dynamic content
        for _ in range(3):
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
            time.sleep(random.uniform(2, 4))
        soup = BeautifulSoup(driver.page_source, "html.parser")
        container = soup.find("section", class_="container-results")
        if not container:
            print("No container-results found on the page.")
            return results

        article_items = container.select("li.sc-c9f6afaa-0")
        if not article_items:
            print("No article items found in container.")
            return results

        for item in article_items:
            a_tags = item.find_all("a", href=True)
            title = None
            link = None
            for a in a_tags:
                span = a.find("span")
                if span:
                    text = span.get_text(strip=True)
                    if text:
                        title = text
                        link = a["href"]
                        break

            if link and link.startswith("/"):
                link = "https://yourstory.com" + link

            date_tag = item.find("span", class_="sc-36431a7-0 dpmmXH")
            date = date_tag.get_text(strip=True) if date_tag else None

            cat_container = item.select_one("div.sc-c9f6afaa-10.jqCVBY span")
            category = cat_container.get_text(strip=True) if cat_container else None

            excerpt = get_excerpt(driver, link) if link else ""
            results.append({
                "title": title,
                "link": link,
                "date": date,
                "category": category,
                "excerpt": excerpt
            })
            print(f"Scraped entry - Title: {title}")
    except Exception as e:
        print(f"Error scraping page {page} for query '{query}': {e}")
    return results

def save_results(all_results, filename="yourstory_funders_companies_results.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=4)
    print("File saved to", filename)

def main():
    # Load companies and founders data from JSON
    with open("founders_companies.json", "r", encoding="utf-8") as f:
        companies_data = json.load(f)

    # Build a set of unique queries from company names and founder names.
    queries = set()
    for record in companies_data:
        if "Company" in record and record["Company"]:
            queries.add(record["Company"])
        if "Founders" in record and record["Founders"]:
            try:
                founders_list = ast.literal_eval(record["Founders"])
                for founder in founders_list:
                    queries.add(founder)
            except Exception as e:
                print(f"Error parsing founders for {record.get('Company', 'Unknown')}: {e}")

    print(f"Total unique queries to scrape: {len(queries)}")
    driver = create_driver(headless=True)
    all_results = {}
    entry_count = 0

    # Loop over each query and scrape data.
    for query in queries:
        print(f"\n--- Scraping results for query: '{query}' ---")
        all_results[query] = []  # initialize results for this query
        for page in range(1, 2):  # You can increase the page range if needed.
            data = scrape_yourstory(driver, query, page)
            for entry in data:
                all_results[query].append(entry)
                entry_count += 1
                print(f"Total entries scraped so far: {entry_count}")
                if entry_count % 2 == 0:
                    save_results(all_results)
    # Final save of results
    save_results(all_results)
    print("\nScraping completed. Total entries scraped:", entry_count)
    driver.quit()

if __name__ == "__main__":
    main()
