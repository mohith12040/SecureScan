import os
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas renderer to display dynamic 'Page X of Y' footers
    and standard cybersecurity headers.
    """
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # Suppress headers and footers on the cover page (Page 1)
        if self._pageNumber > 1:
            # Header
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(HexColor("#0f172a")) # Dark slate
            self.drawString(54, 750, "SECURESCAN: AI-DRIVEN VULNERABILITY AUDIT")
            
            self.setFont("Helvetica", 8)
            self.setFillColor(HexColor("#64748b")) # Muted grey
            ist_now = datetime.utcnow() + timedelta(hours=5, minutes=30)
            self.drawRightString(letter[0] - 54, 750, ist_now.strftime("%Y-%m-%d %H:%M IST"))
            
            # Header divider line
            self.setStrokeColor(HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 742, letter[0] - 54, 742)
            
            # Footer
            self.line(54, 50, letter[0] - 54, 50)
            self.drawString(54, 38, "CONFIDENTIAL - INTERNAL USE ONLY")
            
            page_str = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(letter[0] - 54, 38, page_str)
            
        self.restoreState()


class PDFReportGenerator:
    def __init__(self, filename, scan_record, open_ports, risk_analysis):
        self.filename = filename
        self.scan = scan_record
        self.ports = open_ports
        self.risk = risk_analysis
        
        # Design system palette
        self.c_primary = HexColor("#0f172a")     # Deep Slate
        self.c_secondary = HexColor("#00f0ff")   # Cyber Cyan
        self.c_bg_dark = HexColor("#1e293b")     # Slate Dark
        self.c_text = HexColor("#334155")        # Charcoal
        
        # Severity colors
        self.severity_colors = {
            'Low': HexColor("#10b981"),       # Emerald
            'Medium': HexColor("#f59e0b"),    # Amber
            'High': HexColor("#f97316"),      # Orange
            'Critical': HexColor("#ef4444")    # Red
        }

    def generate(self):
        # Create PDF document
        doc = SimpleDocTemplate(
            self.filename,
            pagesize=letter,
            rightMargin=54,
            leftMargin=54,
            topMargin=54,
            bottomMargin=54
        )
        
        styles = getSampleStyleSheet()
        
        # Custom Typography
        style_title = ParagraphStyle(
            'CoverTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=32,
            leading=38,
            textColor=self.c_primary,
            spaceAfter=15
        )
        
        style_subtitle = ParagraphStyle(
            'CoverSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=14,
            leading=18,
            textColor=HexColor("#64748b"),
            spaceAfter=30
        )
        
        style_h1 = ParagraphStyle(
            'Heading1_Custom',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=22,
            textColor=self.c_primary,
            spaceBefore=15,
            spaceAfter=10,
            keepWithNext=True
        )
        
        style_body = ParagraphStyle(
            'Body_Custom',
            parent=styles['BodyText'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=self.c_text,
            spaceAfter=8
        )
        
        style_bold = ParagraphStyle(
            'Body_Bold',
            parent=style_body,
            fontName='Helvetica-Bold'
        )

        story = []

        # ----------------------------------------------------
        # COVER PAGE
        # ----------------------------------------------------
        story.append(Spacer(1, 40))
        
        # Cyber-security top badge
        badge_style = ParagraphStyle(
            'Badge',
            fontName='Helvetica-Bold',
            fontSize=9,
            textColor=colors.white,
            backColor=self.c_primary,
            borderPadding=6,
            spaceAfter=25
        )
        story.append(Paragraph("AI-DRIVEN SECURITY INTEGRITY PLATFORM", badge_style))
        story.append(Spacer(1, 10))
        
        # Title
        story.append(Paragraph("SecureScan Audit Report", style_title))
        story.append(Paragraph("Automated Vulnerability Scan, AI Severity Classification & Remediation Guidance", style_subtitle))
        story.append(Spacer(1, 20))
        
        # Cover metadata box
        meta_data = [
            [Paragraph("Target Host:", style_bold), Paragraph(self.scan.target, style_body)],
            [Paragraph("Scan Type:", style_bold), Paragraph(self.scan.scan_type, style_body)],
            [Paragraph("Execution Time:", style_bold), Paragraph((self.scan.created_at + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d %H:%M:%S IST"), style_body)],
            [Paragraph("Open Ports Found:", style_bold), Paragraph(str(self.scan.open_ports_count), style_body)],
            [Paragraph("Calculated Threat Score:", style_bold), Paragraph(f"{self.risk['risk_score']} / 100", style_body)],
            [Paragraph("AI Severity Prediction:", style_bold), Paragraph(f"<font color='{self.severity_colors[self.scan.predicted_severity].hexval()}'><b>{self.scan.predicted_severity}</b></font> ({self.scan.confidence_score:.1%} confidence)", style_body)]
        ]
        
        meta_table = Table(meta_data, colWidths=[150, 350])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), HexColor("#f8fafc")),
            ('PADDING', (0,0), (-1,-1), 12),
            ('BOX', (0,0), (-1,-1), 1, HexColor("#e2e8f0")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LINEBELOW', (0,0), (-1,-2), 0.5, HexColor("#f1f5f9")),
        ]))
        
        story.append(meta_table)
        story.append(Spacer(1, 80))
        
        # Confidentiality Warning
        story.append(Paragraph(
            "<b>WARNING:</b> This document contains classified security scanning results regarding the analyzed network endpoint target. "
            "Leakage of this data can present severe exposure of network vulnerabilities to malicious actors. Keep encrypted and limit distribution to authorized system administrators only.",
            ParagraphStyle('Warning', parent=style_body, textColor=HexColor("#ef4444"), fontSize=9, leading=12)
        ))
        
        story.append(PageBreak())

        # ----------------------------------------------------
        # PAGE 2: EXECUTIVE SUMMARY & THREAT ANALYSIS
        # ----------------------------------------------------
        story.append(Spacer(1, 15)) # Spacer under header line
        story.append(Paragraph("Executive Security Summary", style_h1))
        
        summary_text = (
            f"An automated cyber security scanning audit was successfully executed against target host <b>{self.scan.target}</b>. "
            f"The assessment scanned ports, services, and exposure architectures. A custom mathematical risk analysis, layered with a "
            f"Supervised Random Forest Classifier Model, was applied to predict the system's absolute vulnerability envelope. "
            f"Our AI Engine classifies this target as having a <b><font color='{self.severity_colors[self.scan.predicted_severity].hexval()}'>{self.scan.predicted_severity.upper()}</font></b> threat severity profile "
            f"with an analytical risk score of <b>{self.risk['risk_score']}/100</b>."
        )
        story.append(Paragraph(summary_text, style_body))
        story.append(Spacer(1, 15))
        
        # Severity callout block
        sev_color = self.severity_colors[self.scan.predicted_severity]
        action_label = {
            'Low': 'INFORMATIONAL',
            'Medium': 'MONITOR & AUDIT',
            'High': 'PATCH URGENTLY',
            'Critical': 'IMMEDIATE ACTION REQUIRED'
        }[self.scan.predicted_severity]
        
        callout_data = [
            [
                Paragraph(f"<font size=14 color='white'><b>VULNERABILITY LEVEL: {self.scan.predicted_severity.upper()}</b></font>", style_bold),
                Paragraph(f"<font size=12 color='white'><b>ACTION: {action_label}</b></font>", style_bold)
            ]
        ]
        callout_table = Table(callout_data, colWidths=[250, 250])
        callout_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), sev_color),
            ('ALIGN', (1,0), (1,0), 'RIGHT'),
            ('PADDING', (0,0), (-1,-1), 15),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ROUNDEDCORNERS', [4, 4, 4, 4])
        ]))
        story.append(callout_table)
        story.append(Spacer(1, 20))
        
        # ----------------------------------------------------
        # PAGE 2: DISCOVERED PORTS & SERVICES
        # ----------------------------------------------------
        story.append(Paragraph("Discovered Open Ports & Service Footprints", style_h1))
        story.append(Paragraph("The following network entry ports were detected in an active open state and exposing transport socket services:", style_body))
        story.append(Spacer(1, 5))
        
        # Ports table
        table_headers = [
            Paragraph("<b>Port</b>", style_bold),
            Paragraph("<b>Protocol</b>", style_bold),
            Paragraph("<b>Service</b>", style_bold),
            Paragraph("<b>Service Version / Banner</b>", style_bold),
            Paragraph("<b>Status</b>", style_bold)
        ]
        
        ports_table_data = [table_headers]
        
        if not self.ports:
            ports_table_data.append([
                Paragraph("None", style_body),
                Paragraph("-", style_body),
                Paragraph("No open ports found", style_body),
                Paragraph("-", style_body),
                Paragraph("Secure", style_body)
            ])
        else:
            for p in self.ports:
                ports_table_data.append([
                    Paragraph(str(p['port']), style_body),
                    Paragraph(p.get('protocol', 'tcp').upper(), style_body),
                    Paragraph(p.get('service', 'unknown'), style_body),
                    Paragraph(p.get('version', 'unknown') or 'unknown', style_body),
                    Paragraph("<font color='#10b981'><b>OPEN</b></font>", style_body)
                ])
                
        ports_table = Table(ports_table_data, colWidths=[60, 60, 90, 230, 60])
        ports_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor("#e2e8f0")),
            ('PADDING', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, HexColor("#cbd5e1")),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, HexColor("#f8fafc")])
        ]))
        
        story.append(ports_table)
        story.append(Spacer(1, 20))
        
        # ----------------------------------------------------
        # PAGE 3: DETAILED ACTIONABLE REMEDIATION GUIDANCE
        # ----------------------------------------------------
        story.append(PageBreak())
        story.append(Spacer(1, 15))
        story.append(Paragraph("Structured Remediation Guidance Plan", style_h1))
        story.append(Paragraph(
            "Below is a prioritized list of mitigation steps generated by our rule engine and security models. "
            "Addressing these items in order of priority will significantly minimize the target's threat envelope.",
            style_body
        ))
        story.append(Spacer(1, 10))
        
        rem_headers = [
            Paragraph("<b>Host Asset</b>", style_bold),
            Paragraph("<b>Priority</b>", style_bold),
            Paragraph("<b>Action Plan / Defensive Strategy</b>", style_bold)
        ]
        rem_table_data = [rem_headers]
        
        priority_colors = {
            'Low': '#10b981',
            'Medium': '#eab308',
            'High': '#f97316',
            'Critical': '#ef4444'
        }
        
        for r in self.risk['remediations']:
            asset = f"Port {r['port']} ({r['service']})" if r['port'] != 'N/A' else 'General Target'
            p_val = r['priority']
            p_color = priority_colors.get(p_val, '#334155')
            
            rem_table_data.append([
                Paragraph(asset, style_bold),
                Paragraph(f"<font color='{p_color}'><b>{p_val.upper()}</b></font>", style_bold),
                Paragraph(r['remediation'], style_body)
            ])
            
        rem_table = Table(rem_table_data, colWidths=[120, 80, 300])
        rem_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor("#e2e8f0")),
            ('PADDING', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 0.5, HexColor("#cbd5e1")),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, HexColor("#f8fafc")])
        ]))
        
        story.append(rem_table)
        
        # Build the PDF
        doc.build(story, canvasmaker=NumberedCanvas)
        print(f"Professional PDF report compiled and written to: {self.filename}")
