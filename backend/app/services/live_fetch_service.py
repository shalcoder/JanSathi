"""
Live fetch service for near-real-time scheme information.

This service only fetches from known official public sources and returns
short extracted snippets for grounding answers.
"""

from __future__ import annotations

import re
import time
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


class LiveFetchService:
    def __init__(self) -> None:
        # Keep live lookups fast so chat latency stays low.
        self.timeout: Tuple[int, int] = (2, 4)
        self.ttl_seconds = 600
        self._cache: Dict[str, Tuple[float, List[str]]] = {}
        self._headers = {
            "User-Agent": "JanSathiLiveFetch/1.0 (+https://myscheme.gov.in)",
            "Accept-Language": "en-IN,en;q=0.9",
        }

        # Restrict web answers to trusted official domains.
        self.allowed_domains = [
            "gov.in",
            "nic.in",
            "myscheme.gov.in",
            "pmaymis.gov.in",
            "pmayg.nic.in",
            "pmkisan.gov.in",
            "pfms.nic.in",
            "eshram.gov.in",
            "pmjay.gov.in",
            "nfsa.gov.in",
        ]

        # Official sources only.
        self.scheme_sources = {
            "pm_awas_urban": [
                "https://pmaymis.gov.in/",
            ],
            "pm_kisan": [
                "https://pmkisan.gov.in/",
                "https://pmkisan.gov.in/BeneficiaryStatus_New.aspx",
            ],
            "e_shram": [
                "https://eshram.gov.in/",
            ],
            "ayushman": [
                "https://pmjay.gov.in/",
            ],
            "ration": [
                "https://nfsa.gov.in/",
            ],
            "generic": [
                "https://www.india.gov.in/",
                "https://www.myscheme.gov.in/",
            ],
        }

        # Optional RSS sources that are publicly available.
        self.rss_sources = [
            "https://www.india.gov.in/rss/",
        ]

    def fetch(self, query: str, scheme_hint: str = "unknown", max_items: int = 4) -> List[str]:
        q = (query or "").strip().lower()
        cache_key = f"{scheme_hint}|{q}"
        now = time.time()

        cached = self._cache.get(cache_key)
        if cached and (now - cached[0] < self.ttl_seconds):
            return cached[1][:max_items]

        scheme_key = self._infer_scheme_key(q, scheme_hint)
        urls = list(self.scheme_sources.get(scheme_key, []))
        if not urls:
            urls = self.scheme_sources["generic"]

        snippets: List[str] = []

        # 1) Use DuckDuckGo search to discover fresh pages quickly.
        for hit in self._duckduckgo_snippets(query=q, scheme_key=scheme_key, max_items=max_items):
            snippets.append(hit)
            if len(snippets) >= max_items:
                break

        # 2) Fallback to direct official pages if search returned little.
        for url in urls:
            if len(snippets) >= max_items:
                break
            text = self._fetch_page_snippet(url=url, query=q)
            if text:
                snippets.append(text)

        # RSS enrichment only if we still have little signal.
        if len(snippets) < 2:
            for rss_url in self.rss_sources:
                rss_text = self._fetch_rss_snippet(rss_url, q)
                if rss_text:
                    snippets.append(rss_text)
                if len(snippets) >= max_items:
                    break

        self._cache[cache_key] = (now, snippets)
        return snippets[:max_items]

    def _is_allowed_url(self, url: str) -> bool:
        try:
            host = (urlparse(url).hostname or "").lower()
            if not host:
                return False
            return any(host == d or host.endswith(f".{d}") for d in self.allowed_domains)
        except Exception:
            return False

    def _duckduckgo_snippets(self, query: str, scheme_key: str, max_items: int) -> List[str]:
        try:
            from duckduckgo_search import DDGS  # type: ignore
        except Exception:
            return []

        domain_hints = {
            "pm_awas_urban": "site:pmaymis.gov.in OR site:pmayg.nic.in",
            "pm_kisan": "site:pmkisan.gov.in OR site:pfms.nic.in",
            "e_shram": "site:eshram.gov.in",
            "ayushman": "site:pmjay.gov.in",
            "ration": "site:nfsa.gov.in",
            "generic": "site:india.gov.in OR site:myscheme.gov.in",
        }
        scoped_query = f"{query} {domain_hints.get(scheme_key, domain_hints['generic'])}".strip()

        out: List[str] = []
        try:
            with DDGS() as ddgs:
                results = ddgs.text(scoped_query, max_results=max(6, max_items * 2))
                for row in results:
                    url = (row.get("href") or "").strip()
                    title = (row.get("title") or "Official update").strip()
                    body = re.sub(r"\s+", " ", (row.get("body") or "")).strip()
                    if not url or not self._is_allowed_url(url):
                        continue
                    snippet = body[:220] + ("..." if len(body) > 220 else "")
                    out.append(f"Live search: {title}. {snippet} Source: {url}")
                    if len(out) >= max_items:
                        break
        except Exception:
            return []

        return out

    def _infer_scheme_key(self, q: str, scheme_hint: str) -> str:
        sh = (scheme_hint or "").lower()
        if sh in self.scheme_sources:
            return sh
        if any(k in q for k in ["pm awas", "pmay", "awas yojana"]):
            return "pm_awas_urban"
        if any(k in q for k in ["pm-kisan", "pm kisan", "pmkisan"]):
            return "pm_kisan"
        if any(k in q for k in ["e-shram", "eshram", "shram"]):
            return "e_shram"
        if any(k in q for k in ["ayushman", "pmjay"]):
            return "ayushman"
        if any(k in q for k in ["ration", "nfsa", "food security"]):
            return "ration"
        return "generic"

    def _fetch_page_snippet(self, url: str, query: str) -> Optional[str]:
        try:
            resp = requests.get(url, headers=self._headers, timeout=self.timeout)
            if resp.status_code != 200 or not resp.text:
                return None

            soup = BeautifulSoup(resp.text, "html.parser")
            title = (soup.title.string or "").strip() if soup.title else ""

            # Gather candidate text blocks from common informative elements.
            candidates: List[str] = []
            for tag in soup.select("meta[name='description']"):
                desc = (tag.get("content") or "").strip()
                if desc:
                    candidates.append(desc)

            for node in soup.select("h1, h2, h3, p, li"):
                t = re.sub(r"\s+", " ", node.get_text(" ", strip=True)).strip()
                if len(t) >= 40:
                    candidates.append(t)
                if len(candidates) >= 120:
                    break

            if not candidates and title:
                return f"Live source: {title} ({url})"

            # Prefer lines that share tokens with query.
            tokens = [t for t in re.findall(r"[a-zA-Z0-9-]+", query) if len(t) > 3]
            scored: List[Tuple[int, str]] = []
            for c in candidates:
                low = c.lower()
                score = sum(1 for tok in tokens if tok in low)
                if score > 0:
                    scored.append((score, c))

            if scored:
                scored.sort(key=lambda x: x[0], reverse=True)
                best = scored[0][1]
            else:
                best = candidates[0]

            best = best[:300].rstrip()
            if len(best) == 300 and not best.endswith("..."):
                best += "..."
            source_head = title or "Official update"
            return f"Live update from {source_head}: {best} Source: {url}"
        except Exception:
            return None

    def _fetch_rss_snippet(self, rss_url: str, query: str) -> Optional[str]:
        try:
            resp = requests.get(rss_url, headers=self._headers, timeout=self.timeout)
            if resp.status_code != 200 or not resp.text:
                return None
            soup = BeautifulSoup(resp.text, "xml")
            items = soup.find_all("item")[:20]
            if not items:
                return None

            q_tokens = [t for t in re.findall(r"[a-zA-Z0-9-]+", query.lower()) if len(t) > 3]
            for it in items:
                title = (it.title.get_text(strip=True) if it.title else "").strip()
                desc = (it.description.get_text(" ", strip=True) if it.description else "").strip()
                link = (it.link.get_text(strip=True) if it.link else rss_url).strip()
                text = f"{title} {desc}".lower()
                if not q_tokens or any(t in text for t in q_tokens):
                    return f"Live RSS update: {title}. {desc[:220]} Source: {link}"
            return None
        except Exception:
            return None
