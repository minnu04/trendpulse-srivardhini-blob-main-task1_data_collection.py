"""
TrendPulse: Data Processing Module (Task 2)

This script loads the raw JSON data collected in Task 1,
cleans it using Pandas, and saves a tidy CSV file.
"""

from pathlib import Path
import json
import pandas as pd


def find_latest_trends_file(data_dir: Path) -> Path:
    """Return the latest trends_YYYYMMDD.json file from the data directory."""
    json_files = sorted(data_dir.glob("trends_*.json"))
    if not json_files:
        raise FileNotFoundError("No trends_YYYYMMDD.json file found in the data folder.")
    return json_files[-1]


def main() -> None:
    data_dir = Path("data")
    input_file = find_latest_trends_file(data_dir)

    # 1) Load JSON into a DataFrame
    with input_file.open("r", encoding="utf-8") as file:
        raw_data = json.load(file)

    # Task 1 output may be wrapped as {"metadata": ..., "stories": [...]}.
    if isinstance(raw_data, dict) and "stories" in raw_data:
        records = raw_data["stories"]
    elif isinstance(raw_data, list):
        records = raw_data
    else:
        raise ValueError("Unsupported JSON format. Expected a list or a dict with 'stories'.")

    df = pd.DataFrame(records)
    print(f"Loaded {len(df)} stories from {input_file.as_posix()}")
    print()

    # 2) Clean data step by step

    # Remove duplicate stories using post_id as unique key.
    df = df.drop_duplicates(subset=["post_id"])
    print(f"After removing duplicates: {len(df)}")

    # Remove rows that are missing critical fields.
    df = df.dropna(subset=["post_id", "title", "score"])
    print(f"After removing nulls: {len(df)}")

    # Strip extra spaces in titles.
    df["title"] = df["title"].astype(str).str.strip()

    # Convert numeric fields to proper integer types.
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df = df.dropna(subset=["score"])
    df["score"] = df["score"].astype(int)

    df["num_comments"] = pd.to_numeric(df.get("num_comments", 0), errors="coerce")
    df["num_comments"] = df["num_comments"].fillna(0).astype(int)

    # Remove low-quality stories.
    df = df[df["score"] >= 5]
    print(f"After removing low scores: {len(df)}")
    print()

    # 3) Save cleaned data to CSV
    output_file = data_dir / "trends_clean.csv"
    df.to_csv(output_file, index=False)

    print(f"Saved {len(df)} rows to {output_file.as_posix()}")
    print()

    print("Stories per category:")
    if "subreddit" in df.columns:
        print(df["subreddit"].value_counts().sort_index().to_string())
    else:
        print("Category column not found.")


if __name__ == "__main__":
    main()
