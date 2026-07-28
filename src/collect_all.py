"""
Run all three collectors in sequence and report what succeeded/failed.

Usage:
    python src/collect_all.py
    python src/collect_all.py --skip youtube   # run only naver + google

Each collector is independent and wrapped in a try/except so one failing
API (e.g. missing key, rate limit) doesn't stop the others from running.
"""
import argparse
from dotenv import load_dotenv

load_dotenv()

from collectors.naver_trends import fetch_naver_trends
from collectors.google_trends import fetch_google_trends
from collectors.youtube_mentions import fetch_youtube_mentions

COLLECTORS = {
    "naver": fetch_naver_trends,
    "google": fetch_google_trends,
    "youtube": fetch_youtube_mentions,
}


class ExtendAction(argparse.Action):
    """Makes repeated --skip flags accumulate instead of each one overwriting
    the last. Without this, `--skip youtube --skip naver` silently only skips
    'naver' — a real footgun with argparse's default nargs='*' behavior."""
    def __call__(self, parser, namespace, values, option_string=None):
        items = list(getattr(namespace, self.dest, None) or [])
        items.extend(values)
        setattr(namespace, self.dest, items)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip", nargs="*", default=[], choices=COLLECTORS.keys(),
                         action=ExtendAction,
                         help="collectors to skip, e.g. --skip youtube "
                              "(can also repeat --skip multiple times)")
    args = parser.parse_args()

    results = {}
    for name, fn in COLLECTORS.items():
        if name in args.skip:
            print(f"\n=== Skipping {name} ===")
            continue
        print(f"\n=== Running {name} ===")
        try:
            fn()
            results[name] = "ok"
        except Exception as e:
            print(f"  ! {name} failed: {e}")
            results[name] = f"failed: {e}"

    print("\n=== Summary ===")
    for name, status in results.items():
        print(f"  {name}: {status}")


if __name__ == "__main__":
    main()