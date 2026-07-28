from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def min_max_score(series: pd.Series) -> pd.Series:
    """Convert values into a 0–100 score."""
    valid = series.dropna()

    if valid.empty:
        return pd.Series(np.nan, index=series.index)

    minimum = valid.min()
    maximum = valid.max()

    if minimum == maximum:
        return series.apply(
            lambda value: 50.0 if pd.notna(value) else np.nan
        )

    return ((series - minimum) / (maximum - minimum)) * 100


def calculate_momentum(
    file_path: Path,
    source_name: str,
    recent_periods: int = 12,
) -> pd.DataFrame:
    """
    Compare the latest 12 observations with the previous 12 observations.
    Positive values mean interest is growing.
    """
    df = pd.read_csv(file_path)

    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    results = []

    for keyword, group in df.groupby("keyword"):
        group = (
            group.sort_values("date")
            .dropna(subset=["value"])
            .reset_index(drop=True)
        )

        recent = group.tail(recent_periods)
        previous = group.iloc[
            max(0, len(group) - recent_periods * 2):
            max(0, len(group) - recent_periods)
        ]

        if recent.empty or previous.empty:
            momentum = np.nan
            recent_average = np.nan
            previous_average = np.nan
        else:
            recent_average = recent["value"].mean()
            previous_average = previous["value"].mean()

            if previous_average == 0:
                momentum = (
                    100.0 if recent_average > 0 else 0.0
                )
            else:
                momentum = (
                    (recent_average - previous_average)
                    / previous_average
                ) * 100

        results.append(
            {
                "keyword": keyword,
                f"{source_name}_recent_avg": recent_average,
                f"{source_name}_previous_avg": previous_average,
                f"{source_name}_momentum_pct": momentum,
            }
        )

    return pd.DataFrame(results)


def add_category_scores(
    df: pd.DataFrame,
    source_column: str,
    score_column: str,
) -> pd.DataFrame:
    """Normalize a feature within each keyword category."""
    df[score_column] = (
        df.groupby("category")[source_column]
        .transform(min_max_score)
        .clip(0, 100)
    )

    return df


def calculate_weighted_average(
    row: pd.Series,
    columns_and_weights: dict[str, float],
) -> float:
    """
    Calculate a weighted average using only available values.

    Missing data is excluded instead of automatically receiving zero.
    """
    weighted_total = 0.0
    available_weight = 0.0

    for column, weight in columns_and_weights.items():
        value = row[column]

        if pd.notna(value):
            weighted_total += value * weight
            available_weight += weight

    if available_weight == 0:
        return np.nan

    return weighted_total / available_weight


def main() -> None:
    master_path = PROCESSED_DIR / "master_table.csv"

    master = pd.read_csv(master_path)

    naver_momentum = calculate_momentum(
        RAW_DIR / "naver_trends.csv",
        "naver",
    )

    google_momentum = calculate_momentum(
        RAW_DIR / "google_trends.csv",
        "google",
    )

    features = master.merge(
        naver_momentum,
        on="keyword",
        how="left",
    )

    features = features.merge(
        google_momentum,
        on="keyword",
        how="left",
    )

    # Reduce the effect of extreme momentum values.
    features["naver_momentum_pct"] = (
        features["naver_momentum_pct"].clip(-100, 300)
    )

    features["google_momentum_pct"] = (
        features["google_momentum_pct"].clip(-100, 300)
    )

    # Current interest scores
    features = add_category_scores(
        features,
        "naver_avg",
        "naver_interest_score",
    )

    features = add_category_scores(
        features,
        "google_avg",
        "google_interest_score",
    )

    features["current_interest"] = features.apply(
        lambda row: calculate_weighted_average(
            row,
            {
                "naver_interest_score": 0.5,
                "google_interest_score": 0.5,
            },
        ),
        axis=1,
    )

    # Momentum scores
    features = add_category_scores(
        features,
        "naver_momentum_pct",
        "naver_momentum_score",
    )

    features = add_category_scores(
        features,
        "google_momentum_pct",
        "google_momentum_score",
    )

    features["momentum"] = features.apply(
        lambda row: calculate_weighted_average(
            row,
            {
                "naver_momentum_score": 0.5,
                "google_momentum_score": 0.5,
            },
        ),
        axis=1,
    )

    # Creator attention
    features["log_total_views"] = np.log1p(
        features["total_views"]
    )

    features = add_category_scores(
        features,
        "log_total_views",
        "creator_attention",
    )

    # Cross-market alignment
    both_available = (
        features["naver_momentum_score"].notna()
        & features["google_momentum_score"].notna()
    )

    features["cross_market_alignment"] = np.nan

    features.loc[
        both_available,
        "cross_market_alignment",
    ] = (
        100
        - (
            features.loc[both_available, "naver_momentum_score"]
            - features.loc[both_available, "google_momentum_score"]
        ).abs()
    ).clip(0, 100)

    # Data coverage
    signal_columns = [
        "naver_interest_score",
        "google_interest_score",
        "naver_momentum_score",
        "google_momentum_score",
        "creator_attention",
    ]

    features["available_signals"] = (
        features[signal_columns].notna().sum(axis=1)
    )

    features["data_coverage_pct"] = (
        features["available_signals"]
        / len(signal_columns)
        * 100
    )

    selected_columns = [
        "keyword",
        "korean_keyword",
        "category",
        "naver_avg",
        "google_avg",
        "total_views",
        "naver_recent_avg",
        "naver_previous_avg",
        "naver_momentum_pct",
        "google_recent_avg",
        "google_previous_avg",
        "google_momentum_pct",
        "naver_interest_score",
        "google_interest_score",
        "current_interest",
        "naver_momentum_score",
        "google_momentum_score",
        "momentum",
        "creator_attention",
        "cross_market_alignment",
        "available_signals",
        "data_coverage_pct",
    ]

    features = features[selected_columns]

    features = features.sort_values(
        ["category", "keyword"]
    ).reset_index(drop=True)

    numeric_columns = features.select_dtypes(
        include="number"
    ).columns

    features[numeric_columns] = features[
        numeric_columns
    ].round(2)

    output_path = PROCESSED_DIR / "features.csv"
    features.to_csv(output_path, index=False)

    print(f"Saved {len(features)} rows to {output_path}")
    print()
    print(
        features[
            [
                "keyword",
                "category",
                "current_interest",
                "momentum",
                "creator_attention",
                "cross_market_alignment",
                "data_coverage_pct",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()