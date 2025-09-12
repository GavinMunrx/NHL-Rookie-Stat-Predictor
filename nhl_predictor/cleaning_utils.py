
import pandas as pd
import numpy as np
import re

def normalize_name(name):
    """Remove position suffixes, parentheses, extra spaces, lowercase."""
    if pd.isna(name):
        return ""
    name = re.sub(r"\s*\(.*\)$", "", name)
    return name.strip().lower()

def clean_and_merge():
    # Load datasets
    amateur_df = pd.read_csv("data/raw/amateur_all.csv")
    nhl_df = pd.read_csv("data/raw/nhl_all.csv")
    nhl_debut = pd.read_csv("data/raw/nhl_debuts.csv")
    nhl_bio = pd.read_csv("data/raw/nhl_player_bio_data.csv")

    # Normalize names
    for df in [amateur_df, nhl_df, nhl_debut, nhl_bio]:
        df['name_norm'] = df['name'].apply(normalize_name)

    # Convert season to sortable integer
    def season_to_int(season):
        return int(season.split('-')[0])
    
    for df in [amateur_df, nhl_df, nhl_debut]:
        df['season_sort'] = df['season'].apply(season_to_int)

    # Remove lockout season
    for df in [amateur_df, nhl_df, nhl_debut]:
        df.drop(df[df['season'] == '2012-2013'].index, inplace=True)

    # Sort NHL dataframe
    nhl_df = nhl_df.sort_values(['name_norm', 'season_sort'])

    # Compute cumulative games prior to each season
    nhl_df['gp_prior'] = nhl_df.groupby('name_norm')['gp'].cumsum() - nhl_df['gp']

    # Compute max games played in last 2 seasons
    def last_two_seasons_gp(series):
        games = series.tolist()
        last2 = []
        for i in range(len(games)):
            if i == 0:
                last2.append(0)
            elif i == 1:
                last2.append(games[i-1])
            else:
                last2.append(max(games[i-1], games[i-2]))
        return pd.Series(last2, index=series.index)

    nhl_df['gp_last2'] = nhl_df.groupby('name_norm')['gp'].apply(last_two_seasons_gp).reset_index(level=0, drop=True)

    # Merge debut info
    nhl_df = nhl_df.merge(
        nhl_debut[['name_norm', 'debut_age', 'debut_date']],
        on='name_norm',
        how='left'
    )

    # Convert debut_age to integer years
    def get_age_years(debut_age):
        if pd.isna(debut_age):
            return np.nan
        return int(debut_age.split('-')[0])
    
    nhl_df['age_years'] = nhl_df['debut_age'].apply(get_age_years)

    # Identify rookie seasons
    def is_rookie(row):
        if pd.isna(row['age_years']):
            return False
        if row['age_years'] > 26:
            return False
        # Standard rule: prior games <= 25
        if row['gp_prior'] <= 25:
            return True
        # Under-26 exception: <6 games in each of last 2 seasons
        if row['age_years'] < 26 and row['gp_last2'] < 6:
            return True
        return False

    nhl_df['rookie_candidate'] = nhl_df.apply(is_rookie, axis=1)

    # Keep only first rookie season per player
    rookies = nhl_df[nhl_df['rookie_candidate']].copy()
    rookies = rookies.sort_values(['name_norm', 'season_sort'])
    rookies = rookies.groupby('name_norm').first().reset_index()
    rookies['rookie'] = True

    # Prepare amateur seasons immediately before rookie season
    amateur_df = amateur_df.sort_values(['name_norm', 'season_sort'])
    rookie_seasons = rookies[['name_norm', 'season_sort']].copy()
    amateur_df = amateur_df.merge(
        rookie_seasons,
        on='name_norm',
        how='inner',
        suffixes=('_amateur', '_nhl')
    )

    # Keep only amateur seasons strictly before rookie season
    amateur_df = amateur_df[amateur_df['season_sort_amateur'] < amateur_df['season_sort_nhl']]

    # Pick last amateur season before rookie
    last_amateur_before_rookie = amateur_df.sort_values(['name_norm','season_sort_amateur']).groupby('name_norm').last().reset_index()

    # Merge with rookie data
    merged = pd.merge(
        last_amateur_before_rookie,
        rookies,
        on='name_norm',
        suffixes=('_amateur','_nhl')
    )

    # Merge player bio data
    nhl_bio['name_norm'] = nhl_bio['name'].apply(normalize_name)
    merged = merged.merge(
        nhl_bio,
        on='name_norm',
        how='left',
        suffixes=('', '_bio')
    )
    
    def height_to_inches(height_str):
        if pd.isna(height_str):
            return np.nan
        try:
            feet, inches = height_str.split("'")
            inches = inches.replace('"', '')
            return int(feet) * 12 + int(inches)
        except:
            return np.nan

    # Apply to dataframe
    merged['height'] = merged['height'].apply(height_to_inches)

    # Now you can fill missing values with median
    merged['height'] = merged['height'].fillna(merged['height'].median())

    # Convert birthDate to datetime
    merged['birthDate'] = pd.to_datetime(merged['birthDate'], errors='coerce')

    # Assume rookie season starts Sept 15 of the season start year
    merged['rookie_start_date'] = pd.to_datetime(merged['season_sort_nhl'].astype(str) + '-09-15')

    # Compute age at rookie season start in years
    merged['age_at_rookie_start'] = (merged['rookie_start_date'] - merged['birthDate']).dt.days / 365.25
    merged['age_at_rookie_start'] = merged['age_at_rookie_start'].round(2)

    # Calculate points per game
    merged['ppg_amateur'] = merged.apply(
        lambda row: row['points_amateur'] / row['gp_amateur'] if row['gp_amateur'] > 0 else np.nan,
        axis=1
    )

    merged['ppg_nhl'] = merged.apply(
        lambda row: row['points_nhl'] / row['gp_nhl'] if row['gp_nhl'] > 0 else np.nan,
        axis=1
    )
    
    merged = merged.drop(columns=['name'])
    
    merged = merged.rename(columns={"name_nhl": "name"})
    
    merged = merged[(merged['gp_amateur'] >= 5)]
    
    merged = merged[['name','season_amateur','team_amateur','league_amateur','gp_amateur','goals_amateur','assists_amateur','points_amateur'
                    ,'ppg_amateur','season_nhl','team_nhl','gp_nhl','goals_nhl','assists_nhl','points_nhl','ppg_nhl','age_at_rookie_start','birthDate','weight','height']]
    
    # Output CSV
    merged.to_csv("data/processed/amateur_to_rookie_with_bio.csv", index=False)
    print(f"Merged dataset shape: {merged.shape}")
    return merged

# Run the full pipeline
merged = clean_and_merge()
