#!/usr/bin/env python3
"""Fetch and print today's (30 Apr 2026) article titles from arxiv astro-ph.HE."""

import urllib.request
import re
import sys

URL = "https://arxiv.org/list/astro-ph.HE/recent"
TODAY_HEADING = "Thu, 30 Apr 2026"
YESTERDAY_HEADING = "Wed, 29 Apr 2026"


def fetch_page(url: str) -> str:
    """Fetch the arxiv listing page and return its HTML content."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; arxiv-scraper/1.0)"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def extract_today_section(html: str) -> str | None:
    """Extract the HTML section between today's heading and yesterday's heading."""
    pattern = (
        re.escape(TODAY_HEADING)
        + r".*?</h3>\s*(.*?)<h3.*?>"
        + re.escape(YESTERDAY_HEADING)
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
    try:
        html = fetch_page(URL)
    except Exception as e:
        print(f"Error fetching page: {e}", file=sys.stderr)
        sys.exit(1)

    section = extract_today_section(html)
    if section is None:
        print(
            f"Could not find today's ({TODAY_HEADING}) article section.",
            file=sys.stderr,
        )
        sys.exit(1)

    titles = extract_titles(section)
    if not titles:
        print("No article titles found for today.", file=sys.stderr)
        sys.exit(0)

    print(f"Articles updated on {TODAY_HEADING} ({len(titles)} found):\n")
    for i, title in enumerate(titles, 1):
        print(f"  {i}. {title}")


if __name__ == "__main__":
    main()
