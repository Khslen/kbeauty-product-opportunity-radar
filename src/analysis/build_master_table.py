from pathlib import Path
import sys

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

sys.path.insert(0, str(BASE_DIR))

from config.keywords import ALL_KEYWORDS


def summarize_timeseries(path: Path, prefix: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["keyword", "date"])

    return (
        df.groupby("keyword", as_index=False)
        .agg(
            **{
                f"{prefix}_avg": ("value", "mean"),
                f"{prefix}_latest": ("value", "last"),
                f"{prefix}_observations": ("value", "count"),
            }
        )
    )


def load_youtube() -> pd.DataFrame:
    df = pd.read_csv(RAW_DIR / "youtube_mentions.csv")

    return df[
        [
            "keyword",
            "window_days",
            "video_count",
            "total_views",
        ]
    ].copy()


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    keyword_info = pd.DataFrame(ALL_KEYWORDS)[
        ["en", "kr", "category"]
    ].rename(
        columns={
            "en": "keyword",
            "kr": "korean_keyword",
        }
    )

    naver = summarize_timeseries(
        RAW_DIR / "naver_trends.csv",
        "naver",
    )

    google = summarize_timeseries(
        RAW_DIR / "google_trends.csv",
        "google",
    )

    youtube = load_youtube()

    master = keyword_info.merge(
        naver,
        on="keyword",
        how="left",
    )

    master = master.merge(
        google,
        on="keyword",
        how="left",
    )

    master = master.merge(
        youtube,
        on="keyword",
        how="left",
    )

    category_order = {
        "consumer_need": 1,
        "ingredient": 2,
        "product_format": 3,
    }

    master["category_order"] = master["category"].map(category_order)

    master = (
        master.sort_values(["category_order", "keyword"])
        .drop(columns="category_order")
        .reset_index(drop=True)
    )

    output_path = PROCESSED_DIR / "master_table.csv"
    master.to_csv(output_path, index=False)

    print(f"Saved {len(master)} rows to {output_path}")
    print()
    print(master.to_string(index=False))


if __name__ == "__main__":
    main()