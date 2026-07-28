from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from adjustText import adjust_text


BASE_DIR = Path(__file__).resolve().parents[2]
PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(PROCESSED_DIR / "opportunity_scores.csv")

category_colors = {
    "consumer_need": "#1f77b4",
    "ingredient": "#ff7f0e",
    "product_format": "#2ca02c",
}

category_labels = {
    "consumer_need": "Consumer Need",
    "ingredient": "Ingredient",
    "product_format": "Product Format",
}

x_mid = df["current_interest"].median()
y_mid = df["momentum"].median()

top_10 = df.nsmallest(10, "overall_rank")

fig, ax = plt.subplots(figsize=(14, 10))

# Quadrant shading
ax.axvspan(
    0,
    x_mid,
    ymin=0,
    ymax=y_mid / 105,
    color="#ECEFF1",
    alpha=0.45,
)

ax.axvspan(
    0,
    x_mid,
    ymin=y_mid / 105,
    ymax=1,
    color="#FFF8E1",
    alpha=0.45,
)

ax.axvspan(
    x_mid,
    100,
    ymin=0,
    ymax=y_mid / 105,
    color="#E3F2FD",
    alpha=0.45,
)

ax.axvspan(
    x_mid,
    100,
    ymin=y_mid / 105,
    ymax=1,
    color="#E8F5E9",
    alpha=0.45,
)

# Bubbles by category
for category, group in df.groupby("category"):
    ax.scatter(
        group["current_interest"],
        group["momentum"],
        s=50 + group["opportunity_score"] * 20,
        color=category_colors[category],
        alpha=0.72,
        edgecolors="black",
        linewidth=0.6,
        label=category_labels[category],
        zorder=3,
    )

# Median divider lines
ax.axvline(
    x_mid,
    linestyle="--",
    linewidth=1.8,
    color="#444444",
    zorder=2,
)

ax.axhline(
    y_mid,
    linestyle="--",
    linewidth=1.8,
    color="#444444",
    zorder=2,
)

# Label top 10 only
texts = []

for _, row in top_10.iterrows():
    texts.append(
        ax.text(
            row["current_interest"],
            row["momentum"],
            f"{int(row['overall_rank'])}. {row['keyword']}",
            fontsize=9,
            zorder=4,
        )
    )

adjust_text(
    texts,
    ax=ax,
    arrowprops=dict(
        arrowstyle="-",
        color="gray",
        lw=0.7,
        alpha=0.7,
    ),
)

# Quadrant labels
ax.text(
    x_mid + 4,
    y_mid + 25,
    "High Priority",
    fontsize=16,
    weight="bold",
)

ax.text(
    5,
    y_mid + 25,
    "Emerging Opportunities",
    fontsize=16,
    weight="bold",
)

ax.text(
    x_mid + 4,
    6,
    "Established Markets",
    fontsize=16,
    weight="bold",
)

ax.text(
    5,
    6,
    "Low Potential",
    fontsize=16,
    weight="bold",
)

# Title and subtitle
fig.suptitle(
    "K-Beauty Opportunity Map",
    fontsize=24,
    weight="bold",
    y=0.98,
)

ax.set_title(
    "Bubble size = Opportunity Score | Dashed lines = Median values",
    fontsize=12,
    color="#555555",
    pad=14,
)

ax.set_xlabel("Current Interest Score", fontsize=13)
ax.set_ylabel("Momentum Score", fontsize=13)

ax.set_xlim(0, 100)
ax.set_ylim(0, 105)

ax.grid(alpha=0.18)

ax.legend(
    title="Category",
    loc="upper left",
    frameon=True,
)

plt.tight_layout(rect=[0, 0, 1, 0.95])

output_path = OUTPUT_DIR / "opportunity_map.png"

plt.savefig(
    output_path,
    dpi=300,
    bbox_inches="tight",
)

plt.close()

print(f"Saved: {output_path}")