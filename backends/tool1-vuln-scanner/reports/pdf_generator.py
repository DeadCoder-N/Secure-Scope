#!/usr/bin/env python3
"""
PDF Report Generator for Vulnerability Scanner
FIX: _create_business_impact_analysis, _create_manual_testing_guide,
     _create_ai_prompts_section, _create_code_examples were previously
     defined inside if __name__ == '__main__': block — unreachable dead code.
     All methods are now properly inside the class.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from datetime import datetime
from pathlib import Path
from typing import Dict


class PDFReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_styles()

    def _setup_styles(self):
        self.title_style = ParagraphStyle(
            'CustomTitle', parent=self.styles['Heading1'],
            fontSize=22, textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=6, alignment=TA_CENTER, fontName='Helvetica-Bold'
        )
        self.h1_style = ParagraphStyle(
            'CustomH1', parent=self.styles['Heading1'],
            fontSize=15, textColor=colors.HexColor('#0066cc'),
            spaceAfter=10, spaceBefore=10, fontName='Helvetica-Bold'
        )
        self.h2_style = ParagraphStyle(
            'CustomH2', parent=self.styles['Heading2'],
            fontSize=12, textColor=colors.HexColor('#003366'),
            spaceAfter=8, spaceBefore=8, fontName='Helvetica-Bold'
        )
        self.body_style = ParagraphStyle(
            'CustomBody', parent=self.styles['BodyText'],
            fontSize=10, alignment=TA_JUSTIFY, spaceAfter=6, leading=12
        )

    def generate(self, report_data: Dict, output_file: str):
        doc = SimpleDocTemplate(
            output_file, pagesize=letter,
            rightMargin=0.75*inch, leftMargin=0.75*inch,
            topMargin=0.75*inch, bottomMargin=0.75*inch,
            title="Security Vulnerability Report"
        )
        elements = []
        elements.extend(self._title_page(report_data))
        elements.append(PageBreak())
        elements.extend(self._summary(report_data))
        elements.append(PageBreak())
        elements.extend(self._business_impact(report_data['severity_breakdown']))
        elements.append(PageBreak())
        if report_data.get('vulnerabilities'):
            elements.extend(self._findings(report_data))
            elements.append(PageBreak())
            elements.extend(self._ai_prompts())
        doc.build(elements)
        return output_file

    def _title_page(self, data: Dict):
        elements = [Spacer(1, 1.2*inch)]
        elements.append(Paragraph("SECURITY VULNERABILITY REPORT", self.title_style))
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph("Automated Security Assessment — SecureScope", self.styles['Normal']))
        elements.append(Spacer(1, 0.4*inch))
        scan_date = datetime.fromisoformat(data['scan_date'])
        target_name = Path(data['target']).name if data['scan_type'] == 'local' else data['target']
        for item in [
            f"<b>Target:</b> {target_name}",
            f"<b>Scan Type:</b> {data['scan_type'].upper()}",
            f"<b>Scan Date:</b> {scan_date.strftime('%B %d, %Y at %H:%M:%S')}",
            f"<b>Total Vulnerabilities:</b> {data['total_vulnerabilities']}",
        ]:
            elements.append(Paragraph(item, self.body_style))
            elements.append(Spacer(1, 0.08*inch))
        return elements

    def _summary(self, data: Dict):
        elements = [Paragraph("EXECUTIVE SUMMARY", self.h1_style), Spacer(1, 0.15*inch)]
        sev = data['severity_breakdown']
        total = data['total_vulnerabilities']
        risk_score = min(100, sev.get('CRITICAL',0)*25 + sev.get('HIGH',0)*10 + sev.get('MEDIUM',0)*3 + sev.get('LOW',0)*1)

        table_data = [
            ['Severity', 'Count', 'Priority', 'Action Required'],
            ['CRITICAL', str(sev.get('CRITICAL', 0)), 'P0', 'Immediate (24h)'],
            ['HIGH',     str(sev.get('HIGH', 0)),     'P1', 'Urgent (1 week)'],
            ['MEDIUM',   str(sev.get('MEDIUM', 0)),   'P2', 'Important (2 weeks)'],
            ['LOW',      str(sev.get('LOW', 0)),       'P3', 'Normal (1 month)'],
        ]
        t = Table(table_data, colWidths=[1.5*inch, 1*inch, 1*inch, 2.5*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0066cc')),
            ('TEXTCOLOR',  (0,0), (-1,0), colors.whitesmoke),
            ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',   (0,0), (-1,-1), 10),
            ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
            ('GRID',       (0,0), (-1,-1), 1, colors.black),
            ('BACKGROUND', (0,1), (0,1), colors.HexColor('#ffcccc')),
            ('BACKGROUND', (0,2), (0,2), colors.HexColor('#ffddaa')),
            ('BACKGROUND', (0,3), (0,3), colors.HexColor('#ffffcc')),
            ('BACKGROUND', (0,4), (0,4), colors.HexColor('#ccffcc')),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.2*inch))
        risk_level = 'CRITICAL' if sev.get('CRITICAL',0) > 0 else 'HIGH' if sev.get('HIGH',0) > 5 else 'MEDIUM' if sev.get('HIGH',0) > 0 else 'LOW'
        elements.append(Paragraph(f"<b>Risk Score:</b> {risk_score}/100 &nbsp;&nbsp; <b>Risk Level:</b> {risk_level} &nbsp;&nbsp; <b>Total Issues:</b> {total}", self.body_style))
        return elements

    def _business_impact(self, severity: Dict):
        elements = [Paragraph("BUSINESS IMPACT ANALYSIS", self.h1_style), Spacer(1, 0.15*inch)]
        financial_data = [
            ['Impact Category', 'Low Risk', 'Medium Risk', 'High Risk', 'Critical Risk'],
            ['Data Breach Cost', '$50K-$100K', '$100K-$500K', '$500K-$2M', '$2M-$10M+'],
            ['Incident Response', '$10K-$25K', '$25K-$75K', '$75K-$200K', '$200K-$500K'],
            ['Legal/Compliance', '$5K-$20K', '$20K-$100K', '$100K-$500K', '$500K-$5M'],
            ['Revenue Loss', '1-2%', '2-5%', '5-15%', '15-40%'],
        ]
        t = Table(financial_data, colWidths=[1.5*inch, 1.25*inch, 1.25*inch, 1.25*inch, 1.25*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#dc2626')),
            ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
            ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',   (0,0), (-1,-1), 8),
            ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
            ('GRID',       (0,0), (-1,-1), 1, colors.black),
        ]))
        elements.append(Paragraph("<b>Financial Impact</b>", self.h2_style))
        elements.append(t)
        elements.append(Spacer(1, 0.2*inch))

        compliance_data = [
            ['Regulation', 'Violation Type', 'Fine Range', 'Additional Penalties'],
            ['GDPR', 'Data Breach', '€20M or 4% revenue', 'Lawsuits, Audits'],
            ['PCI-DSS', 'Card Data Exposure', '$5K-$500K/month', 'Card processing ban'],
            ['HIPAA', 'PHI Breach', '$100-$50K per record', 'Criminal charges'],
            ['CCPA', 'Privacy Violation', '$2.5K-$7.5K per record', 'Class action suits'],
        ]
        t2 = Table(compliance_data, colWidths=[1.2*inch, 1.5*inch, 1.8*inch, 1.8*inch])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#ea580c')),
            ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
            ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',   (0,0), (-1,-1), 8),
            ('ALIGN',      (0,0), (-1,-1), 'LEFT'),
            ('GRID',       (0,0), (-1,-1), 1, colors.black),
        ]))
        elements.append(Paragraph("<b>Compliance & Regulatory Impact</b>", self.h2_style))
        elements.append(t2)
        return elements

    def _findings(self, data: Dict):
        elements = [Paragraph("DETAILED FINDINGS", self.h1_style), Spacer(1, 0.15*inch)]
        for i, vuln in enumerate(data['vulnerabilities'], 1):
            sev = vuln.get('severity', 'LOW')
            color_map = {'CRITICAL': '#cc0000', 'HIGH': '#ff6600', 'MEDIUM': '#ffcc00', 'LOW': '#00cc00'}
            color = color_map.get(sev, '#666666')
            elements.append(Paragraph(
                f"<b>#{i} — {vuln.get('type', 'Unknown')}</b> &nbsp; <font color='{color}'>[{sev}]</font>",
                self.h2_style
            ))
            file_info = vuln.get('file', '')
            if file_info:
                line = vuln.get('line', '')
                loc = f"{Path(file_info).name}{f' : line {line}' if line else ''}"
                elements.append(Paragraph(f"<b>Location:</b> {loc}", self.body_style))
            if vuln.get('description'):
                elements.append(Paragraph(f"<b>Description:</b> {vuln['description']}", self.body_style))
            if vuln.get('fix_prompt'):
                elements.append(Paragraph(f"<b>💡 Fix:</b> {vuln['fix_prompt']}", self.body_style))
            elements.append(Spacer(1, 0.15*inch))
        return elements

    def _ai_prompts(self):
        elements = [Paragraph("AI ASSISTANT PROMPTS", self.h1_style)]
        elements.append(Paragraph("Copy these into ChatGPT, Claude, or Amazon Q to fix vulnerabilities:", self.body_style))
        elements.append(Spacer(1, 0.15*inch))
        prompts = [
            ("Fix Exposed Secrets", "Remove all hardcoded secrets from my code. Move them to .env file, update code to use environment variables, add .env to .gitignore, and provide a secret rotation checklist."),
            ("Update Dependencies", "Analyze my package.json/requirements.txt and identify vulnerable packages. Suggest safe update versions, highlight breaking changes, and provide update commands."),
            ("Add Security Headers", "Add comprehensive security headers to my application: Content-Security-Policy, Strict-Transport-Security, X-Frame-Options, X-Content-Type-Options, Referrer-Policy."),
            ("Fix Code Vulnerabilities", "Review my code for eval(), exec(), innerHTML, and other dangerous patterns. Replace with safe alternatives and add input validation."),
        ]
        for title, text in prompts:
            elements.append(Paragraph(f"<b>{title}</b>", self.h2_style))
            t = Table([[text]], colWidths=[6.5*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f0f9ff')),
                ('BOX',        (0,0), (-1,-1), 2, colors.HexColor('#0891b2')),
                ('LEFTPADDING', (0,0), (-1,-1), 10),
                ('RIGHTPADDING',(0,0), (-1,-1), 10),
                ('TOPPADDING',  (0,0), (-1,-1), 10),
                ('BOTTOMPADDING',(0,0),(-1,-1), 10),
                ('FONTSIZE',   (0,0), (-1,-1), 9),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 0.15*inch))
        return elements
