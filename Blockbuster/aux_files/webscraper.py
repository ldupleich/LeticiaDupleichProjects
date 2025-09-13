"""
What will most likely happen is that I will combine multiple checkpoints into
the final dataset by running this program over multiple sessions (of course 
adjusting the input dataset 54000_movies_dataset_prelim.csv at start of each session
to ensure that the scraper isn't scraping data already saved in previous session's
checkpoint).

This final merger will occur in the file aux_files/merge_dataset2.py

Checkpoints save scraped data cumulatively per session with 1000 scraped movies between each.
For my laptop, that is one checkpoint per 30 minutes.

Checkpoint naming convention: first digit is session number, second digit is checkpoint number,
i.e. checkpoint2.3 is the third checkpoint of scraping session 2.
"""

# Global variable used for checkpoint session naming. 
CURRENT_SESSION = 5

from bs4 import BeautifulSoup
import pandas as pd
import requests
import json
from tqdm import tqdm

# The webscraping functions were graciously provided by Maria.

def find_first_key(obj, target_key):
    """
    Recursively search through `obj` (which can be a dict, list, or scalar)
    for the first occurrence of `target_key`. Return its value if found, else None.
    """
    if isinstance(obj, dict):
        if target_key in obj:
            return obj[target_key]
        for v in obj.values():
            found = find_first_key(v, target_key)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for item in obj:
            found = find_first_key(item, target_key)
            if found is not None:
                return found
    return None

def extract_gross_worldwide(soup):
    section = soup.find("section", {"data-testid": "BoxOffice"})
    if section:
        for li in section.select("li.ipc-metadata-list__item"):
            label_span = li.find("span", class_="ipc-metadata-list-item__label")
            if label_span and label_span.get_text(strip=True) == "Gross worldwide":
                value_span = li.find("span", class_="ipc-metadata-list-item__list-content-item")
                if value_span:
                    return value_span.get_text(strip=True)
    return ""

def scrape_imdb_to_df(tconst_list, checkpoints = True):
    """
    Fetch each title page from the given tconst list, parse its JSON-LD 
    to extract the first reviewBody (or description) and the first keywords.
    Also scrape the Gross worldwide from the BoxOffice section.
    """
    data_rows = []
    CURRENT_CHECKPOINT = 1
    for i, tconst in enumerate(tqdm(tconst_list)):
        
        # Checkpoint saving to prevent dataloss, creates checkpoints every 1000 movies scraped.
        if checkpoints and ((i != 0) and (((i % 1000) == 0) or (i == len(tconst_list)-1))):
            temp_df = pd.DataFrame(data_rows)
            temp2_df = pd.merge(movie_dataset, temp_df, on = "tconst")
            temp2_df.to_csv(f"../datasets/webscraper_checkpoints/checkpoint{CURRENT_SESSION}.{CURRENT_CHECKPOINT}.csv")
            CURRENT_CHECKPOINT += 1
            
        url = f"https://www.imdb.com/title/{tconst}/"
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            resp = requests.get(url, headers=headers)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
        except Exception:
            # On error, i.e. no internet, finish scraping
            data_rows.append({
                "tconst": tconst,
                "storyline": "",
                "themes": [],
                "director": "",
                "actors": [],
                "gross_worldwide": ""
            })
            continue

        # Extract Gross worldwide
        gross = extract_gross_worldwide(soup)
        
        storyline = ""
        themes = []
        director = ""
        actors = []

        # Locate and parse JSON-LD
        ld_json_tag = soup.find("script", {"type": "application/ld+json"})
        if ld_json_tag and ld_json_tag.string:
            # extra careful steps
            try:
                data = json.loads(ld_json_tag.string)
            except Exception:
                data = {}
            else:
                # STORYLINE
                review_val = find_first_key(data, "reviewBody")
                if review_val:
                    storyline = review_val.strip()

                # THEMES: first max_themes from keywords
                raw_keywords = find_first_key(data, "keywords")
                if isinstance(raw_keywords, str):
                    for kw in raw_keywords.split(","):
                        kw_clean = kw.strip()
                        if kw_clean:
                            themes.append(kw_clean)
                        if len(themes) > 4:
                            break
                elif isinstance(raw_keywords, list):
                    for item in raw_keywords:
                        if isinstance(item, str):
                            themes.append(item.strip())
                        elif isinstance(item, dict) and "name" in item:
                            themes.append(item["name"].strip())
                        if len(themes) > 4:
                            break

                # DIRECTOR: could be a dict or list of dicts
                dir_val = find_first_key(data, "director")
                if isinstance(dir_val, dict):
                    director = dir_val.get("name", "").strip()
                elif isinstance(dir_val, list) and dir_val:
                    first_dir = dir_val[0]
                    if isinstance(first_dir, dict):
                        director = first_dir.get("name", "").strip()

                # ACTORS
                actor_val = find_first_key(data, "actor")
                if isinstance(actor_val, list):
                    for a in actor_val:
                        if isinstance(a, dict) and "name" in a:
                            actors.append(a["name"].strip())
                        if len(actors) > 4:
                            break
                elif isinstance(actor_val, dict):
                    name = actor_val.get("name", "").strip()
                    if name:
                        actors.append(name)

        data_rows.append({
            "tconst": tconst,
            "storyline": storyline,
            "themes": themes,
            "director": director,
            "actors": actors,
            "gross_worldwide": gross
        })

    return pd.DataFrame(data_rows)

if __name__ == "__main__":

    movie_dataset = pd.read_csv("../datasets/54000_movies_dataset_prelim.csv")
    
    # Taking the tconst column and making it a list for the scrape_imdb_to_df function.
    tconst_list = movie_dataset["tconst"].iloc[51000:].tolist()
    
    # Running the scraper
    scrape_imdb_to_df(tconst_list)