# NHL-Rookie-Stat-Predictor

# Data for Download

https://drive.google.com/drive/folders/1YjIa0uNs8BlRtDSCjLJMaiRIyEGq8BDI?usp=sharing

# Phase 1

## Overview
This project aims to predict NHL rookie scoring performance based on a players pre-NHL statistics from junior, European, or other professional leagues. The model links historical amateur/overseas professional stats with each player’s NHL rookie season to build a predictive model. This utilizes time series machine learning methodology. 

Current Focus:
- Collecting and cleaning amateur and NHL data.
- Merging datasets to align rookie seasons with prior league performance.
- Building an initial machine learning model to test feasibility.

---

## Data Preparation & Cleaning
- **Amateur Data:** Scraped from EliteProspects (OHL, WHL, QMJHL, NCAA, SHL, Liiga, KHL, AHL, etc.).
- **NHL Rookie Data:** Compiled from 2012–2013 to present, data is excluded from model for 2012-2013 due to lockout season (for now).
- **NHL Debut Data:** Scraped from Hockey-reference.com with minimal server load, and used in determining players rookie status and rookie year.
- **NHL Bio Data:** Downloaded from moneypuck.com containing birth year, height and weight data.
- **Merging:** For each player, their last amateur season before NHL entry was matched with their NHL rookie year stats.
- **Filtering:** Only include amateur seasons with ≥5 games to reduce noise from small sample sizes.

### Special Considerations
- Removed **2012–13 NHL season** due to lockout (inconsistent games played).
- Ensured rookie season appears **after** amateur stats chronologically.
- Players are considered rookies based on NHL definition:
  - Fewer than 25 NHL games played in prior seasons.
  - Fewer then 6 games in each of the past 2 seasons
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
- The model has **predictive value** but isn’t highly accurate yet, esoecially given the variance with Rookie stats and all the factors that contribute to success, further features must be created.
- This confirms feasibility: historical amateur stats **can correlate** with NHL rookie scoring, though more features are needed to prove this further.
- In looking over the CSV file used to train the model, many rookies are excluded as they spent time in a different league during the same year. Thus I must adjust the code to account for this as the file only contained ~90 players, however the true number should be much higher.

---

# Phase 2

**Improvements:**
- Filtered amateur and professional seasons with **≥15 games** to reduce noise and outliers.
- Added player attributes: **age at rookie start, height, weight**.
- One-hot encoded **amateur league**.
- Tuned Random Forest and XGBoost using `RandomizedSearchCV`.
- Added 3rd model training combining XGBoost with PPG data instead of total points data.
- Increased n_estimators, optimized max_depth, adjusted random_state, adjusted min_samples, learning_rate, and much more.
- Created .ipynb for data visualization and outlier detection for further imporvements. 

### Features
- points per game professional and amateur
- Age, height, weight
- League encoding (one-hot)

### Latest Results
| Model         |  MAE  |  R²   |
|---------------|-------|-------|
| Random Forest | 7.11  | 0.327 |
| XGBoost       | 6.92  | 0.384 |
| XGBoost (ppg) |  0.1  | 0.216 |

**Observations:**
- Filtering and hyperparameter tuning significantly reduced MAE compared to Phase 1.
- XGBoost slightly outperforms Random Forest in both MAE and R².
- Models capture more predictive signal but still miss variance caused by role, team context, and injuries.

## UPDATED Interpretation
- The model has an even greater **predictive value** and has become much more accurate. With extreme improvements in the MAE, the model is still not able to explain much of the variance in rookie statistics.
- The cleaned CSV makes training much easier and more accurate.
- Going even deeper into more niche features could aid in explaining the variance at a deeper level.

---

## Next Steps (Phase 3)
- Apply **league strength adjustments** (SHL > OHL > NCAA) for refined predictions.  
- Consider **ensemble methods** (Random Forest + XGBoost) for improved stability.  
- Explore **neural networks** or other advanced models for further performance gains.  

---

## Replication Instructions
- Coming soon ...
