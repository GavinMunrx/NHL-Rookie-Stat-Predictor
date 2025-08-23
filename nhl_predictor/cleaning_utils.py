
import pandas as pd

def clean_data():
    # Load your CSVs
    amateur_df = pd.read_csv("data/raw/amateur_all.csv")
    nhl_df = pd.read_csv("data/raw/nhl_all.csv")

    # Ensure season is sortable (string or int)
    amateur_df["season"] = amateur_df["season"].astype(str)
    nhl_df["season"] = nhl_df["season"].astype(str)

    # Remove 2012-2013 lockout season
    amateur_df = amateur_df[amateur_df["season"] != "2012-2013"]
    nhl_df = nhl_df[nhl_df["season"] != "2012-2013"]

    # Get last amateur season
    last_amateur = (amateur_df
                    .sort_values("season")
                    .groupby("name")
                    .tail(1))

    # Get first NHL season
    first_nhl = (nhl_df
                .sort_values("season")
                .groupby("name")
                .head(1))

    # Ensure rookie NHL season is after last amateur season
    merged = pd.merge(
        last_amateur,
        first_nhl,
        on="name",
        suffixes=("_amateur", "_nhl")
    )

    # Filter rows where NHL season > amateur season
    merged = merged[merged["season_nhl"] > merged["season_amateur"]]

    # Save merged dataset
    merged.to_csv("amateur_to_rookie.csv", index=False)
    print(f"Merged dataset shape (only valid rookie transitions): {merged.shape}")
