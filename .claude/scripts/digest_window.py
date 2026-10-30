#!/usr/bin/env python3
"""Work out which time window the morning digest should cover.

  digest_window.py            print the window (start and end, ISO) as JSON; writes nothing
  digest_window.py --record   save now as the last digest run (call only after a digest is written)

The window starts at the last recorded run, so a Monday run covers the weekend. With no record it
covers the last 24 hours, and it never reaches back more than 7 days.
State lives in .claude/state/digest.json.
"""
import argparse
import json
import os
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_STATE = os.path.join(HERE, "..", "state", "digest.json")
DEFAULT_LOOKBACK = timedelta(hours=24)
MAX_LOOKBACK = timedelta(days=7)


def _last_run(state_file):
    try:
        with open(state_file, encoding="utf-8") as fh:
            return datetime.fromisoformat(json.load(fh)["last_run"])
    except (OSError, ValueError, KeyError):
        return None


def window(state_file, now):
    last = _last_run(state_file)
    if last is None or last > now:
        start = now - DEFAULT_LOOKBACK
    else:
        start = max(last, now - MAX_LOOKBACK)
    return start, now


def record(state_file, now):
    os.makedirs(os.path.dirname(state_file), exist_ok=True)
    with open(state_file, "w", encoding="utf-8") as fh:
        json.dump({"last_run": now.isoformat(timespec="seconds")}, fh)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", action="store_true")
    ap.add_argument("--state", default=DEFAULT_STATE)
    args = ap.parse_args()
    now = datetime.now().replace(microsecond=0)
    if args.record:
        record(args.state, now)
        print("recorded %s" % now.isoformat())
        return
    start, end = window(args.state, now)
    print(json.dumps({"start": start.isoformat(), "end": end.isoformat()}))


if __name__ == "__main__":
    main()
