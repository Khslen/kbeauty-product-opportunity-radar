"""
YouTube Data API v3 collector.

Free tier is 10,000 "units"/day; a search.list call costs 100 units, so this
collector supports at most ~100 keyword searches/day on the free tier. With
~22 keywords in the default config, you're well within budget, but be mindful
if you expand the keyword list a lot.
"""
import os
import time
import pandas as pd
from datetime import datetime, timezone, timedelta
from googleapiclient.discovery import build

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from config.keywords import ALL_KEYWORDS
from src.utils import save_df, require_env


def fetch_youtube_mentions(days_back: int = 30, max_results: int = 25):
    require_env("YOUTUBE_API_KEY")
    youtube = build("youtube", "v3", developerKey=os.getenv("YOUTUBE_API_KEY"))

    published_after = (datetime.now(timezone.utc) - timedelta(days=days_back)) \
        .strftime("%Y-%m-%dT%H:%M:%SZ")
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    all_rows = []

    for kw in ALL_KEYWORDS:
        term = kw["en"]
        try:
            search_resp = youtube.search().list(
                q=term,
                part="id",
                type="video",
                order="date",
                publishedAfter=published_after,
                maxResults=max_results,
            ).execute()

            video_ids = [item["id"]["videoId"] for item in search_resp.get("items", [])]
            video_count = len(video_ids)
            total_views = 0

            if video_ids:
                stats_resp = youtube.videos().list(
                    part="statistics",
                    id=",".join(video_ids),
                ).execute()
                for item in stats_resp.get("items", []):
                    total_views += int(item["statistics"].get("viewCount", 0))

            all_rows.append({
                "source": "youtube",
                "keyword": term,
                "date": today_str,
                "window_days": days_back,
                "video_count": video_count,
                "total_views": total_views,
            })
            print(f"  ok: {term} -> {video_count} videos, {total_views} total views")

        except Exception as e:
            print(f"  ! error on '{term}': {e}")

        time.sleep(0.5)

    df = pd.DataFrame(all_rows)
    save_df(df, "youtube_mentions.csv")
    return df


if __name__ == "__main__":
    print("Fetching YouTube mentions...")
    fetch_youtube_mentions()
