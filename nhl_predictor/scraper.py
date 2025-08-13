from nhl_predictor.scraper_utils import scrape_amateur_stats
from nhl_predictor.scraper_utils import scrape_nhl_stats
import os
import pandas as pd

def run_scraping():
    leagues = ["ohl","whl"]
    seasons = ["2023-2024", "2024-2025"]

    all_amateur = []
    all_nhl = []

    os.makedirs("data/raw", exist_ok=True)

    # for season in seasons:
    for league in leagues:
        for season in seasons:
            try:
                players = scrape_amateur_stats(league, str(season))
                all_amateur.extend(players)
            except Exception as e:
                print(f"Error scraping {league} {season}: {e}")

    for season in seasons:
        try:
            season_stats = scrape_nhl_stats(season)
            all_nhl.append(season_stats)
        except Exception as e:
            print(f"Error scraping NHL rookies {season}: {e}")

    pd.DataFrame(all_amateur).to_csv("data/raw/amateur_all.csv", index=False)
    final_nhl_df = pd.concat(all_nhl, ignore_index=True)
    final_nhl_df.to_csv("data/raw/nhl_all.csv", index=False)
    print(f"Saved {len(all_amateur)} amateur players, {len(all_nhl)} NHL Players.")
