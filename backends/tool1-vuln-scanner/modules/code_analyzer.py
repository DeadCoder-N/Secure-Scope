#!/usr/bin/env python3
"""
Code Analyzer Module
FIX: scan_directory now calls _analyze_python/_analyze_javascript per file.
Previously only _run_bandit() was called — if bandit not installed, zero results.
"""

import subprocess
import json
from pathlib import Path
from typing import List, Dict


class CodeAnalyzer:
    def __init__(self):
        self.analyzers = {
            '.py':  self._analyze_python,
            '.js':  self._analyze_javascript,
            '.ts':  self._analyze_typescript,
            '.jsx': self._analyze_javascript,
            '.tsx': self._analyze_typescript,
        }

    def scan_directory(self, directory: Path) -> List[Dict]:
        findings = []

        # Run Bandit for Python (if installed)
        findings.extend(self._run_bandit(directory))

        # FIX: also run per-file analysis for all supported extensions
        exclude_dirs = {'node_modules', '.git', 'dist', 'build', '__pycache__', 'venv', 'env'}
        for file_path in directory.rglob('*'):
            if file_path.is_dir():
                continue
            if any(ex in file_path.parts for ex in exclude_dirs):
                continue
            analyzer = self.analyzers.get(file_path.suffix.lower())
            if analyzer:
                findings.extend(analyzer(file_path))

        return findings

    def _run_bandit(self, directory: Path) -> List[Dict]:
        findings = []
        try:
            result = subprocess.run(
                ['bandit', '-r', str(directory), '-f', 'json', '-ll'],
                capture_output=True, text=True, timeout=60
            )
            if result.stdout:
                data = json.loads(result.stdout)
                for issue in data.get('results', []):
                    findings.append({
                        'type': 'Code Vulnerability',
                        'severity': self._map_severity(issue.get('issue_severity', 'LOW')),
                        'file': issue.get('filename', 'Unknown'),
                        'line': issue.get('line_number', 0),
                        'description': issue.get('issue_text', 'Security issue detected'),
                        'cwe': str(issue.get('issue_cwe', {}).get('id', 'CWE-Unknown')),
                    })
        except (FileNotFoundError, Exception):
            pass  # bandit not installed — fall through to per-file analysis
        return findings

    def _map_severity(self, severity: str) -> str:
        return {'HIGH': 'HIGH', 'MEDIUM': 'MEDIUM', 'LOW': 'LOW'}.get(severity.upper(), 'MEDIUM')

    def _analyze_python(self, file_path: Path) -> List[Dict]:
        findings = []
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            checks = [
                ('eval(',        'Dangerous Function',       'HIGH',   'CWE-95',  'eval() can lead to code injection'),
                ('exec(',        'Dangerous Function',       'HIGH',   'CWE-95',  'exec() can lead to code injection'),
                ('pickle.loads(','Insecure Deserialization', 'HIGH',   'CWE-502', 'pickle.loads() can execute arbitrary code'),
                ('os.system(',   'Dangerous Function',       'HIGH',   'CWE-78',  'os.system() can lead to command injection'),
                ('subprocess.call(', 'Dangerous Function',  'MEDIUM', 'CWE-78',  'subprocess.call() with shell=True is dangerous'),
            ]
            for pattern, vuln_type, severity, cwe, desc in checks:
                if pattern in content:
                    findings.append({
                        'type': vuln_type,
                        'severity': severity,
                        'file': str(file_path),
                        'description': desc,
                        'cwe': cwe,
                    })
        except Exception:
            pass
        return findings

    def _analyze_javascript(self, file_path: Path) -> List[Dict]:
        findings = []
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            checks = [
                ('eval(',                  'Dangerous Function', 'HIGH',   'CWE-95', 'eval() can lead to code injection'),
                ('.innerHTML',             'Potential XSS',      'MEDIUM', 'CWE-79', 'innerHTML usage can lead to XSS if not sanitized'),
                ('dangerouslySetInnerHTML','Potential XSS',      'MEDIUM', 'CWE-79', 'dangerouslySetInnerHTML can lead to XSS'),
                ('document.write(',        'Potential XSS',      'MEDIUM', 'CWE-79', 'document.write() can lead to XSS'),
            ]
            for pattern, vuln_type, severity, cwe, desc in checks:
                if pattern in content:
                    findings.append({
                        'type': vuln_type,
                        'severity': severity,
                        'file': str(file_path),
                        'description': desc,
                        'cwe': cwe,
                    })
        except Exception:
            pass
        return findings

    def _analyze_typescript(self, file_path: Path) -> List[Dict]:
        return self._analyze_javascript(file_path)
