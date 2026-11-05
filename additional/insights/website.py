"""Fetch a few public pages from a contractor website (decision D12).

Rules: respect robots.txt, at most 4 pages, 8-second timeout for each
request, same domain only. Page text stays in memory and is not stored.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

USER_AGENT = "RoofingLeadIntel/0.1 (sales research demo; respects robots.txt)"
TIMEOUT_S = 8
MAX_PAGES = 4
MAX_CHARS = 4000
LINK_WORDS = re.compile(r"about|team|staff|leadership|contact|who-we-are|our-company|owner|meet", re.I)


@dataclass
class Page:
    url: str
    text: str


def _allowed(robots: RobotFileParser | None, url: str) -> bool:
    return robots is None or robots.can_fetch(USER_AGENT, url)


def _robots(base: str) -> RobotFileParser | None:
    rp = RobotFileParser()
    try:
        resp = requests.get(urljoin(base, "/robots.txt"), timeout=TIMEOUT_S, headers={"User-Agent": USER_AGENT})
    except requests.RequestException:
        return None  # no robots.txt reachable: the standard treats this as allowed
    if resp.status_code >= 400:
        return None
    rp.parse(resp.text.splitlines())
    return rp


def page_text(html: str) -> tuple[str, BeautifulSoup]:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg", "iframe"]):
        tag.decompose()
    text = re.sub(r"\s+", " ", soup.get_text(" ")).strip()
    return text[:MAX_CHARS], soup


def fetch_page(url: str, robots: RobotFileParser | None) -> tuple[Page | None, BeautifulSoup | None]:
    if not _allowed(robots, url):
        log.info("robots.txt does not allow %s", url)
        return None, None
    try:
        resp = requests.get(url, timeout=TIMEOUT_S, headers={"User-Agent": USER_AGENT}, allow_redirects=True)
    except requests.RequestException as exc:
        log.info("Fetch failed for %s: %s", url, type(exc).__name__)
        return None, None
    if resp.status_code != 200 or "html" not in resp.headers.get("content-type", ""):
        return None, None
    text, soup = page_text(resp.text)
    return Page(url=resp.url, text=text), soup


def fetch_site(website_url: str) -> list[Page]:
    """Return up to MAX_PAGES pages: the homepage and its about, team or contact pages."""
    base = f"{urlparse(website_url).scheme}://{urlparse(website_url).netloc}"
    domain = urlparse(website_url).netloc.removeprefix("www.")
    robots = _robots(base)
    home, soup = fetch_page(website_url, robots)
    if home is None:
        return []
    pages = [home]
    seen = {home.url.rstrip("/")}
    candidates = []
    for a in soup.find_all("a", href=True):
        href = urljoin(home.url, a["href"]).split("#")[0]
        if urlparse(href).netloc.removeprefix("www.") != domain:
            continue
        if LINK_WORDS.search(href) or LINK_WORDS.search(a.get_text(" ")):
            if href.rstrip("/") not in seen:
                seen.add(href.rstrip("/"))
                candidates.append(href)
    for href in candidates[: MAX_PAGES - 1]:
        page, _ = fetch_page(href, robots)
        if page:
            pages.append(page)
    return pages
