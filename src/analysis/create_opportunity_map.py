import matplotlib.pyplot as plt
import pandas as pd
from adjustText import adjust_text

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
        "Run calculate_scores.py first."
    )

df = pd.read_csv(input_path)

required_columns = {
    "keyword",
    "category",
    "current_interest",
    "momentum",
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
# CHART SETTINGS
# ============================================================

x_mid = df["current_interest"].median()
y_mid = df["momentum"].median()

x_min = max(
    0,
    df["current_interest"].min() - 8,
)

x_max = min(
    105,
    df["current_interest"].max() + 12,
)

y_min = max(
    0,
    df["momentum"].min() - 8,
)

y_max = min(
    105,
    df["momentum"].max() + 12,
)

top_labels = df.nsmallest(
    10,
    "overall_rank",
)


# ============================================================
# CREATE FIGURE
# ============================================================

fig, ax = plt.subplots(figsize=(14, 10))

ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)


# ============================================================
# SOFT QUADRANT BACKGROUNDS
# ============================================================

ax.axvspan(
    x_min,
    x_mid,
    ymin=0,
    ymax=(y_mid - y_min) / (y_max - y_min),
    color="#F8FAFC",
    alpha=1,
    zorder=0,
)

ax.axvspan(
    x_min,
    x_mid,
    ymin=(y_mid - y_min) / (y_max - y_min),
    ymax=1,
    color="#FFF7ED",
    alpha=0.75,
    zorder=0,
)

ax.axvspan(
    x_mid,
    x_max,
    ymin=0,
    ymax=(y_mid - y_min) / (y_max - y_min),
    color="#EFF6FF",
    alpha=0.75,
    zorder=0,
)

ax.axvspan(
    x_mid,
    x_max,
    ymin=(y_mid - y_min) / (y_max - y_min),
    ymax=1,
    color="#ECFDF5",
    alpha=0.85,
    zorder=0,
)


# ============================================================
# BUBBLES
# ============================================================

for category, group in df.groupby("category"):

    category_color = COLORS.get(
        category,
        "#9CA3AF",
    )

    category_label = CATEGORY_LABELS.get(
        category,
        format_keyword(category),
    )

    bubble_sizes = 80 + (
        group["opportunity_score"] ** 1.45
    ) * 2.4

    ax.scatter(
        group["current_interest"],
        group["momentum"],
        s=bubble_sizes,
        color=category_color,
        alpha=0.78,
        edgecolors="white",
        linewidth=1.4,
        label=category_label,
        zorder=3,
    )


# ============================================================
# MEDIAN DIVIDERS
# ============================================================

ax.axvline(
    x_mid,
    color=COLORS["secondary"],
    linestyle=(0, (4, 5)),
    linewidth=1.3,
    alpha=0.75,
    zorder=2,
)

ax.axhline(
    y_mid,
    color=COLORS["secondary"],
    linestyle=(0, (4, 5)),
    linewidth=1.3,
    alpha=0.75,
    zorder=2,
)


# ============================================================
# TOP 10 LABELS
# ============================================================

texts = []

for _, row in top_labels.iterrows():

    text = ax.text(
        row["current_interest"],
        row["momentum"],
        f"{int(row['overall_rank'])}. {row['keyword_display']}",
        fontsize=9.5,
        weight="bold",
        color=COLORS["dark"],
        zorder=5,
    )

    texts.append(text)

adjust_text(
    texts,
    ax=ax,
    expand_text=(1.15, 1.25),
    expand_points=(1.4, 1.5),
    force_text=(0.4, 0.5),
    force_points=(0.3, 0.4),
    arrowprops={
        "arrowstyle": "-",
        "color": "#9CA3AF",
        "linewidth": 0.8,
        "alpha": 0.8,
    },
)


# ============================================================
# QUADRANT LABELS
# ============================================================

quadrant_style = {
    "fontsize": 13,
    "weight": "bold",
    "color": COLORS["secondary"],
    "alpha": 0.85,
}

ax.text(
    x_min + 2,
    y_max - 5,
    "EMERGING\nOPPORTUNITIES",
    ha="left",
    va="top",
    **quadrant_style,
)

ax.text(
    x_mid + 2,
    y_max - 5,
    "HIGH-PRIORITY\nOPPORTUNITIES",
    ha="left",
    va="top",
    **quadrant_style,
)

ax.text(
    x_min + 2,
    y_min + 4,
    "LOWER PRIORITY",
    ha="left",
    va="bottom",
    **quadrant_style,
)

ax.text(
    x_mid + 2,
    y_min + 4,
    "ESTABLISHED\nMARKETS",
    ha="left",
    va="bottom",
    **quadrant_style,
)


# ============================================================
# TITLES AND LABELS
# ============================================================

fig.text(
    0.07,
    0.965,
    "K-Beauty Opportunity Map",
    fontsize=24,
    weight="bold",
    color=COLORS["dark"],
    ha="left",
    va="top",
)

fig.text(
    0.07,
    0.925,
    (
        "Higher and further right indicates stronger momentum "
        "and greater current consumer interest."
    ),
    fontsize=11,
    color=COLORS["secondary"],
    ha="left",
    va="top",
)

ax.set_xlabel(
    "Current Interest Score",
    fontsize=12,
    labelpad=14,
)

ax.set_ylabel(
    "Momentum Score",
    fontsize=12,
    labelpad=14,
)

ax.tick_params(
    axis="both",
    length=0,
)

ax.grid(
    True,
    color=COLORS["grid"],
    linewidth=0.7,
    alpha=0.6,
    zorder=1,
)


# ============================================================
# LEGEND
# ============================================================

legend = ax.legend(
    title="Opportunity Type",
    loc="upper left",
    bbox_to_anchor=(0.01, 0.91),
    fontsize=10,
    title_fontsize=10,
    frameon=True,
    facecolor="white",
    edgecolor=COLORS["grid"],
)

legend.get_frame().set_alpha(0.95)


# ============================================================
# FOOTNOTE
# ============================================================

fig.text(
    0.07,
    0.025,
    (
        "Bubble size represents Opportunity Score. "
        "Only the top 10 ranked opportunities are labeled."
    ),
    fontsize=9.5,
    color=COLORS["secondary"],
)

plt.tight_layout(rect=[0.05, 0.06, 0.98, 0.88])

save_figure(fig, "opportunity_map.png")

print("Opportunity map created successfully.")