"""
Google Trends collector, via the `trendspy` library.

NOTE (July 2026): This used to run on `pytrends`, but that library's GitHub
repo was archived by its maintainers in April 2025 and is now permanently
unmaintained — it still installs, but any future Google backend changes will
never be patched. `trendspy` is an actively maintained alternative with a
similar interest_over_time() call shape. No API key needed, but Google will
still rate-limit aggressive scraping — this collector processes keywords one
at a time with a delay, and retries once on failure.
"""
import time
import pandas as pd
from trendspy import Trends

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from config.keywords import ALL_KEYWORDS
from src.utils import save_df


def fetch_google_trends(timeframe: str = "today 24-m", sleep_seconds: float = 8.0):
    # request_delay controls trendspy's internal pacing; the default (1.0s) is
    # too aggressive for a batch of 20+ keywords run back-to-back and causes
    # 429 rate-limit errors. max_retries lets trendspy itself retry with
    # backoff before we even get to our own retry loop below.
    tr = Trends(request_delay=6.0, max_retries=3)
    all_rows = []

    for kw in ALL_KEYWORDS:
        term = kw["en"]
        for attempt in range(2):
            try:
                df = tr.interest_over_time([term], timeframe=timeframe)
                if df is None or df.empty:
                    print(f"  ! no data for '{term}'")
                    break

                # trendspy names the column exactly after the keyword string
                value_col = term if term in df.columns else [
                    c for c in df.columns if c != "isPartial"
                ][0]

                for dt, row in df.iterrows():
                    all_rows.append({
                        "source": "google_trends",
                        "keyword": term,
                        "date": pd.Timestamp(dt).strftime("%Y-%m-%d"),
                        "value": row[value_col],
                    })
                print(f"  ok: {term}")
                break
            except Exception as e:
                print(f"  ! error on '{term}' (attempt {attempt + 1}): {e}")
                time.sleep(10)
        time.sleep(sleep_seconds)

    result = pd.DataFrame(all_rows)
    save_df(result, "google_trends.csv")
    return result


if __name__ == "__main__":
    print("Fetching Google Trends...")
    fetch_google_trends()