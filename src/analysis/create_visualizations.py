import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from plotting import (
    CATEGORY_LABELS,
    COLORS,
    DATA_DIR,
    apply_project_style,
    format_keyword,
    save_figure,
)


apply_project_style()


# ============================================================
# LOAD DATA
# ============================================================

input_path = DATA_DIR / "opportunity_scores.csv"

if not input_path.exists():
    raise FileNotFoundError(
        f"Could not find {input_path}. "
        "Run calculate_scores.py before creating visualizations."
    )

df = pd.read_csv(input_path)

required_columns = {
    "keyword",
    "category",
    "opportunity_score",
    "overall_rank",
}

missing_columns = required_columns - set(df.columns)

if missing_columns:
    raise ValueError(
        "The opportunity score file is missing these columns: "
        f"{sorted(missing_columns)}"
    )

df["keyword_display"] = df["keyword"].apply(format_keyword)


# ============================================================
# HELPER FUNCTION: PROFESSIONAL BAR CHART
# ============================================================

def create_ranked_bar_chart(
    chart_df: pd.DataFrame,
    title: str,
    subtitle: str,
    filename: str,
    bar_color: str,
    max_items: int = 10,
    highlight_top_three: bool = False,
) -> None:

    chart_df = (
        chart_df.sort_values("opportunity_score", ascending=False)
        .head(max_items)
        .copy()
    )

    chart_df = chart_df.sort_values(
        "opportunity_score",
        ascending=True,
    )

    fig_height = max(6.5, len(chart_df) * 0.62)

    fig, ax = plt.subplots(figsize=(12, fig_height))

    colors = [bar_color] * len(chart_df)

    if highlight_top_three and len(chart_df) >= 3:
        top_indices = chart_df.nlargest(
            3,
            "opportunity_score",
        ).index

        colors = [
            COLORS["highlight"] if index in top_indices else bar_color
            for index in chart_df.index
        ]

    bars = ax.barh(
        chart_df["keyword_display"],
        chart_df["opportunity_score"],
        color=colors,
        height=0.58,
        alpha=0.95,
    )

    maximum_score = max(
        100,
        chart_df["opportunity_score"].max() * 1.18,
    )

    ax.set_xlim(0, maximum_score)

    ax.xaxis.grid(True)
    ax.yaxis.grid(False)

    ax.tick_params(
        axis="y",
        length=0,
        labelsize=11,
    )

    ax.tick_params(
        axis="x",
        length=0,
    )

    ax.set_xlabel(
        "Opportunity Score",
        fontsize=11,
        labelpad=12,
    )

    for bar, score in zip(
        bars,
        chart_df["opportunity_score"],
    ):
        ax.text(
            score + maximum_score * 0.012,
            bar.get_y() + bar.get_height() / 2,
            f"{score:.1f}",
            va="center",
            ha="left",
            fontsize=10,
            weight="bold",
            color=COLORS["dark"],
        )

    fig.text(
        0.08,
        0.965,
        title,
        fontsize=22,
        weight="bold",
        ha="left",
        va="top",
        color=COLORS["dark"],
    )

    fig.text(
        0.08,
        0.925,
        subtitle,
        fontsize=11,
        ha="left",
        va="top",
        color=COLORS["secondary"],
    )

    plt.tight_layout(rect=[0.07, 0.04, 0.98, 0.88])

    save_figure(fig, filename)


# ============================================================
# 1. OVERALL OPPORTUNITY RANKING
# ============================================================

overall_df = df.sort_values(
    "overall_rank",
    ascending=True,
).head(15)

create_ranked_bar_chart(
    chart_df=overall_df,
    title="Overall K-Beauty Opportunity Ranking",
    subtitle=(
        "Opportunity Score combines current demand, momentum, "
        "creator attention, and data reliability."
    ),
    filename="overall_ranking.png",
    bar_color="#9CA3AF",
    max_items=15,
    highlight_top_three=True,
)


# ============================================================
# 2. CATEGORY-SPECIFIC CHARTS
# ============================================================

category_files = {
    "consumer_need": "consumer_need.png",
    "ingredient": "ingredient.png",
    "product_format": "product_format.png",
}

