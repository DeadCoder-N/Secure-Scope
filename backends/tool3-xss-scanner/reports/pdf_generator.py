#!/usr/bin/env python3
"""
PDF Report Generator for XSS Scanner
FIX: Title is 'XSS Security Report' (was 'SQL Injection Security Report')
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from datetime import datetime
from typing import Dict


class XSSPDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle('T', parent=self.styles['Heading1'], fontSize=20,
            textColor=colors.HexColor('#1a1a1a'), spaceAfter=6, alignment=TA_CENTER, fontName='Helvetica-Bold')
        self.h1_style = ParagraphStyle('H1', parent=self.styles['Heading1'], fontSize=14,
            textColor=colors.HexColor('#d97706'), spaceAfter=8, spaceBefore=10, fontName='Helvetica-Bold')
        self.h2_style = ParagraphStyle('H2', parent=self.styles['Heading2'], fontSize=11,
            textColor=colors.HexColor('#92400e'), spaceAfter=6, spaceBefore=6, fontName='Helvetica-Bold')
        self.body_style = ParagraphStyle('B', parent=self.styles['BodyText'], fontSize=9,
            alignment=TA_JUSTIFY, spaceAfter=4, leading=12)

    def generate(self, report: Dict, output_file: str):
        doc = SimpleDocTemplate(output_file, pagesize=letter,
            rightMargin=0.75*inch, leftMargin=0.75*inch,
            topMargin=0.75*inch, bottomMargin=0.75*inch)
        elements = []

        # Title page — FIX: correct title
        elements.append(Spacer(1, inch))
        elements.append(Paragraph("XSS SECURITY REPORT", self.title_style))
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph("Cross-Site Scripting Assessment — SecureScope", self.styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        for item in [
            f"<b>Target:</b> {report.get('target', 'N/A')}",
            f"<b>Scan Mode:</b> {report.get('scan_mode', 'manual').upper()}",
            f"<b>Scan Date:</b> {datetime.now().strftime('%B %d, %Y at %H:%M')}",
            f"<b>Total Vulnerabilities:</b> {report.get('total_vulnerabilities', 0)}",
            f"<b>Parameters Tested:</b> {report.get('params_tested', 'N/A')}",
        ]:
            elements.append(Paragraph(item, self.body_style))
        elements.append(PageBreak())

        # Summary
        elements.append(Paragraph("EXECUTIVE SUMMARY", self.h1_style))
        sev = report.get('severity_breakdown', {})
        table_data = [
            ['Severity', 'Count', 'OWASP', 'Remediation'],
            ['HIGH',   str(sev.get('HIGH', 0)),   'A03:2021', 'Urgent (1 week)'],
            ['MEDIUM', str(sev.get('MEDIUM', 0)), 'A03:2021', 'Important (2 weeks)'],
            ['LOW',    str(sev.get('LOW', 0)),     'A03:2021', 'Normal (1 month)'],
        ]
        t = Table(table_data, colWidths=[1.5*inch, 1*inch, 1.5*inch, 2.5*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#d97706')),
            ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
            ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',   (0,0), (-1,-1), 9),
            ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
            ('GRID',       (0,0), (-1,-1), 1, colors.black),
        ]))
        elements.append(t)
        elements.append(PageBreak())

        # Findings
        vulns = report.get('vulnerabilities', [])
        if vulns:
            elements.append(Paragraph("DETAILED FINDINGS", self.h1_style))
            for i, v in enumerate(vulns, 1):
                sev_val = v.get('severity', 'HIGH')
                color_map = {'CRITICAL': '#cc0000', 'HIGH': '#ff6600', 'MEDIUM': '#ffcc00', 'LOW': '#00cc00'}
                c = color_map.get(sev_val, '#666666')
                elements.append(Paragraph(
                    f"<b>#{i} — {v.get('type', 'XSS')}</b> &nbsp; <font color='{c}'>[{sev_val}]</font>",
                    self.h2_style))
                for label, key in [('URL', 'url'), ('Parameter', 'parameter'), ('Payload', 'payload'),
                                    ('Evidence', 'evidence'), ('CWE', 'cwe'), ('OWASP', 'owasp')]:
                    if v.get(key):
                        elements.append(Paragraph(f"<b>{label}:</b> {v[key]}", self.body_style))
                if v.get('fix_prompt'):
                    elements.append(Paragraph(f"<b>💡 Fix:</b> {v['fix_prompt']}", self.body_style))
                elements.append(Spacer(1, 0.15*inch))

        doc.build(elements)
        return output_file
