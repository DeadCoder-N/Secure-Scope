#!/usr/bin/env python3
"""
XSS Scanner Backend API — SecureScope Tool 3
Port: 5003
"""

import sys
import json
import uuid
import tempfile
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.scanner import XSSScanner
from reports.pdf_generator import XSSPDFGenerator

app = Flask(__name__)
CORS(app, expose_headers=['Content-Disposition'])

scan_results = {}


def build_report(findings, target, scan_mode, params_tested=None):
    sev = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
    for f in findings:
        key = f.get('severity', 'HIGH')
        sev[key] = sev.get(key, 0) + 1
    return {
        'target': target,
        'scan_mode': scan_mode,
        'scan_date': datetime.now().isoformat(),
        'total_vulnerabilities': len(findings),
        'params_tested': params_tested,
        'severity_breakdown': sev,
        'vulnerabilities': findings,
    }


@app.route('/api/scan', methods=['POST'])
def scan():
    try:
        data = request.json
        target = data.get('target', '').strip()
        scan_mode = data.get('scan_mode', 'manual')

        if not target:
            return jsonify({'error': 'Target URL is required'}), 400

        scanner = XSSScanner()

        if scan_mode == 'smart':
            result = scanner.scan_smart(target)
            findings = result['findings']
            params_tested = result['params_tested']
        else:
            findings = scanner.scan_manual(target)
            params_tested = None

        report = build_report(findings, target, scan_mode, params_tested)

        scan_id = str(uuid.uuid4())[:8]
        date_str = datetime.now().strftime('%d_%b_%Y')
        temp_dir = Path(tempfile.gettempdir())
        json_file = temp_dir / f"xss_{date_str}_{scan_id}.json"
        pdf_file  = temp_dir / f"xss_{date_str}_{scan_id}.pdf"

        with open(json_file, 'w') as f:
            json.dump(report, f, indent=2)

        try:
            XSSPDFGenerator().generate(report, str(pdf_file))
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
            return jsonify({'error': 'No scan results'}), 404
        scan_id = list(scan_results.keys())[-1]

    slot = scan_results.get(scan_id)
    if not slot:
        return jsonify({'error': 'Scan ID not found'}), 404

    file_path = slot.get('pdf') if fmt == 'pdf' else slot.get('json')
    mimetype  = 'application/pdf' if fmt == 'pdf' else 'application/json'

    if not file_path or not Path(file_path).exists():
        return jsonify({'error': f'{fmt.upper()} not found'}), 404

    with open(file_path, 'rb') as f:
        data = f.read()

    response = Response(data, mimetype=mimetype)
    response.headers['Content-Disposition'] = f'attachment; filename="{Path(file_path).name}"'
    response.headers['Cache-Control'] = 'no-cache'
    return response


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'XSS Scanner', 'port': 5003})


if __name__ == '__main__':
    print("\n" + "="*50)
    print("⚡ XSS SCANNER — SecureScope Tool 3")
    print("="*50)
    print("📍 http://localhost:5003")
    print("="*50 + "\n")
    app.run(host='0.0.0.0', port=5003, debug=False, threaded=True, use_reloader=False)