category_titles = {
    "consumer_need": "Top Consumer Need Opportunities",
    "ingredient": "Top Ingredient Opportunities",
    "product_format": "Top Product Format Opportunities",
}

category_subtitles = {
    "consumer_need": (
        "Consumer concerns and skincare needs ranked by opportunity potential."
    ),
    "ingredient": (
        "Emerging and established ingredients ranked by market opportunity."
    ),
    "product_format": (
        "Product formats ranked using demand, momentum, and creator signals."
    ),
}

for category, filename in category_files.items():

    category_df = df[df["category"] == category].copy()

    if category_df.empty:
        print(
            f"Skipped {category}: "
            "no rows were found for this category."
        )
        continue

    create_ranked_bar_chart(
        chart_df=category_df,
        title=category_titles[category],
        subtitle=category_subtitles[category],
        filename=filename,
        bar_color=COLORS[category],
        max_items=10,
    )


# ============================================================
# 3. PROJECT SUMMARY DASHBOARD
# ============================================================

top_overall = df.sort_values(
    "overall_rank",
    ascending=True,
).iloc[0]

summary_values = {
    "Keywords Analyzed": len(df),
    "Data Sources": 3,
    "Top Opportunity": format_keyword(top_overall["keyword"]),
}

top_by_category = {}

for category in CATEGORY_LABELS:
    category_df = df[df["category"] == category]

    if not category_df.empty:
        top_row = category_df.sort_values(
            "opportunity_score",
            ascending=False,
        ).iloc[0]

        top_by_category[category] = top_row


fig, ax = plt.subplots(figsize=(14, 8))

ax.set_xlim(0, 14)
ax.set_ylim(0, 8)
ax.axis("off")

fig.text(
    0.07,
    0.90,
    "K-Beauty Product Opportunity Radar",
    fontsize=25,
    weight="bold",
    color=COLORS["dark"],
)

fig.text(
    0.07,
    0.845,
    (
        "A multi-source consumer signal analysis using "
        "Naver DataLab, Google Trends, and YouTube."
    ),
    fontsize=12,
    color=COLORS["secondary"],
)

cards = [
    {
        "x": 0.8,
        "y": 4.9,
        "width": 3.8,
        "height": 1.7,
        "label": "Keywords Analyzed",
        "value": str(summary_values["Keywords Analyzed"]),
        "color": COLORS["dark"],
    },
    {
        "x": 5.1,
        "y": 4.9,
        "width": 3.8,
        "height": 1.7,
        "label": "Data Sources",
        "value": str(summary_values["Data Sources"]),
        "color": COLORS["dark"],
    },
    {
        "x": 9.4,
        "y": 4.9,
        "width": 3.8,
        "height": 1.7,
        "label": "Top Opportunity",
        "value": summary_values["Top Opportunity"],
        "color": COLORS["highlight"],
    },
]

category_y = 2.25

for index, category in enumerate(CATEGORY_LABELS):

    if category not in top_by_category:
        continue

    row = top_by_category[category]

    cards.append(
        {
            "x": 0.8 + index * 4.3,
            "y": category_y,
            "width": 3.8,
            "height": 1.7,
            "label": f"Top {CATEGORY_LABELS[category]}",
            "value": format_keyword(row["keyword"]),
            "color": COLORS[category],
        }
    )

for card in cards:

    rectangle = plt.Rectangle(
        (card["x"], card["y"]),
        card["width"],
        card["height"],
        facecolor=COLORS["light_background"],
        edgecolor=COLORS["grid"],
        linewidth=1,
    )

    ax.add_patch(rectangle)

    ax.text(
        card["x"] + 0.25,
        card["y"] + card["height"] - 0.42,
        card["label"],
        fontsize=10,
        color=COLORS["secondary"],
        va="top",
    )

    ax.text(
        card["x"] + 0.25,
        card["y"] + 0.55,
        card["value"],
        fontsize=17,
        weight="bold",
        color=card["color"],
        va="center",
        wrap=True,
    )

fig.text(
    0.07,
    0.09,
    (
        "The model prioritizes opportunities with strong current demand, "
        "positive momentum, creator attention, and reliable data coverage."
    ),
    fontsize=10.5,
    color=COLORS["secondary"],
)

save_figure(fig, "project_summary.png")


print("All standard visualizations were created successfully.")