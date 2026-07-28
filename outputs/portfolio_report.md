# K-Beauty Product Opportunity Radar

## Executive Summary

How can cosmetic brands identify emerging product opportunities before they become saturated?

This project combines Korean consumer search behavior (Naver DataLab), global search interest (Google Trends), and creator attention (YouTube) to build a data-driven Opportunity Score for K-beauty trends.

Rather than measuring popularity alone, the model evaluates both current demand and growth momentum to identify product opportunities that may deserve further investment.

---

# Business Problem

Beauty brands constantly face the same question:

> Which skincare trend should we invest in next?

Launching products too late often means entering a crowded market, while launching too early increases risk.

The goal of this project is to build a simple decision-support tool that helps marketing and product teams prioritize opportunities using publicly available consumer data.

---

# Data Sources

| Source | Purpose |
|---------|----------|
| Naver DataLab | Korean consumer search demand |
| Google Trends | Global search demand |
| YouTube Data API | Creator attention and discussion |

---

# Methodology

The project follows the pipeline below.

Raw Data

↓

Data Cleaning

↓

Feature Engineering

↓

Opportunity Score

↓

Business Insights

Three types of skincare signals were analyzed.

- Consumer Needs
- Ingredients
- Product Formats

For each keyword, the following features were calculated.

- Current Interest
- Momentum
- Creator Attention
- Data Coverage

The final Opportunity Score combines these signals into a single ranking.

---

# Key Findings

### Consumer Needs

The strongest consumer needs identified were:

- Skin Barrier
- Sensitive Skin
- Hyperpigmentation

These topics showed consistently high consumer interest across multiple data sources.

---

### Ingredients

The highest opportunity ingredients were:

- Panthenol
- PDRN
- Tranexamic Acid

Panthenol and PDRN showed particularly strong momentum, suggesting growing consumer interest rather than simply mature popularity.

---

### Product Formats

The leading product formats were:

- Korean Serum
- Sunscreen Stick
- Korean Ampoule

These formats continue to receive strong search activity while maintaining creator attention.

---

# Business Recommendations

Based on the results, a cosmetics company could prioritize products combining:

Consumer Need

↓

Ingredient

↓

Format

For example:

Sensitive Skin

↓

Panthenol

↓

Serum

or

Skin Barrier

↓

PDRN

↓

Cream

These concepts align with current consumer demand while maintaining positive growth momentum.

---

# Limitations

Several limitations should be considered.

- Public search data does not directly measure sales.
- Google Trends may occasionally return incomplete data because of API rate limits.
- YouTube reflects creator attention rather than consumer purchases.
- Opportunity Scores should support business decisions rather than replace market research.

---

# Future Improvements

Possible extensions include:

- Amazon review analysis
- Olive Young rankings
- TikTok creator signals
- Product launch timeline analysis
- Brand-level competitive analysis

---

# Conclusion

This project demonstrates how publicly available consumer signals can be transformed into actionable business insights.

Rather than focusing solely on data collection or visualization, the project emphasizes translating multiple data sources into practical recommendations for marketing and product strategy.