from nhl_predictor.scraper_utils import scrape_eliteprospects_league_season
import os
import pandas as pd

def run_scraping():
    leagues = ["ohl"]
    season = "2023-2024"

    all_amateur = []
    all_nhl = []

    os.makedirs("data/raw", exist_ok=True)

    # for season in seasons:
    for league in leagues:
            try:
                players = scrape_eliteprospects_league_season(league, str(season))
                all_amateur.extend(players)
            except Exception as e:
                print(f"Error scraping {league} {season}: {e}")

        # try:
        # #     rookies = scrape_moneypuck_nhl_rookies(str(season))
        # #     all_nhl.extend(rookies)
        # except Exception as e:
        #     print(f"Error scraping NHL rookies {season}: {e}")

    pd.DataFrame(all_amateur).to_csv("data/raw/amateur_all_test.csv", index=False)
    pd.DataFrame(all_nhl).to_csv("data/raw/nhl_rookies_all.csv", index=False)
    print(f"Saved {len(all_amateur)} amateur players, {len(all_nhl)} NHL rookies.")
