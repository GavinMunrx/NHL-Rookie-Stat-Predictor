
import pandas as pd
import numpy as np
import re

def normalize_name(name):
    """Normalize player names for merging."""
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

    # Convert season to integer for sorting
    def season_to_int(season):
        return int(season.split('-')[0])

    for df in [amateur_df, nhl_df, nhl_debut]:
        df['season_sort'] = df['season'].apply(season_to_int)

    # Remove lockout season
    for df in [amateur_df, nhl_df, nhl_debut]:
        df.drop(df[df['season'] == '2012-2013'].index, inplace=True)

    # Sort NHL data
    nhl_df = nhl_df.sort_values(['name_norm', 'season_sort'])
    
    # Compute previous season GP 
    nhl_df['prev1_gp'] = nhl_df.groupby('name_norm')['gp'].shift(1).fillna(0)
    nhl_df['prev2_gp'] = nhl_df.groupby('name_norm')['gp'].shift(2).fillna(0)

    # Merge debut info
    nhl_df = nhl_df.merge(
        nhl_debut[['name_norm', 'debut_age', 'debut_date']],
        on='name_norm',
        how='left'
    )

    # Convert debut_age to integer years
    nhl_df['age_years'] = nhl_df['debut_age'].apply(lambda x: int(x.split('-')[0]) if pd.notna(x) else np.nan)

    # Rookie Check
    def is_rookie(row):
        """
        Rookie detection:
        - Age < 25
        - Previous games: prev1 < 25 OR (prev1 < 6 AND prev2 < 6)
        - Exclude obvious 1-game debuts
        """
        if pd.isna(row['age_years']) or row['age_years'] >= 25:
            return False
        if row['gp'] == 1:  # exclude 1-game debuts
            return False
        if row['prev1_gp'] < 25:
            return True
        if row['prev1_gp'] < 6 and row['prev2_gp'] < 6:
            return True
        return False


    nhl_df['rookie_candidate'] = nhl_df.apply(is_rookie, axis=1)

    # Keep only first rookie season
    rookies = nhl_df[nhl_df['rookie_candidate']].copy()
    rookies = rookies.sort_values(['name_norm', 'season_sort'])
    rookies = rookies.groupby('name_norm').first().reset_index()
    rookies['rookie'] = True

    # Merge amateur seasons 
    amateur_df = amateur_df.sort_values(['name_norm', 'season_sort'])
    rookie_seasons = rookies[['name_norm', 'season_sort']]
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

    # Merge amateur + rookie + bio
    merged = pd.merge(last_amateur_before_rookie, rookies, on='name_norm', suffixes=('_amateur','_nhl'))
    nhl_bio['name_norm'] = nhl_bio['name'].apply(normalize_name)
    merged = merged.merge(nhl_bio, on='name_norm', how='left')

    # Height conversion
    def height_to_inches(height_str):
        if pd.isna(height_str):
            return np.nan
        try:
            feet, inches = height_str.split("'")
            inches = inches.replace('"', '')
            return int(feet) * 12 + int(inches)
        except:
            return np.nan

    merged['height'] = merged['height'].apply(height_to_inches)
    merged['height'] = pd.to_numeric(merged['height'], errors='coerce')
    merged['height'] = merged['height'].fillna(merged['height'].median())

    # Birthdate
    merged['birthDate'] = pd.to_datetime(merged['birthDate'], errors='coerce')
    merged['rookie_start_date'] = pd.to_datetime(merged['season_sort_nhl'].astype(str) + '-09-15')
    merged['age_at_rookie_start'] = ((merged['rookie_start_date'] - merged['birthDate']).dt.days / 365.25).round(2)

    # Points per game
    merged['ppg_amateur'] = merged.apply(lambda r: r['points_amateur'] / r['gp_amateur'] if r['gp_amateur']>0 else np.nan, axis=1)
    merged['ppg_nhl'] = merged.apply(lambda r: r['points_nhl'] / r['gp_nhl'] if r['gp_nhl']>0 else np.nan, axis=1)
    
    # Clean column names
    merged = merged.drop(columns=['name']).rename(columns={"name_nhl":"name"})
    
    # Ensure 'name' is a string
    merged['name'] = merged['name'].astype(str)

    # Append suffix to duplicates
    counts = merged.groupby('name').cumcount()
    merged['name'] = merged['name'] + counts.replace(0, '').astype(str)

    # Reset index
    merged = merged.reset_index(drop=True)

    # Save CSV
    merged.to_csv("data/processed/amateur_to_rookie_with_bio.csv", index=False)
    print(f"Final dataset shape (duplicates kept with suffixes): {merged.shape}")



    merged = merged[['name','season_amateur','team_amateur','league_amateur','gp_amateur','goals_amateur','assists_amateur','points_amateur',
                    'ppg_amateur','season_nhl','team_nhl','gp_nhl','goals_nhl','assists_nhl','points_nhl','ppg_nhl',
                    'age_at_rookie_start','birthDate','weight','height']]

    # Output CSV
    merged.to_csv("data/processed/amateur_to_rookie_with_bio.csv", index=False)
    print(f"Merged dataset shape: {merged.shape}")
    
    return merged
