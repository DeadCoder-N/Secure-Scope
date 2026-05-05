#!/usr/bin/env python3
"""
Secret Detector Module
Scans files for exposed secrets, credentials, and sensitive information
"""

import re
import json
from pathlib import Path
from typing import List, Dict

class SecretDetector:
    def __init__(self, patterns_file: str = None):
        """Initialize with secret patterns"""
        if patterns_file is None:
            patterns_file = Path(__file__).parent.parent / 'payloads' / 'secret_patterns.json'
        
        with open(patterns_file, 'r') as f:
            data = json.load(f)
            self.patterns = data['patterns']
    
    def scan_file(self, file_path: Path) -> List[Dict]:
        """Scan a single file for secrets"""
        findings = []
        
        # Skip binary files and large files
        if file_path.stat().st_size > 10 * 1024 * 1024:  # 10MB limit
            return findings
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                for pattern_info in self.patterns:
                    matches = re.finditer(pattern_info['pattern'], content, re.IGNORECASE)
                    
                    for match in matches:
                        # Get line number
                        line_num = content[:match.start()].count('\n') + 1
                        
                        # Extract matched value
                        value = match.group(0)
                        
                        # Skip false positives
                        if self._is_false_positive(value, pattern_info['name']):
                            continue
                        
                        findings.append({
                            'type': 'Exposed Secret',
                            'severity': pattern_info['severity'],
                            'file': str(file_path),
                            'line': line_num,
                            'secret_type': pattern_info['name'],
                            'value': self._redact_value(value),
                            'cwe': pattern_info['cwe']
                        })
        
        except Exception as e:
            pass  # Skip files that can't be read
        
        return findings
    
    def _is_false_positive(self, value: str, secret_type: str) -> bool:
        """Filter out common false positives"""
        false_positives = [
            'example.com', 'test@test.com', 'user@example.com',
            'password123', 'secret123', 'your_api_key_here',
            'YOUR_SECRET_HERE', 'REPLACE_WITH_YOUR_KEY',
            '123-456-7890', '000-000-0000',
            'localhost', '127.0.0.1'
        ]
        
        value_lower = value.lower()
        for fp in false_positives:
            if fp.lower() in value_lower:
                return True
        
        # Skip placeholder patterns
        if 'xxx' in value_lower or 'yyy' in value_lower:
            return True
        
        # Skip very short secrets (likely false positives)
        if secret_type in ['Generic API Key', 'Generic Secret'] and len(value) < 15:
            return True
        
        return False
    
    def _redact_value(self, value: str) -> str:
        """Redact sensitive parts of the value"""
        if len(value) <= 10:
            return value[:3] + '...'
        else:
            return value[:10] + '...'
    
    def scan_directory(self, directory: Path, exclude_dirs: List[str] = None) -> List[Dict]:
        """Recursively scan directory for secrets"""
        if exclude_dirs is None:
            exclude_dirs = [
                'node_modules', '.git', 'dist', 'build', '__pycache__',
                'venv', 'env', '.venv', 'vendor', 'target'
            ]
        
        findings = []
        
        # File extensions to scan
        scannable_extensions = {
            '.js', '.jsx', '.ts', '.tsx', '.py', '.java', '.go', '.rb',
            '.php', '.cs', '.cpp', '.c', '.h', '.sh', '.bash', '.zsh',
            '.env', '.config', '.conf', '.cfg', '.ini', '.yaml', '.yml',
            '.json', '.xml', '.toml', '.properties', '.txt', '.md'
        }
        
        for file_path in directory.rglob('*'):
            # Skip directories
            if file_path.is_dir():
                continue
            
            # Skip excluded directories
            if any(excluded in file_path.parts for excluded in exclude_dirs):
                continue
            
            # Only scan specific file types
            if file_path.suffix.lower() in scannable_extensions or file_path.name in ['.env', '.env.local']:
                file_findings = self.scan_file(file_path)
                findings.extend(file_findings)
        
        return findings

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else '.'
    detector = SecretDetector()
    findings = detector.scan_directory(Path(target))
    print(f"\n🔍 Found {len(findings)} secrets")
    for finding in findings[:5]:
        print(f"  - {finding['secret_type']} in {finding['file']}")
