#!/usr/bin/env python3
"""
Configuration Checker Module
FIX: .env detection now skips .env.example and checks if .env is gitignored.
Previously flagged every .env as CRITICAL even on local scans.
"""

import requests
from pathlib import Path
from typing import List, Dict
from bs4 import BeautifulSoup


class ConfigChecker:
    def __init__(self):
        self.required_headers = {
            'Content-Security-Policy':   'CRITICAL',
            'X-Frame-Options':           'HIGH',
            'X-Content-Type-Options':    'HIGH',
            'Strict-Transport-Security': 'HIGH',
            'X-XSS-Protection':          'MEDIUM',
            'Referrer-Policy':           'MEDIUM',
            'Permissions-Policy':        'LOW',
        }

    def check_website(self, url: str) -> List[Dict]:
        findings = []
        try:
            response = requests.get(url, timeout=10, allow_redirects=True)
            findings.extend(self._check_headers(response.headers, url))
            findings.extend(self._check_html(response.text, url))
        except Exception as e:
            findings.append({
                'type': 'Connection Error',
                'severity': 'INFO',
                'description': f'Could not connect to {url}: {str(e)}'
            })
        return findings

    def _check_headers(self, headers: Dict, url: str) -> List[Dict]:
        findings = []
        for header, severity in self.required_headers.items():
            if header not in headers:
                findings.append({
                    'type': 'Missing Security Header',
                    'severity': severity,
                    'file': url,
                    'header': header,
                    'cwe': 'CWE-693',
                    'description': f'{header} header is not set',
                })
        if 'Server' in headers:
            findings.append({
                'type': 'Information Disclosure',
                'severity': 'LOW',
                'file': url,
                'header': 'Server',
                'cwe': 'CWE-200',
                'description': 'Server header exposes server information',
            })
        if 'X-Powered-By' in headers:
            findings.append({
                'type': 'Information Disclosure',
                'severity': 'LOW',
                'file': url,
                'header': 'X-Powered-By',
                'cwe': 'CWE-200',
                'description': 'X-Powered-By header exposes technology stack',
            })
        return findings

    def _check_html(self, html: str, url: str) -> List[Dict]:
        findings = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            for script in soup.find_all('script', src=True):
                src = script.get('src', '')
                if any(cdn in src for cdn in ['cdn.', 'unpkg.', 'jsdelivr.', 'cdnjs.']):
                    if not script.get('integrity'):
                        findings.append({
                            'type': 'Missing SRI',
                            'severity': 'MEDIUM',
                            'file': url,
                            'script': src,
                            'cwe': 'CWE-353',
                            'description': f'CDN script lacks integrity attribute: {src}',
                        })
            for form in soup.find_all('form'):
                if form.get('method', 'get').lower() == 'post':
                    csrf_fields = form.find_all('input', {'name': lambda x: x and 'csrf' in x.lower()})
                    if not csrf_fields:
                        findings.append({
                            'type': 'Missing CSRF Protection',
                            'severity': 'HIGH',
                            'file': url,
                            'form_action': form.get('action', ''),
                            'cwe': 'CWE-352',
                            'description': f'Form lacks CSRF token: {form.get("action", "")}',
                        })
        except Exception:
            pass
        return findings

    def check_local_files(self, directory: Path) -> List[Dict]:
        findings = []

        # Check index.html for SRI / CSRF issues
        index_file = directory / 'index.html'
        if index_file.exists():
            try:
                findings.extend(self._check_html(index_file.read_text(encoding='utf-8'), str(index_file)))
            except Exception:
                pass

        # FIX: only flag .env files that are NOT .env.example AND NOT listed in .gitignore
        gitignore_path = directory / '.gitignore'
        gitignored = set()
        if gitignore_path.exists():
            try:
                for line in gitignore_path.read_text().splitlines():
                    gitignored.add(line.strip().lstrip('/'))
            except Exception:
                pass

        for env_file in directory.rglob('.env*'):
            # Skip example/template files
            if env_file.name in ('.env.example', '.env.local.example', '.env.sample'):
                continue
            # Skip if gitignored
            if env_file.name in gitignored or '.env' in gitignored:
                continue
            findings.append({
                'type': 'Sensitive File Exposed',
                'severity': 'CRITICAL',
                'file': str(env_file),
                'cwe': 'CWE-538',
                'description': f'{env_file.name} may be committed — add to .gitignore',
            })

        return findings
