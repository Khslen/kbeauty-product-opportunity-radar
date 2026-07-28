from pathlib import Path
from datetime import datetime

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "outputs"

df = pd.read_csv(PROCESSED_DIR / "opportunity_scores.csv")

top10 = df.head(10)

consumer = (
    df[df["category"] == "consumer_need"]
    .sort_values("opportunity_score", ascending=False)
)

ingredients = (
    df[df["category"] == "ingredient"]
    .sort_values("opportunity_score", ascending=False)
)

formats = (
    df[df["category"] == "product_format"]
    .sort_values("opportunity_score", ascending=False)
)


def section(title):
    return f"\n## {title}\n\n"


report = f"""# K-Beauty Product Opportunity Radar

Generated: {datetime.now().strftime("%Y-%m-%d")}

---

## Executive Summary

This project combines Korean search behavior (Naver DataLab), global search interest (Google Trends), and creator attention (YouTube) to identify emerging K-beauty opportunities.

The Opportunity Score combines:

- Current Interest (30%)
- Momentum (40%)
- Creator Attention (20%)
- Cross-Market Alignment (10%)

---

"""

report += section("Top 10 Opportunities")

for _, row in top10.iterrows():
    report += (
        f"{int(row['overall_rank'])}. "
        f"**{row['keyword']}** "
        f"({row['category']}) — "
        f"{row['opportunity_score']:.1f}\n"
    )

report += section("Top Consumer Needs")

for _, row in consumer.head(5).iterrows():
    report += (
        f"- {row['keyword']} ({row['opportunity_score']:.1f})\n"
    )

report += section("Top Ingredients")

for _, row in ingredients.head(5).iterrows():
    report += (
        f"- {row['keyword']} ({row['opportunity_score']:.1f})\n"
    )

report += section("Top Product Formats")

for _, row in formats.head(5).iterrows():
    report += (
        f"- {row['keyword']} ({row['opportunity_score']:.1f})\n"
    )

report += """

## Business Recommendations

1. Prioritize ingredients with high momentum rather than only high popularity.

2. Focus on opportunities supported by both Korean and global demand.

3. Combine high-scoring consumer needs with high-scoring ingredients when planning new products.

4. Validate promising opportunities using TikTok and Amazon before product launch.

---

## Charts

See the following figures in the outputs folder:

- overall_ranking.png
- consumer_need.png
- ingredient.png
- product_format.png
- opportunity_matrix.png

"""

output = OUTPUT_DIR / "portfolio_report.md"

with open(output, "w", encoding="utf-8") as f:
    f.write(report)

print(f"Report saved to {output}")