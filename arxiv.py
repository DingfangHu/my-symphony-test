#!/usr/bin/env python3
"""Fetch and print today's article titles from arxiv astro-ph.HE."""

import urllib.request
import re
import sys
from datetime import datetime, timedelta

URL = "https://arxiv.org/list/astro-ph.HE/recent"


def _format_arxiv_date(dt: datetime) -> str:
    """Format a datetime as arxiv heading style: 'Thu, 30 Apr 2026'."""
    return dt.strftime("%a, ") + str(dt.day) + dt.strftime(" %b %Y")


def _get_headings() -> tuple[str, str]:
    """Return (today_heading, yesterday_heading) based on current date."""
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    return _format_arxiv_date(today), _format_arxiv_date(yesterday)


def fetch_page(url: str) -> str:
    """Fetch the arxiv listing page and return its HTML content."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; arxiv-scraper/1.0)"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def extract_today_section(html: str, today_heading: str, yesterday_heading: str) -> str | None:
    """Extract the HTML section between today's heading and yesterday's heading."""
    pattern = (
        re.escape(today_heading)
        + r".*?</h3>\s*(.*?)<h3.*?>"
        + re.escape(yesterday_heading)
    )
    match = re.search(pattern, html, re.DOTALL)
    if match:
        return match.group(1)
    return None


def extract_titles(section: str) -> list[str]:
    """Extract article titles from the given HTML section."""
    titles = re.findall(
        r"<span class='descriptor'>Title:</span>\s*(.*?)\s*</div>",
        section,
        re.DOTALL,
    )
    cleaned = []
    for t in titles:
        t = re.sub(r"<[^>]*>", "", t)
        t = re.sub(r"\s+", " ", t)
        t = t.strip()
        cleaned.append(t)
    return cleaned


def main() -> None:
    """Main entry: fetch page, extract today's titles, and print them."""
    today_heading, yesterday_heading = _get_headings()

    try:
        html = fetch_page(URL)
    except Exception as e:
        print(f"Error fetching page: {e}", file=sys.stderr)
        sys.exit(1)

    section = extract_today_section(html, today_heading, yesterday_heading)
    if section is None:
        print(
            f"Could not find today's ({today_heading}) article section.",
            file=sys.stderr,
        )
        sys.exit(1)

    titles = extract_titles(section)
    if not titles:
        print("No article titles found for today.", file=sys.stderr)
        sys.exit(0)

    print(f"Articles updated on {today_heading} ({len(titles)} found):\n")
    for i, title in enumerate(titles, 1):
        print(f"  {i}. {title}")


if __name__ == "__main__":
    main()
