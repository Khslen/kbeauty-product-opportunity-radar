from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
PROCESSED_DIR = BASE_DIR / "data" / "processed"


WEIGHTS = {
    "current_interest": 0.30,
    "momentum": 0.40,
    "creator_attention": 0.20,
    "cross_market_alignment": 0.10,
}


def weighted_score(row: pd.Series) -> float:
    total = 0.0
    available_weight = 0.0

    for column, weight in WEIGHTS.items():
        value = row[column]

        if pd.notna(value):
            total += value * weight
            available_weight += weight

    if available_weight == 0:
        return np.nan

    return total / available_weight


def confidence_label(coverage: float) -> str:
    if coverage >= 100:
        return "High"
    if coverage >= 80:
        return "Medium"
    return "Low"


def main() -> None:
    input_path = PROCESSED_DIR / "features.csv"
    output_path = PROCESSED_DIR / "opportunity_scores.csv"

    df = pd.read_csv(input_path)

    # Score before accounting for missing data.
    df["raw_opportunity_score"] = df.apply(
        weighted_score,
        axis=1,
    )

    # Reduce the score slightly when important signals are missing.
    df["reliability_factor"] = (
        0.70 + 0.30 * (df["data_coverage_pct"] / 100)
    )

    df["opportunity_score"] = (
        df["raw_opportunity_score"]
        * df["reliability_factor"]
    )

    df["confidence"] = df["data_coverage_pct"].apply(
        confidence_label
    )

    df["category_rank"] = (
        df.groupby("category")["opportunity_score"]
        .rank(method="dense", ascending=False)
        .astype(int)
    )

    df["overall_rank"] = (
        df["opportunity_score"]
        .rank(method="dense", ascending=False)
        .astype(int)
    )

    df = df.sort_values(
        ["opportunity_score", "data_coverage_pct"],
        ascending=[False, False],
    ).reset_index(drop=True)

    selected_columns = [
        "overall_rank",
        "category_rank",
        "keyword",
        "korean_keyword",
        "category",
        "opportunity_score",
        "raw_opportunity_score",
        "current_interest",
        "momentum",
        "creator_attention",
        "cross_market_alignment",
        "data_coverage_pct",
        "confidence",
    ]

    df = df[selected_columns]

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns

    df[numeric_columns] = df[numeric_columns].round(2)

    df.to_csv(output_path, index=False)

    print(f"Saved {len(df)} rows to {output_path}")
    print()
    print(
        df[
            [
                "overall_rank",
                "keyword",
                "category",
                "opportunity_score",
                "confidence",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()