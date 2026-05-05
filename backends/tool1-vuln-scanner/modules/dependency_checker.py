#!/usr/bin/env python3
"""
Dependency Checker Module
Checks for outdated and vulnerable dependencies
"""

import json
import re
from pathlib import Path
from typing import List, Dict
import subprocess

class DependencyChecker:
    def __init__(self):
        """Initialize dependency checker"""
        self.package_managers = {
            'package.json': self._check_npm,
            'requirements.txt': self._check_pip,
            'Gemfile': self._check_ruby,
            'go.mod': self._check_go,
            'pom.xml': self._check_maven,
            'composer.json': self._check_composer
        }
    
    def scan_directory(self, directory: Path) -> List[Dict]:
        """Scan directory for dependency files"""
        findings = []
        
        for file_name, checker_func in self.package_managers.items():
            file_path = directory / file_name
            if file_path.exists():
                file_findings = checker_func(file_path)
                findings.extend(file_findings)
        
        return findings
    
    def _check_npm(self, file_path: Path) -> List[Dict]:
        """Check npm dependencies in package.json"""
        findings = []
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            dependencies = {}
            dependencies.update(data.get('dependencies', {}))
            dependencies.update(data.get('devDependencies', {}))
            
            for package, version in dependencies.items():
                # Remove version prefixes
                clean_version = version.lstrip('^~>=<')
                
                # Check if version looks outdated (simple heuristic)
                if self._is_potentially_outdated(clean_version):
                    findings.append({
                        'type': 'Outdated Dependency',
                        'severity': 'HIGH',
                        'file': str(file_path),
                        'package': package,
                        'version': version,
                        'cwe': 'CWE-1104',
                        'description': f'{package} version {version} may be outdated'
                    })
        
        except Exception as e:
            pass
        
        return findings
    
    def _check_pip(self, file_path: Path) -> List[Dict]:
        """Check Python dependencies in requirements.txt"""
        findings = []
        
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Parse package==version or package>=version
                match = re.match(r'([a-zA-Z0-9_-]+)\s*([=<>!]+)\s*([0-9.]+)', line)
                if match:
                    package, operator, version = match.groups()
                    
                    if self._is_potentially_outdated(version):
                        findings.append({
                            'type': 'Outdated Dependency',
                            'severity': 'HIGH',
                            'file': str(file_path),
                            'package': package,
                            'version': version,
                            'cwe': 'CWE-1104',
                            'description': f'{package} version {version} may be outdated'
                        })
        
        except Exception as e:
            pass
        
        return findings
    
    def _check_ruby(self, file_path: Path) -> List[Dict]:
        """Check Ruby dependencies in Gemfile"""
        findings = []
        # Placeholder for Ruby gem checking
        return findings
    
    def _check_go(self, file_path: Path) -> List[Dict]:
        """Check Go dependencies in go.mod"""
        findings = []
        # Placeholder for Go module checking
        return findings
    
    def _check_maven(self, file_path: Path) -> List[Dict]:
        """Check Maven dependencies in pom.xml"""
        findings = []
        # Placeholder for Maven checking
        return findings
    
    def _check_composer(self, file_path: Path) -> List[Dict]:
        """Check PHP dependencies in composer.json"""
        findings = []
        # Placeholder for Composer checking
        return findings
    
    def _is_potentially_outdated(self, version: str) -> bool:
        """Simple heuristic to check if version might be outdated"""
        try:
            # Parse major.minor.patch
            parts = version.split('.')
            if len(parts) >= 2:
                major = int(parts[0])
                minor = int(parts[1]) if len(parts) > 1 else 0
                
                # Flag very old major versions
                if major < 2:
                    return True
                
                # Flag if major version is old (< 10) and minor is 0
                if major < 10 and minor == 0:
                    return True
        
        except:
            pass
        
        return False
    
    def check_with_safety(self, directory: Path) -> List[Dict]:
        """Use Safety CLI to check Python dependencies for known vulnerabilities"""
        findings = []
        requirements_file = directory / 'requirements.txt'
        
        if not requirements_file.exists():
            return findings
        
        try:
            # Run safety check
            result = subprocess.run(
                ['safety', 'check', '--file', str(requirements_file), '--json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout:
                vulnerabilities = json.loads(result.stdout)
                
                for vuln in vulnerabilities:
                    findings.append({
                        'type': 'Vulnerable Dependency',
                        'severity': 'CRITICAL',
                        'file': str(requirements_file),
                        'package': vuln.get('package', 'Unknown'),
                        'version': vuln.get('installed_version', 'Unknown'),
                        'vulnerability': vuln.get('vulnerability', 'Unknown CVE'),
                        'cwe': 'CWE-1035',
                        'description': vuln.get('advisory', 'Known security vulnerability')
                    })
        
        except Exception as e:
            pass  # Safety not installed or failed
        
        return findings

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else '.'
    checker = DependencyChecker()
    findings = checker.scan_directory(Path(target))
    print(f"\n📦 Found {len(findings)} dependency issues")
    for finding in findings[:5]:
        print(f"  - {finding['package']} {finding['version']}")
