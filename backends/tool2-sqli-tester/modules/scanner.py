#!/usr/bin/env python3
"""
SQL Injection Scanner — SecureScope Tool 2
Loads payloads from .txt files (75 total)
Detects: Error-based, Union-based, Boolean-blind, Time-based
"""

import requests
import time
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from typing import List, Dict, Optional
from modules.crawler import Crawler

PAYLOADS_DIR = Path(__file__).parent.parent / 'payloads'

ERROR_SIGNATURES = [
    'SQL syntax', 'mysql_fetch', 'mysql_num_rows', 'mysqli',
    'PostgreSQL', 'pg_query', 'ODBC', 'Microsoft SQL', 'ORA-',
    'Oracle error', 'SQLite', 'sqlite3', 'Unclosed quotation',
    'quoted string', 'syntax error', 'unterminated string',
    'Warning: mysql', 'valid MySQL result', 'MySqlClient',
    'You have an error in your SQL syntax', 'Division by zero',
    'Invalid column name', "Column count doesn't match",
    'supplied argument is not a valid MySQL',
]


def load_payloads(filename: str) -> List[str]:
    f = PAYLOADS_DIR / filename
    if not f.exists():
        return []
    return [line.strip() for line in f.read_text().splitlines() if line.strip() and not line.startswith('#')]


class SQLiScanner:
    def __init__(self):
        self.error_payloads   = load_payloads('error_based.txt')
        self.union_payloads   = load_payloads('union_based.txt')
        self.boolean_payloads = load_payloads('boolean_blind.txt')
        self.time_payloads    = load_payloads('time_based.txt')
        self.session = requests.Session()
        self.session.headers['User-Agent'] = 'SecureScope-SQLi/1.0'

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
        # Get baseline
        try:
            baseline_resp = self.session.get(url, timeout=8)
            baseline_len  = len(baseline_resp.text)
            baseline_time = 0.5
        except Exception:
            baseline_len  = 0
            baseline_time = 0.5

        # 1. Error-based
        for payload in self.error_payloads:
            test_url = Crawler.build_test_url(url, param, payload)
            try:
                resp = self.session.get(test_url, timeout=8)
                error = self._detect_sql_error(resp.text)
                if error:
                    # Verify: control must NOT have error
                    ctrl_url  = Crawler.build_test_url(url, param, 'safe_ctrl_123')
                    ctrl_resp = self.session.get(ctrl_url, timeout=8)
                    if not self._detect_sql_error(ctrl_resp.text):
                        return self._finding('Error-Based SQLi', 'CRITICAL', url, param, payload,
                                             f'SQL error: {error}')
            except Exception:
                continue

        # 2. Union-based
        for payload in self.union_payloads:
            test_url = Crawler.build_test_url(url, param, payload)
            try:
                resp = self.session.get(test_url, timeout=8)
                if self._detect_sql_error(resp.text):
                    return self._finding('Union-Based SQLi', 'CRITICAL', url, param, payload,
                                         'UNION query triggered SQL error')
                if abs(len(resp.text) - baseline_len) > 200:
                    return self._finding('Union-Based SQLi', 'HIGH', url, param, payload,
                                         f'Response length changed significantly ({len(resp.text)} vs {baseline_len})')
            except Exception:
                continue

        # 3. Boolean-blind
        blind = self._test_boolean(url, param, baseline_len)
        if blind:
            return blind

        # 4. Time-based
        time_result = self._test_time_based(url, param, baseline_time)
        if time_result:
            return time_result

        return None

    def _test_boolean(self, url: str, param: str, baseline_len: int) -> Optional[Dict]:
        try:
            true_url  = Crawler.build_test_url(url, param, "' AND '1'='1")
            false_url = Crawler.build_test_url(url, param, "' AND '1'='2")
            true_resp  = self.session.get(true_url,  timeout=8)
            false_resp = self.session.get(false_url, timeout=8)
            true_len   = len(true_resp.text)
            false_len  = len(false_resp.text)
            diff = abs(true_len - false_len)
            natural_var = abs(true_len - baseline_len)
            if diff > 100 and diff > natural_var:
                return self._finding('Boolean-Blind SQLi', 'HIGH', url, param,
                                     "' AND '1'='1 vs ' AND '1'='2",
                                     f'TRUE={true_len}B FALSE={false_len}B diff={diff}B')
        except Exception:
            pass
        return None

    def _test_time_based(self, url: str, param: str, baseline_time: float) -> Optional[Dict]:
        sleep_sec = 5
        threshold = baseline_time + sleep_sec - 1
        for payload in self.time_payloads[:6]:
            test_url = Crawler.build_test_url(url, param, payload)
            try:
                start   = time.time()
                self.session.get(test_url, timeout=12)
                elapsed = time.time() - start
                if elapsed >= threshold:
                    return self._finding('Time-Based SQLi', 'HIGH', url, param, payload,
                                         f'Response delayed {elapsed:.1f}s (baseline {baseline_time:.1f}s)')
            except requests.Timeout:
                return self._finding('Time-Based SQLi', 'HIGH', url, param, payload,
                                     'Request timed out — server likely sleeping')
            except Exception:
                continue
        return None

    # ── Helpers ─────────────────────────────────────────────────

    def _detect_sql_error(self, text: str) -> Optional[str]:
        tl = text.lower()
        for sig in ERROR_SIGNATURES:
            if sig.lower() in tl:
                return sig
        return None

    def _finding(self, vuln_type: str, severity: str, url: str, param: str,
                 payload: str, evidence: str) -> Dict:
        fix_map = {
            'Error-Based SQLi':   'Use parameterized queries / prepared statements. Never concatenate user input into SQL. Disable detailed SQL errors in production.',
            'Union-Based SQLi':   'Use parameterized queries. Disable detailed SQL error messages. Use an ORM.',
            'Boolean-Blind SQLi': 'Use parameterized queries. Implement WAF rules. Validate and whitelist input.',
            'Time-Based SQLi':    'Use parameterized queries. Set query timeouts. Monitor for slow queries.',
        }
        return {
            'type':       vuln_type,
            'severity':   severity,
            'url':        url,
            'parameter':  param,
            'payload':    payload,
            'evidence':   evidence,
            'fix_prompt': fix_map.get(vuln_type, 'Use parameterized queries and input validation.'),
            'owasp':      'A03:2021 – Injection',
            'cwe':        'CWE-89',
        }
