#!/usr/bin/env python3
"""
Vulnerability Scanner Engine
Orchestrates all scanning modules and generates reports
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import subprocess
import tempfile
import shutil

from modules.secret_detector import SecretDetector
from modules.dependency_checker import DependencyChecker
from modules.code_analyzer import CodeAnalyzer
from modules.config_checker import ConfigChecker
from modules.security_headers_analyzer import SecurityHeadersAnalyzer


class VulnerabilityScanner:
    def __init__(self, target: str, scan_type: str = 'auto'):
        self.target = target
        self.scan_type = scan_type
        self.findings = []
        self.scan_date = datetime.now().isoformat()

        self.secret_detector = SecretDetector()
        self.dependency_checker = DependencyChecker()
        self.code_analyzer = CodeAnalyzer()
        self.config_checker = ConfigChecker()
        self.headers_analyzer = SecurityHeadersAnalyzer()

    def scan(self) -> Dict:
        print(f"\n🔍 Starting scan: {self.target}")

        if self.scan_type == 'auto':
            self.scan_type = self._detect_target_type()

        scan_dir, is_temp = self._prepare_scan_directory()

        try:
            print("🔐 Scanning for secrets...")
            secret_findings = self.secret_detector.scan_directory(scan_dir)
            self.findings.extend(secret_findings)
            print(f"   Found {len(secret_findings)} secrets")

            print("📦 Checking dependencies...")
            dep_findings = self.dependency_checker.scan_directory(scan_dir)
            self.findings.extend(dep_findings)
            print(f"   Found {len(dep_findings)} dependency issues")

            # FIX: code_analyzer now actually called per file
            print("🔬 Analyzing code...")
            code_findings = self.code_analyzer.scan_directory(scan_dir)
            self.findings.extend(code_findings)
            print(f"   Found {len(code_findings)} code vulnerabilities")

            print("⚙️  Checking configurations...")
            config_findings = self.config_checker.check_local_files(scan_dir)
            self.findings.extend(config_findings)
            print(f"   Found {len(config_findings)} configuration issues")

            if self.scan_type == 'web':
                print("🌐 Checking live website...")
                web_findings = self.config_checker.check_website(self.target)
                self.findings.extend(web_findings)

                print("🔒 Analyzing security headers...")
                headers_result = self.headers_analyzer.analyze_headers(self.target)
                self.findings.extend(headers_result.get('vulnerabilities', []))

        finally:
            if is_temp and scan_dir.exists():
                shutil.rmtree(scan_dir)

        report = self._generate_report()
        print(f"\n✅ Scan complete! Total: {report['total_vulnerabilities']}")
        return report

    def _detect_target_type(self) -> str:
        if self.target.startswith('http://') or self.target.startswith('https://'):
            return 'github' if 'github.com' in self.target else 'web'
        return 'local'

    def _prepare_scan_directory(self) -> tuple:
        if self.scan_type == 'github':
            temp_dir = Path(tempfile.mkdtemp())
            print(f"📥 Cloning repository...")
            subprocess.run(
                ['git', 'clone', '--depth', '1', self.target, str(temp_dir)],
                check=True, capture_output=True, timeout=60
            )
            return temp_dir, True

        elif self.scan_type == 'local':
            local_path = Path(self.target)
            if not local_path.exists():
                raise FileNotFoundError(f"Directory not found: {self.target}")
            return local_path, False

        elif self.scan_type == 'web':
            temp_dir = Path(tempfile.mkdtemp())
            return temp_dir, True

        raise ValueError(f"Unknown scan type: {self.scan_type}")

    def _generate_report(self) -> Dict:
        severity_breakdown = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0}
        for finding in self.findings:
            severity = finding.get('severity', 'LOW')
            severity_breakdown[severity] = severity_breakdown.get(severity, 0) + 1

        return {
            'scan_date': self.scan_date,
            'target': self.target,
            'scan_type': self.scan_type,
            'total_vulnerabilities': len(self.findings),
            'severity_breakdown': severity_breakdown,
            'vulnerabilities': self.findings
        }
