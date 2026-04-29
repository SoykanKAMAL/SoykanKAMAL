#!/usr/bin/env python3
"""Rewrite the <tspan id="uptime_data"> in profile.svg with the current
duration since the game-dev start date. Run by .github/workflows/today.yml
on a daily cron.
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

START_DATE = date(2019, 7, 1)
SVG_PATH = Path(__file__).parent / "profile.svg"


def days_in_month(year: int, month: int) -> int:
    if month == 2:
        leap = (year % 4 == 0 and year % 100 != 0) or year % 400 == 0
        return 29 if leap else 28
    if month in (4, 6, 9, 11):
        return 30
    return 31


def relative_time(start: date, end: date) -> str:
    years = end.year - start.year
    months = end.month - start.month
    days = end.day - start.day

    if days < 0:
        months -= 1
        prev_year = end.year if end.month != 1 else end.year - 1
        prev_month = end.month - 1 or 12
        days += days_in_month(prev_year, prev_month)

    if months < 0:
        years -= 1
        months += 12

    def unit(n: int, label: str) -> str:
        return f"{n} {label}{'s' if n != 1 else ''}"

    return f"{unit(years, 'year')}, {unit(months, 'month')}, {unit(days, 'day')}"


def main() -> int:
    svg = SVG_PATH.read_text()
    new_text = relative_time(START_DATE, date.today())
    pattern = re.compile(r'(<tspan[^>]*id="uptime_data"[^>]*>)[^<]*(</tspan>)')
    new_svg, n = pattern.subn(rf"\g<1>{new_text}\g<2>", svg)
    if n == 0:
        print("uptime_data tspan not found", file=sys.stderr)
        return 1
    if new_svg != svg:
        SVG_PATH.write_text(new_svg)
        print(f"Updated uptime: {new_text}")
    else:
        print(f"No change needed (already {new_text})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
