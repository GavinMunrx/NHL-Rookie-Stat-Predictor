from nhl_predictor.scraper import run_scraping
from nhl_predictor.train import run_training

if __name__ == "__main__":
    print("Step 1: Scraping data...")
    run_scraping()
    
    
    
    run_training()  