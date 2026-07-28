"""
Naver DataLab Search Trend collector.

Docs: https://developers.naver.com/docs/serviceapi/datalab/search/search.md

This is the highest-signal source in this project: it's Korean search interest,
which is where K-beauty trends usually start before they go global. Almost no
one outside Korea builds this into a trend-prediction project, so it's a good
differentiator.

Rate limit: Naver allows up to 25,000 requests/day per app, and up to 5 keyword
groups per request. We batch keywords into groups of 5 to stay efficient.
"""
import os
import time
import requests
import pandas as pd
from datetime import date, timedelta

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from config.keywords import ALL_KEYWORDS
from src.utils import save_df, require_env

NAVER_URL = "https://openapi.naver.com/v1/datalab/search"


def _chunk(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


def fetch_naver_trends(start_date: str = None, end_date: str = None, time_unit: str = "week"):
    """
    start_date/end_date format: 'YYYY-MM-DD'. Defaults to the last 24 months.
    time_unit: 'date', 'week', or 'month'.
    """
    require_env("NAVER_CLIENT_ID", "NAVER_CLIENT_SECRET")
    headers = {
        "X-Naver-Client-Id": os.getenv("NAVER_CLIENT_ID"),
        "X-Naver-Client-Secret": os.getenv("NAVER_CLIENT_SECRET"),
        "Content-Type": "application/json",
    }

    if end_date is None:
        end_date = date.today().isoformat()
    if start_date is None:
        start_date = (date.today() - timedelta(days=730)).isoformat()

    all_rows = []

    for group in _chunk(ALL_KEYWORDS, 5):
        keyword_groups = [
            {"groupName": kw["en"], "keywords": [kw["kr"]]} for kw in group
        ]
        body = {
            "startDate": start_date,
            "endDate": end_date,
            "timeUnit": time_unit,
            "keywordGroups": keyword_groups,
        }
        resp = requests.post(NAVER_URL, headers=headers, json=body, timeout=15)
        if resp.status_code != 200:
            print(f"  ! Naver API error {resp.status_code} for group "
                  f"{[k['en'] for k in group]}: {resp.text[:200]}")
            continue

        results = resp.json().get("results", [])
        for result in results:
            keyword_en = result["title"]
            for point in result["data"]:
                all_rows.append({
                    "source": "naver_datalab",
                    "keyword": keyword_en,
                    "date": point["period"],
                    "value": point["ratio"],  # relative index, 0-100
                })

        time.sleep(0.3)  # be polite to the API

    df = pd.DataFrame(all_rows)
    save_df(df, "naver_trends.csv")
    return df


if __name__ == "__main__":
    print("Fetching Naver DataLab trends...")
    fetch_naver_trends()
