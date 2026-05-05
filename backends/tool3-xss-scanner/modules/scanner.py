#!/usr/bin/env python3
"""
XSS Scanner — SecureScope Tool 3
Loads payloads from .txt files (60 total)
Detects: Reflected XSS, Stored XSS patterns
FIX: verify_vulnerability — only True if malicious reflected AND control NOT reflected
"""

import requests
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from typing import List, Dict, Optional
from modules.crawler import Crawler

PAYLOADS_DIR = Path(__file__).parent.parent / 'payloads'
CONTROL_MARKER = 'SECURESCOPE_CTRL_99887'


def load_payloads(filename: str) -> List[str]:
    f = PAYLOADS_DIR / filename
    if not f.exists():
        return []
    return [line.strip() for line in f.read_text().splitlines() if line.strip() and not line.startswith('#')]


class XSSScanner:
    def __init__(self):
        self.reflected_payloads = load_payloads('reflected.txt')
        self.bypass_payloads    = load_payloads('bypass.txt')
        self.stored_patterns    = load_payloads('stored.txt')
        self.dom_patterns       = load_payloads('dom_based.txt')
        self.all_payloads       = self.reflected_payloads + self.bypass_payloads
        self.session = requests.Session()
        self.session.headers['User-Agent'] = 'SecureScope-XSS/1.0'

    # ── Public API ──────────────────────────────────────────────

    def scan_manual(self, url: str) -> List[Dict]:
        parsed = urlparse(url)
        params = list(parse_qs(parsed.query).keys())
        if not params:
            return []
        findings = []
        for param in params:
            result = self._test_param(url, param)
            if result:
                findings.append(result)
        return findings

    def scan_smart(self, base_url: str) -> Dict:
        crawler = Crawler(base_url)
        targets = crawler.crawl()
        findings = []
        tested = 0
        for target in targets:
            for param in target['params']:
                tested += 1
                result = self._test_param(target['url'], param)
                if result:
                    findings.append(result)
        return {'findings': findings, 'urls_tested': len(targets), 'params_tested': tested}

    # ── Core test logic ─────────────────────────────────────────

    def _test_param(self, url: str, param: str) -> Optional[Dict]:
        # Control check — does this endpoint echo everything?
        try:
            ctrl_url  = Crawler.build_test_url(url, param, CONTROL_MARKER)
            ctrl_resp = self.session.get(ctrl_url, timeout=8)
            control_reflected = CONTROL_MARKER in ctrl_resp.text
        except Exception:
            control_reflected = False

        # Test payloads
        for payload in self.all_payloads:
            test_url = Crawler.build_test_url(url, param, payload)
            try:
                resp = self.session.get(test_url, timeout=8)
                # FIX: only True if payload reflected AND control NOT reflected
                if self._verify(payload, resp.text, control_reflected):
                    severity = self._severity(payload)
                    return self._finding('Reflected XSS', severity, url, param, payload,
                                         self._extract_evidence(payload, resp.text))
            except Exception:
                continue

        # Check stored XSS patterns in base response
        try:
            base_resp = self.session.get(url, timeout=8)
            for pattern in self.stored_patterns + self.dom_patterns:
                if pattern.lower() in base_resp.text.lower():
                    return self._finding('Stored XSS Pattern', 'MEDIUM', url, param,
                                         pattern, f'Dangerous pattern in response: {pattern}')
        except Exception:
            pass

        return None

    def _verify(self, payload: str, response_text: str, control_reflected: bool) -> bool:
        """Only True if payload reflected AND control marker was NOT reflected."""
        payload_reflected = (payload in response_text or
                             payload.lower() in response_text.lower())
        if not payload_reflected:
            return False
        if control_reflected:
            return False
        return True

    def _severity(self, payload: str) -> str:
        pl = payload.lower()
        if '<script>' in pl or 'onerror=' in pl:
            return 'HIGH'
        if 'javascript:' in pl or 'onload=' in pl:
            return 'HIGH'
        return 'MEDIUM'

    def _extract_evidence(self, payload: str, text: str) -> str:
        idx = text.lower().find(payload[:12].lower())
        if idx != -1:
            return text[max(0, idx - 20): idx + len(payload) + 40].strip()
        return 'Payload reflected in response'

    def _finding(self, vuln_type: str, severity: str, url: str, param: str,
                 payload: str, evidence: str) -> Dict:
        fix_map = {
            'Reflected XSS':      'Encode all user input before rendering. Use Content-Security-Policy header. Validate and sanitize input server-side.',
            'Stored XSS Pattern': 'Sanitize stored data before rendering. Use DOMPurify client-side. Implement strict CSP.',
        }
        return {
            'type':       vuln_type,
            'severity':   severity,
            'url':        url,
            'parameter':  param,
            'payload':    payload,
            'evidence':   evidence,
            'fix_prompt': fix_map.get(vuln_type, 'Encode output and validate input.'),
            'owasp':      'A03:2021 – Injection / CWE-79',
            'cwe':        'CWE-79',
        }
