"""Validate time logs:
- CSV schema
- weekly sum <= 40 hours
- no banking enforced (policy; this script flags >40 only)
"""
import csv, sys
from collections import defaultdict
from datetime import datetime

REQUIRED = ["date","hours","repo","issue_or_pr","category","description","artifact_link"]

def week_key(dt):
    # ISO week
    iso = dt.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"

def main(path):
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        missing = [c for c in REQUIRED if c not in r.fieldnames]
        if missing:
            raise SystemExit(f"Missing columns: {missing}")
        totals = defaultdict(float)
        for row in r:
            dt = datetime.strptime(row["date"], "%Y-%m-%d").date()
            hrs = float(row["hours"])
            totals[week_key(dt)] += hrs
        bad = {k:v for k,v in totals.items() if v > 40.0 + 1e-9}
        if bad:
            raise SystemExit(f"Weekly cap exceeded: {bad}")
    print("OK")

if __name__ == "__main__":
    main(sys.argv[1])
