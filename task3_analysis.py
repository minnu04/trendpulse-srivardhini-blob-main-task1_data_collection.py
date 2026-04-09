"""
TrendPulse: What's Actually Trending Right Now (Task 3)

This script loads the cleaned CSV from Task 2, explores it with Pandas and NumPy,
adds a couple of derived columns, and saves the analysed dataset for Task 4.
"""

from pathlib import Path

import numpy as np
import pandas as pd


def main() -> None:
    data_dir = Path("data")
    input_file = data_dir / "trends_clean.csv"
    output_file = data_dir / "trends_analysed.csv"

    df = pd.read_csv(input_file)
    print(f"Loaded data: {df.shape}")
    print()

    print("First 5 rows:")
    print(df.head())
    print()

    average_score = df["score"].mean()
    average_comments = df["num_comments"].mean()

    print(f"Average score   : {average_score:,.0f}")
    print(f"Average comments: {average_comments:,.0f}")
    print()

    scores = df["score"].to_numpy()

    print("--- NumPy Stats ---")
    print(f"Mean score   : {np.mean(scores):,.0f}")
    print(f"Median score : {np.median(scores):,.0f}")
    print(f"Std deviation: {np.std(scores):,.0f}")
    print(f"Max score    : {np.max(scores):,.0f}")
    print(f"Min score    : {np.min(scores):,.0f}")
    print()

    category_col = "category" if "category" in df.columns else "subreddit"
    category_counts = df[category_col].value_counts()
    top_category = category_counts.idxmax()
    top_category_count = int(category_counts.max())
    print(f"Most stories in: {top_category} ({top_category_count} stories)")
    print()

    top_comment_index = df["num_comments"].idxmax()
    top_comment_story = df.loc[top_comment_index]
    print(
        f'Most commented story: "{top_comment_story["title"]}"  '
        f'- {int(top_comment_story["num_comments"]):,} comments'
    )
    print()

    # Engagement measures how much discussion a story gets relative to its score.
    df["engagement"] = df["num_comments"] / (df["score"] + 1)

    # Popularity is based on whether a story is above the dataset average score.
    df["is_popular"] = df["score"] > average_score

    df.to_csv(output_file, index=False)
    print(f"Saved to {output_file.as_posix()}")


if __name__ == "__main__":
    main()