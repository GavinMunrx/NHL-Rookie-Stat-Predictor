import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import os

def run_training():
    df = pd.read_csv("data/processed/merged.csv")

    # One-hot encode league
    league_dummies = pd.get_dummies(df['league'])
    df = pd.concat([df, league_dummies], axis=1)

    X = df[['gp_amateur', 'goals_amateur', 'assists_amateur', 'points_amateur', 'pim_amateur', 'age_amateur', 'height_ameteur', 'weight_ameteur'] + list(league_dummies.columns)]
    y = df['points_nhl']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    print("Model Evaluation:")
    print("MAE:", mean_absolute_error(y_test, y_pred))
    print("R^2 Score:", r2_score(y_test, y_pred))

    os.makedirs("models", exist_ok=True)
    pd.DataFrame({'actual': y_test, 'predicted': y_pred}).to_csv("models/predictions.csv", index=False)
