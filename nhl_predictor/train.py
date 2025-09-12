import pandas as pd
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import os
import joblib
import xgboost as xgb
    
def run_training_dual():
    # Load cleaned data
    df = pd.read_csv("data/processed/amateur_to_rookie_with_bio.csv")

    # Filter out players with very few amateur games
    df = df[df['gp_amateur'] >= 5]

    # One-hot encode league
    league_dummies = pd.get_dummies(df['league_amateur'])
    df = pd.concat([df, league_dummies], axis=1)

    # Feature engineering
    df['age_at_rookie_start'] = df['age_at_rookie_start'].fillna(df['age_at_rookie_start'].median())
    df['weight'] = df['weight'].fillna(df['weight'].median())
    df['height'] = df['height'].fillna(df['height'].median())

    # Features and target
    feature_cols = ['gp_amateur', 'goals_amateur', 'assists_amateur', 'points_amateur',
                    'age_at_rookie_start', 'weight', 'height'] + list(league_dummies.columns)
    X = df[feature_cols]
    y = df['points_nhl']

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # ---------------- Random Forest ----------------
    rf = RandomForestRegressor(n_jobs=-1, random_state=55)
    rf_params = {
        'n_estimators': [200, 300, 400],
        'max_depth': [8, 10, 12, None],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    }
    rf_search = RandomizedSearchCV(rf, rf_params, n_iter=10, cv=3, scoring='neg_mean_absolute_error', random_state=55)
    rf_search.fit(X_train, y_train)
    rf_best = rf_search.best_estimator_
    rf_pred = rf_best.predict(X_test)

    print("Random Forest Evaluation:")
    print("Best Params:", rf_search.best_params_)
    print("MAE:", mean_absolute_error(y_test, rf_pred))
    print("R^2 Score:", r2_score(y_test, rf_pred))

    # ---------------- XGBoost ----------------
    xgb_model = xgb.XGBRegressor(objective='reg:squarederror', n_jobs=-1, random_state=55)
    xgb_params = {
        'n_estimators': [200, 300, 400],
        'max_depth': [3, 5, 7],
        'learning_rate': [0.01, 0.05, 0.1],
        'subsample': [0.7, 0.8, 1.0],
        'colsample_bytree': [0.7, 0.8, 1.0]
    }
    xgb_search = RandomizedSearchCV(xgb_model, xgb_params, n_iter=10, cv=3, scoring='neg_mean_absolute_error', random_state=55)
    xgb_search.fit(X_train, y_train)
    xgb_best = xgb_search.best_estimator_
    xgb_pred = xgb_best.predict(X_test)

    print("\nXGBoost Evaluation:")
    print("Best Params:", xgb_search.best_params_)
    print("MAE:", mean_absolute_error(y_test, xgb_pred))
    print("R^2 Score:", r2_score(y_test, xgb_pred))

    # Save models
    os.makedirs("models", exist_ok=True)
    joblib.dump((rf_best, feature_cols), "models/nhl_rookie_predictor_rf.pkl")
    joblib.dump((xgb_best, feature_cols), "models/nhl_rookie_predictor_xgb.pkl")
    print("\nModels saved to models/nhl_rookie_predictor_rf.pkl and models/nhl_rookie_predictor_xgb.pkl")
