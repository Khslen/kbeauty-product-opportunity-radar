"""Shared helpers for the collectors."""
import os
import pandas as pd
from pathlib import Path

DATA_RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def ensure_data_dir():
    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)


def save_df(df: pd.DataFrame, filename: str):
    """Append-or-create a CSV in data/raw/, tagged with today's collection date."""
    ensure_data_dir()
    path = DATA_RAW_DIR / filename
    if path.exists() and path.stat().st_size > 0:
        try:
            existing = pd.read_csv(path)
            df = pd.concat([existing, df], ignore_index=True)
            df = df.drop_duplicates()
        except pd.errors.EmptyDataError:
            # File exists but has no columns/rows (e.g. a prior run collected
            # 0 results) — treat it as if there were no prior file at all.
            pass
    if df.empty:
        print(f"  ! no data collected — not overwriting {path} with an empty file")
        return
    df.to_csv(path, index=False)
    print(f"  -> saved {len(df)} total rows to {path}")


def require_env(*names):
    """Fail loudly and clearly if required env vars are missing, instead of
    letting a collector fail deep inside an API call with a confusing error."""
    missing = [n for n in names if not os.getenv(n)]
    if missing:
        raise EnvironmentError(
            f"Missing required environment variable(s): {', '.join(missing)}. "
            f"Check your .env file against .env.example."
        )