from nhl_predictor.scraper_utils import scrape_statistics
import os
import pandas as pd

def run_scraping():
    leagues = ["ahl",
            #    "ohl","whl","qmjhl","ushl","khl","shl","nl","liiga","ncaa"
            ]
    
    seasons = ["2012-2013",
            #    "2013-2014",
            #    "2014-2015",
            #    "2015-2016",
            #    "2016-2017",
            #    "2017-2018",
            #    "2018-2019",
            #    "2019-2020",
            #    "2020-2021",
            #    "2021-2022",
            #    "2022-2023",
            #    "2023-2024",
            #    "2024-2025"
               ]

    all_amateur = []
    all_nhl = []

    os.makedirs("data", exist_ok=True)

    # for season in seasons:
    for league in leagues:
        for season in seasons:
            try:
                players_am = scrape_statistics(league, season)
                all_amateur.append(players_am)
            except Exception as e:
                print(f"Error scraping {league} {season}: {e}")

    for season in seasons:
        try:
            players_pro = scrape_statistics('nhl', season)
            all_nhl.append(players_pro)
        except Exception as e:
            print(f"Error scraping NHL rookies {season}: {e}")

    final_am_df = pd.concat(all_amateur, ignore_index=True)
    final_am_df.to_csv("data/amateur_all1.csv", index=False)
    final_nhl_df = pd.concat(all_nhl, ignore_index=True)
    final_nhl_df.to_csv("data/nhl_all.csv", index=False)
    print(f"Saved {len(all_amateur)} seasons of amateur players, {len(all_nhl)} saeasons of NHL players.")
