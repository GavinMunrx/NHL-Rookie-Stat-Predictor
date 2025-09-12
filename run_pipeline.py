from nhl_predictor.scraper import run_scraping
from nhl_predictor.train import run_training_dual
from nhl_predictor.cleaning_utils import clean_and_merge

if __name__ == "__main__":
    # print("Step 1: Scraping data...")
    # run_scraping()
    
    print("Step 2: Cleaning data...")
    clean_and_merge()
    
    print("Step 3: Training data...")
    run_training_dual()