from nhl_predictor.scraper_utils import scrape_statistics
import os
import pandas as pd

def run_scraping():
    leagues = ["ahl",
               "ohl",
               "whl",
               "qmjhl",
               "ushl",
               "khl",
               "shl",
               "nl",
               "liiga",
               "ncaa"
            ]
    
    seasons = ["2012-2013",
               "2013-2014",
               "2014-2015",
               "2015-2016",
               "2016-2017",
               "2017-2018",
               "2018-2019",
               "2019-2020",
               "2020-2021",
               "2021-2022",
               "2022-2023",
               "2023-2024",
               "2024-2025"
               ]

 # Load existing data if available
    am_path = "data/raw/amateur_all.csv"
    nhl_path = "data/raw/nhl_all.csv"

    if os.path.exists(am_path):
        amateur_df = pd.read_csv(am_path)
    else:
        amateur_df = pd.DataFrame()

    if os.path.exists(nhl_path):
        nhl_df = pd.read_csv(nhl_path)
    else:
        nhl_df = pd.DataFrame()

    all_amateur = []
    all_nhl = []

    os.makedirs("data", exist_ok=True)

    # Amateur leagues
    for league in leagues:
        for season in seasons:
            # Check if this league/season already exists in amateur_df
            if not amateur_df.empty and ((amateur_df["league"] == league) & (amateur_df["season"] == season)).any():
                print(f"{league.upper()} {season}, already scraped.")
                continue

            try:
                players_am = scrape_statistics(league, season)
                players_am["league"] = league
                players_am["season"] = season
                all_amateur.append(players_am)
            except Exception as e:
                print(f"Error scraping {league} {season}: {e}")

    # NHL rookies
    for season in seasons:
        if not nhl_df.empty and (nhl_df["season"] == season).any():
            print(f"NHL {season}, already scraped.")
            continue

        try:
            players_pro = scrape_statistics('nhl', season)
            players_pro["season"] = season
            all_nhl.append(players_pro)
        except Exception as e:
            print(f"Error scraping NHL rookies {season}: {e}")

    # Save new data only if there is some
    if all_amateur:
        new_am_df = pd.concat(all_amateur, ignore_index=True)
        amateur_df = pd.concat([amateur_df, new_am_df], ignore_index=True)
        amateur_df.to_csv(am_path, index=False)

    if all_nhl:
        new_nhl_df = pd.concat(all_nhl, ignore_index=True)
        nhl_df = pd.concat([nhl_df, new_nhl_df], ignore_index=True)
        nhl_df.to_csv(nhl_path, index=False)

    print(f"Saved {len(all_amateur)} new amateur seasons, {len(all_nhl)} new NHL seasons.")