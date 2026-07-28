from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "outputs"


CATEGORY_TITLES = {
    "consumer_need": "Top Consumer Needs",
    "ingredient": "Top Ingredients",
    "product_format": "Top Product Formats",
}


def save_bar_chart(
    df: pd.DataFrame,
    title: str,
    filename: str,
    top_n: int = 8,
) -> None:
    chart_data = (
        df.sort_values("opportunity_score", ascending=False)
        .head(top_n)
        .sort_values("opportunity_score", ascending=True)
    )

    plt.figure(figsize=(10, 6))
    plt.barh(
        chart_data["keyword"],
        chart_data["opportunity_score"],
    )

    plt.title(title, fontsize=16, pad=15)
    plt.xlabel("Opportunity Score")
    plt.xlim(0, 100)

    for index, value in enumerate(chart_data["opportunity_score"]):
        plt.text(
            value + 1,
            index,
            f"{value:.1f}",
            va="center",
        )

    plt.tight_layout()
    plt.savefig(
        OUTPUT_DIR / filename,
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()


def create_opportunity_matrix(df: pd.DataFrame) -> None:
    matrix = df.pivot_table(
        index="keyword",
        columns="category",
        values="opportunity_score",
        aggfunc="mean",
    )

    matrix = matrix.rename(
        columns={
            "consumer_need": "Consumer Need",
            "ingredient": "Ingredient",
            "product_format": "Product Format",
        }
    )

    matrix = matrix.sort_index()

    plt.figure(figsize=(10, 12))
    plt.imshow(matrix.fillna(0), aspect="auto")

    plt.colorbar(label="Opportunity Score")
    plt.xticks(
        range(len(matrix.columns)),
        matrix.columns,
        rotation=20,
    )
    plt.yticks(
        range(len(matrix.index)),
        matrix.index,
    )

    plt.title(
        "K-Beauty Opportunity Matrix",
        fontsize=16,
        pad=15,
    )

    for row_index in range(len(matrix.index)):
        for column_index in range(len(matrix.columns)):
            value = matrix.iloc[row_index, column_index]

            if pd.notna(value):
                plt.text(
                    column_index,
                    row_index,
                    f"{value:.1f}",
                    ha="center",
                    va="center",
                )

    plt.tight_layout()
    plt.savefig(
        OUTPUT_DIR / "opportunity_matrix.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    input_path = PROCESSED_DIR / "opportunity_scores.csv"
    df = pd.read_csv(input_path)

    save_bar_chart(
        df=df,
        title="Overall K-Beauty Opportunity Ranking",
        filename="overall_ranking.png",
        top_n=12,
    )

    for category, title in CATEGORY_TITLES.items():
        category_df = df[df["category"] == category]

        save_bar_chart(
            df=category_df,
            title=title,
            filename=f"{category}.png",
            top_n=8,
        )

    create_opportunity_matrix(df)

    print(f"Saved charts to {OUTPUT_DIR}")

    for file_name in [
        "overall_ranking.png",
        "consumer_need.png",
        "ingredient.png",
        "product_format.png",
        "opportunity_matrix.png",
    ]:
        print(f"  - {file_name}")


if __name__ == "__main__":
    main()