#!/usr/bin/env python3
"""
Crawler Module — discovers URLs with parameters from a base URL
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse
from typing import List, Dict, Set


class Crawler:
    def __init__(self, base_url: str, max_pages: int = 30):
        self.base_url = base_url
        self.base_domain = urlparse(base_url).netloc
        self.max_pages = max_pages
        self.visited: Set[str] = set()
        self.session = requests.Session()
        self.session.headers['User-Agent'] = 'SecureScope-Crawler/1.0'

    def crawl(self) -> List[Dict]:
        """Returns list of {url, params} dicts where params is a list of param names."""
        targets = []
        queue = [self.base_url]

        while queue and len(self.visited) < self.max_pages:
            url = queue.pop(0)
            normalized = url.split('?')[0]
            if normalized in self.visited:
                continue
            self.visited.add(normalized)

            try:
                resp = self.session.get(url, timeout=8, allow_redirects=True)
                if 'text/html' not in resp.headers.get('Content-Type', ''):
                    continue

                # Check if current URL has params
                parsed = urlparse(url)
                params = list(parse_qs(parsed.query).keys())
                if params:
                    targets.append({'url': url, 'params': params})

                # Parse links
                soup = BeautifulSoup(resp.text, 'html.parser')
                for tag in soup.find_all(['a', 'form']):
                    href = tag.get('href') or tag.get('action', '')
                    if not href:
                        continue
                    full = urljoin(url, href)
                    if urlparse(full).netloc != self.base_domain:
                        continue
                    # Add links with params as targets
                    p = urlparse(full)
                    link_params = list(parse_qs(p.query).keys())
                    if link_params and full not in [t['url'] for t in targets]:
                        targets.append({'url': full, 'params': link_params})
                    if p.path not in self.visited:
                        queue.append(full)

            except Exception:
                continue

        return targets

    @staticmethod
    def build_test_url(url: str, param: str, payload: str) -> str:
        """Replace a single param value with payload, keep others."""
        parsed = urlparse(url)
        qs = parse_qs(parsed.query, keep_blank_values=True)
        qs[param] = [payload]
        new_query = urlencode({k: v[0] for k, v in qs.items()})
        return urlunparse(parsed._replace(query=new_query))
