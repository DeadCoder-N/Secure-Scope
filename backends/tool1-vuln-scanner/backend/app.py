#!/usr/bin/env python3
"""
Vulnerability Scanner Backend API — SecureScope Tool 1
Port: 5001
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import sys
from pathlib import Path
import json
import tempfile
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from scanner import VulnerabilityScanner
from reports.pdf_generator import PDFReportGenerator

app = Flask(__name__)
CORS(app, expose_headers=['Content-Disposition'])

# Per-scan result store (scan_id → files)
scan_results = {}


def add_fix_prompts(vulnerabilities):
    for vuln in vulnerabilities:
        vuln_type = vuln.get('type', '')
        file = vuln.get('file', '')
        fname = Path(file).name if file else 'file'

        if vuln_type == 'Exposed Secret':
            secret_type = vuln.get('secret_type', 'credential')
            vuln['fix_prompt'] = f"Remove {secret_type} from {fname}. Use environment variables (.env) and add to .gitignore. Rotate exposed credentials immediately."
        elif vuln_type == 'Outdated Dependency':
            package = vuln.get('package', 'package')
            vuln['fix_prompt'] = f"Update {package}: npm update {package} or pip install --upgrade {package}. Run security audit after update."
        elif vuln_type == 'Missing Security Header':
            header = vuln.get('header', 'header')
            vuln['fix_prompt'] = f"Add {header} to server config. Test with securityheaders.com"
        elif vuln_type == 'Missing SRI':
            vuln['fix_prompt'] = f"Add integrity hash to CDN script. Generate: curl -s [URL] | openssl dgst -sha384 -binary | openssl base64 -A"
        elif vuln_type == 'Sensitive File Exposed':
            vuln['fix_prompt'] = f"Add {fname} to .gitignore. Run: git rm --cached {fname}. Never commit sensitive files."
        elif vuln_type in ('Code Vulnerability', 'Dangerous Function', 'Potential XSS', 'Insecure Deserialization'):
            line = vuln.get('line', '?')
            vuln['fix_prompt'] = f"Review {fname} line {line}. {vuln.get('description', 'Fix security issue')}. Follow OWASP guidelines."
        else:
            vuln['fix_prompt'] = f"Review and fix {vuln_type} in {fname}. Check OWASP guidelines."
    return vulnerabilities


def calculate_risk_score(vulnerabilities):
    weights = {'CRITICAL': 25, 'HIGH': 15, 'MEDIUM': 8, 'LOW': 3}
    return min(100, sum(weights.get(v.get('severity', 'LOW'), 0) for v in vulnerabilities))


def get_risk_level(score):
    if score >= 75: return 'CRITICAL'
    if score >= 50: return 'HIGH'
    if score >= 25: return 'MEDIUM'
    return 'LOW'


@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        target = data.get('target')
        scan_type = data.get('scan_type', 'auto')

        if not target:
            return jsonify({'error': 'Target URL is required'}), 400

        scanner = VulnerabilityScanner(target=target, scan_type=scan_type)
        report = scanner.scan()

        report['vulnerabilities'] = add_fix_prompts(report['vulnerabilities'])
        report['risk_score'] = calculate_risk_score(report['vulnerabilities'])
        report['risk_level'] = get_risk_level(report['risk_score'])

        # Generate filenames
        import uuid
        scan_id = str(uuid.uuid4())[:8]
        if 'github.com' in target:
            name = target.rstrip('/').split('/')[-1].replace('.git', '')
        else:
            name = 'scan'
        date_str = datetime.now().strftime('%d_%b_%Y')
        temp_dir = Path(tempfile.gettempdir())
        json_file = temp_dir / f"{name}_{date_str}_{scan_id}.json"
        pdf_file  = temp_dir / f"{name}_{date_str}_{scan_id}.pdf"

        with open(json_file, 'w') as f:
            json.dump(report, f, indent=2)

        try:
            PDFReportGenerator().generate(report, str(pdf_file))
        except Exception as e:
            print(f"PDF generation failed: {e}")

        scan_results[scan_id] = {'json': str(json_file), 'pdf': str(pdf_file)}
        report['scan_id'] = scan_id

        return jsonify(report)

    except Exception as e:
        return jsonify({'error': f'Scan failed: {str(e)}'}), 500


@app.route('/api/download', methods=['GET'])
def download():
    scan_id = request.args.get('scan_id')
    fmt = request.args.get('format', 'json')

    if not scan_id:
        if not scan_results:
            return jsonify({'error': 'No scan results available'}), 404
        scan_id = list(scan_results.keys())[-1]

    slot = scan_results.get(scan_id)
    if not slot:
        return jsonify({'error': f'Scan ID not found: {scan_id}'}), 404

    file_path = slot.get('pdf') if fmt == 'pdf' else slot.get('json')
    mimetype  = 'application/pdf' if fmt == 'pdf' else 'application/json'

    if not file_path or not Path(file_path).exists():
        return jsonify({'error': f'{fmt.upper()} report not found'}), 404

    with open(file_path, 'rb') as f:
        data = f.read()

    response = Response(data, mimetype=mimetype)
    response.headers['Content-Disposition'] = f'attachment; filename="{Path(file_path).name}"'
    response.headers['Cache-Control'] = 'no-cache'
    return response


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'Vulnerability Scanner', 'port': 5001})


if __name__ == '__main__':
    print("\n" + "="*50)
    print("🔐 VULNERABILITY SCANNER — SecureScope Tool 1")
    print("="*50)
    print("📍 http://localhost:5001")
    print("="*50 + "\n")
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True, use_reloader=False)
