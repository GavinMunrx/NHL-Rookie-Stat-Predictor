# NHL-Rookie-Stat-Predictor

# Data for Download


# Phase 1

## Overview
This project aims to predict NHL rookie scoring performance based on a players pre-NHL statistics from junior, European, or other professional leagues. The model links historical amateur/overseas professional stats with each player’s NHL rookie season to build a predictive model. This utilizes time series machine learning methodology. 

Current Focus:
- Collecting and cleaning amateur and NHL data.
- Merging datasets to align rookie seasons with prior league performance.
- Building an initial machine learning model to test feasibility.

---

## Data Preparation
- **Amateur Data:** Scraped from EliteProspects (OHL, WHL, QMJHL, NCAA, SHL, Liiga, KHL, AHL, etc.).
- **NHL Rookie Data:** Compiled from 2012–2013 to present, data is excluded from model for 2012-2013 due to lockout season (for now).
- **Merging:** For each player, their last amateur season before NHL entry was matched with their NHL rookie year stats.

### Special Considerations
- Removed **2012–13 NHL season** due to lockout (inconsistent games played).
- Ensured rookie season appears **after** amateur stats chronologically.
- Players are considered rookies based on NHL definition:
  - Fewer than 25 NHL games played in prior seasons.
  - Under age 26.

---

## Model – Initial Test
A **Random Forest Regressor** was trained using amateur player features (games played, goals, assists, points, league, etc.) to predict rookie NHL points.

### Results
- **MAE (Mean Absolute Error):** `14.23`  
  On average, predictions are off by ~14 points per player. 
  - This need imporvement, specifically by improving rookie tracking code and adding features.

- **R² Score:** `0.24`  
  Model explains ~24% of the variance in rookie scoring outcomes.  
  Indicates the model captures some signal but misses many factors like role, injuries, team strength, linemates, or other factors.

---

## Interpretation
- The model has **predictive value** but isn’t highly accurate yet, esoecially given the variance with Rookie stats and all the factors that contribute to success, further features must be created,
- This confirms feasibility: historical amateur stats **can correlate** with NHL rookie scoring, though more features are needed to prove this further.
- In looking over the CSV file used to train the model, many rookies are excluded as they spent time in a different league during the same year. Thus I must adjust the code to account for this as the file only contained ~90 players, however the true number should be much higher.

---

## Next Steps (Phase 2)
- Create league strength adjustment factors (e.g., SHL > OHL > NCAA) to fine tune. 
- Engineer **rate stats** like Points per Game (PPG) to handle shortened seasons (COVID, lockouts, injuries). 
- Include age, height, and weight as predictive features, this will have to be scraped from seperate websites or using Selinium. 
- Explore more advanced models (XGBoost, Neural Networks).
- Consider adding player debut data and age of debut from Hockeyreference.com to better identify rookie seasons.


## Replicate Instructions
- Coming soon ...