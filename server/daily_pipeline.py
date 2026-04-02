from __future__ import annotations

import argparse
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path


def parse_hhmm(value: str) -> tuple[int, int]:
    try:
        hour_text, minute_text = value.split(":", 1)
        hour = int(hour_text)
        minute = int(minute_text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Time must be in HH:MM format") from exc

    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise argparse.ArgumentTypeError("Hour must be 0-23 and minute must be 0-59")

    return hour, minute


def next_run_at(now: datetime, run_time: tuple[int, int]) -> datetime:
    hour, minute = run_time
    scheduled = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if scheduled <= now:
        scheduled += timedelta(days=1)
    return scheduled


def run_step(script_path: Path, extra_args: list[str]) -> None:
    command = [sys.executable, str(script_path), *extra_args]
    subprocess.run(command, check=True)


def run_pipeline(project_dir: Path, scraper_args: list[str], translator_args: list[str]) -> None:
    print(f"[{datetime.now().isoformat(timespec='seconds')}] Starting daily pipeline")
    run_step(project_dir / "scraper.py", scraper_args)
    run_step(project_dir / "translate_to_english.py", translator_args)
    print(f"[{datetime.now().isoformat(timespec='seconds')}] Daily pipeline completed")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run ENCAR scraping and translation once per day."
    )
    parser.add_argument(
        "--time",
        type=parse_hhmm,
        default=parse_hhmm("03:00"),
        help="Daily run time in local server time, format HH:MM. Default: 03:00",
    )
    parser.add_argument(
        "--run-now",
        action="store_true",
        help="Run immediately once before entering the daily schedule loop.",
    )
    parser.add_argument(
        "--scraper-arg",
        action="append",
        default=[],
        help="Extra argument to pass to scraper.py. Can be repeated.",
    )
    parser.add_argument(
        "--translator-arg",
        action="append",
        default=[],
        help="Extra argument to pass to translate_to_english.py. Can be repeated.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_dir = Path(__file__).resolve().parent

    if args.run_now:
        run_pipeline(project_dir, args.scraper_arg, args.translator_arg)

    while True:
        now = datetime.now()
        scheduled = next_run_at(now, args.time)
        sleep_seconds = max(1, int((scheduled - now).total_seconds()))
        print(
            f"[{now.isoformat(timespec='seconds')}] "
            f"Next run scheduled for {scheduled.isoformat(timespec='seconds')}"
        )
        time.sleep(sleep_seconds)
        run_pipeline(project_dir, args.scraper_arg, args.translator_arg)


if __name__ == "__main__":
    main()
