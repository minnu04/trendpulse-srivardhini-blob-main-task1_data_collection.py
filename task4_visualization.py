"""
TrendPulse: What's Actually Trending Right Now (Task 4)

This script loads the analysed CSV from Task 3, builds three Matplotlib charts,
and combines them into a dashboard figure saved as PNG files.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def shorten_title(title: str, limit: int = 50) -> str:
    """Trim long titles so the bar chart stays readable."""
    title = str(title)
    if len(title) <= limit:
        return title
    return title[: limit - 3].rstrip() + "..."


def build_top_stories_chart(df: pd.DataFrame, output_path: Path) -> None:
    top_stories = df.nlargest(10, "score").copy()
    top_stories = top_stories.sort_values("score")
    labels = top_stories["title"].map(shorten_title)

    fig, ax = plt.subplots(figsize=(11, 7))
    ax.barh(labels, top_stories["score"], color="#2F6BFF")
    ax.set_title("Top 10 Stories by Score")
    ax.set_xlabel("Score")
    ax.set_ylabel("Story Title")
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def build_category_chart(df: pd.DataFrame, output_path: Path, category_col: str) -> None:
    counts = df[category_col].value_counts().sort_values(ascending=False)
    colors = plt.cm.tab20(np.linspace(0, 1, len(counts)))

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(counts.index.astype(str), counts.values, color=colors)
    ax.set_title("Stories per Category")
    ax.set_xlabel("Category")
    ax.set_ylabel("Number of Stories")
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def build_scatter_chart(df: pd.DataFrame, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 7))

    popular = df[df["is_popular"]]
    not_popular = df[~df["is_popular"]]

    ax.scatter(not_popular["score"], not_popular["num_comments"], color="#9AA0A6", alpha=0.7, label="Not popular")
    ax.scatter(popular["score"], popular["num_comments"], color="#E45756", alpha=0.8, label="Popular")
    ax.set_title("Score vs Comments")
    ax.set_xlabel("Score")
    ax.set_ylabel("Number of Comments")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.25)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def build_dashboard(df: pd.DataFrame, output_path: Path, category_col: str) -> None:
    top_stories = df.nlargest(10, "score").copy().sort_values("score")
    labels = top_stories["title"].map(shorten_title)
    counts = df[category_col].value_counts().sort_values(ascending=False)
    category_colors = plt.cm.tab20(np.linspace(0, 1, len(counts)))
    popular = df[df["is_popular"]]
    not_popular = df[~df["is_popular"]]

    fig, axes = plt.subplots(1, 3, figsize=(22, 7))
    fig.suptitle("TrendPulse Dashboard", fontsize=18, fontweight="bold")

    axes[0].barh(labels, top_stories["score"], color="#2F6BFF")
    axes[0].set_title("Top 10 Stories")
    axes[0].set_xlabel("Score")
    axes[0].set_ylabel("Story")
    axes[0].grid(axis="x", linestyle="--", alpha=0.3)

    axes[1].bar(counts.index.astype(str), counts.values, color=category_colors)
    axes[1].set_title("Stories per Category")
    axes[1].set_xlabel("Category")
    axes[1].set_ylabel("Count")
    axes[1].tick_params(axis="x", rotation=30)

    axes[2].scatter(not_popular["score"], not_popular["num_comments"], color="#9AA0A6", alpha=0.7, label="Not popular")
    axes[2].scatter(popular["score"], popular["num_comments"], color="#E45756", alpha=0.8, label="Popular")
    axes[2].set_title("Score vs Comments")
    axes[2].set_xlabel("Score")
    axes[2].set_ylabel("Number of Comments")
    axes[2].legend()
    axes[2].grid(True, linestyle="--", alpha=0.25)

    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    data_file = Path("data") / "trends_analysed.csv"
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    df = pd.read_csv(data_file)
    category_col = "category" if "category" in df.columns else "subreddit"

    build_top_stories_chart(df, output_dir / "chart1_top_stories.png")
    build_category_chart(df, output_dir / "chart2_categories.png", category_col)
    build_scatter_chart(df, output_dir / "chart3_scatter.png")
    build_dashboard(df, output_dir / "dashboard.png", category_col)

    print("Saved chart1_top_stories.png")
    print("Saved chart2_categories.png")
    print("Saved chart3_scatter.png")
    print("Saved dashboard.png")


if __name__ == "__main__":
    main()