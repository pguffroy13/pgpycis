"""
Report generation for pgpycis (HTML and Text formats)
"""

from datetime import datetime
from typing import Dict, List
import base64
from pathlib import Path


class ReportGenerator:
    """Generate security assessment reports in HTML or text format"""
    
    def __init__(self, format="text", language="en_US"):
        """Initialize report generator"""
        self.format = format
        self.language = language
        self.timestamp = datetime.now()
        self.results = {}
        self.statistics = {}
    
    def add_result(self, check_id, title, status, details="", section=""):
        """Add a check result to the report"""
        if section not in self.results:
            self.results[section] = []
        
        self.results[section].append({
            "id": check_id,
            "title": title,
            "status": status,
            "details": details,
            "section": section,
        })
    
    def calculate_statistics(self):
        """Calculate summary statistics"""
        stats = {
            "SUCCESS": 0,
            "FAILURE": 0,
            "WARNING": 0,
            "ERROR": 0,
            "INFO": 0,
            "MANUAL": 0,
            "TOTAL": 0,
        }
        
        for section_results in self.results.values():
            for result in section_results:
                status = result["status"]
                if status in stats:
                    stats[status] += 1
                stats["TOTAL"] += 1
        
        self.statistics = stats
        return stats
    
    def generate(self, output_file=None):
        """Generate report in specified format"""
        self.calculate_statistics()
        
        if self.format == "html":
            report = self._generate_html()
        elif self.format == "text":
            report = self._generate_text()
        else:
            report = self._generate_text()
        
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report)
        
        return report
    
    def _generate_text(self) -> str:
        """Generate text format report"""
        lines = []
        lines.append("=" * 80)
        lines.append("PGPYCIS - PostgreSQL CIS Compliance Assessment Tool")
        lines.append(f"Report generated: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 80)
        lines.append("")
        
        # Summary
        lines.append("# EXECUTIVE SUMMARY")
        lines.append("")
        lines.append(f"Total Checks: {self.statistics['TOTAL']}")
        lines.append(f"Passed: {self.statistics['SUCCESS']}")
        lines.append(f"Failed: {self.statistics['FAILURE']}")
        lines.append(f"Warnings: {self.statistics['WARNING']}")
        lines.append(f"Manual: {self.statistics['MANUAL']}")
        lines.append("")
        
        # Detailed Assessment
        lines.append("# DETAILED ASSESSMENT")
        lines.append("")
        
        for section, results in sorted(self.results.items()):
            if results:
                lines.append(f"## {section}")
                lines.append("")
                
                for result in results:
                    status_marker = "✓" if result["status"] == "SUCCESS" else "✗"
                    lines.append(
                        f"  {status_marker} [{result['id']}] {result['title']} => {result['status']}"
                    )
                    
                    if result["details"]:
                        for detail_line in result["details"].split("\n"):
                            lines.append(f"      {detail_line}")
                    lines.append("")
        
        lines.append("=" * 80)
        lines.append("END OF REPORT")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def _generate_html(self) -> str:
        """Generate HTML format report"""
        sections = []
        
        for section, results in sorted(self.results.items()):
            if not results:
                continue
            
            section_html = [
                f'<div class="section">',
                f'<h2>{section}</h2>',
                '<div class="checks">',
            ]
            
            for result in results:
                status_class = result["status"].lower()
                section_html.append(
                    f'<div class="check {status_class}">'
                )
                section_html.append(
                    f'<div class="check-header">'
                    f'[{result["id"]}] {result["title"]} - '
                    f'<span class="status">{result["status"]}</span>'
                    f'</div>'
                )
                
                if result["details"]:
                    section_html.append(
                        f'<div class="check-details">{result["details"]}</div>'
                    )
                
                section_html.append('</div>')
            
            section_html.append('</div>')
            section_html.append('</div>')
            
            sections.append("\n".join(section_html))
        
        html_template = f"""<!DOCTYPE html>
<html lang="{self.language[:2]}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PGPYCIS Security Assessment Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            background-color: white;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        
        header {{
            border-bottom: 2px solid #007bff;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        
        h1 {{
            color: #007bff;
            font-size: 28px;
            margin-bottom: 10px;
        }}
        
        .timestamp {{
            color: #666;
            font-size: 14px;
        }}
        
        .summary {{
            background-color: #f9f9f9;
            border-left: 4px solid #007bff;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 4px;
        }}
        
        .summary-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 10px;
        }}
        
        .stat-box {{
            padding: 10px;
            background-color: white;
            border-radius: 4px;
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
        }}
        
        .stat-label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
        }}
        
        .section {{
            margin-bottom: 30px;
        }}
        
        .section h2 {{
            color: #007bff;
            font-size: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #ddd;
            margin-bottom: 15px;
        }}
        
        .check {{
            margin-bottom: 10px;
            padding: 10px;
            border-left: 4px solid #ddd;
            border-radius: 4px;
            background-color: #fafafa;
        }}
        
        .check.success {{
            border-left-color: #28a745;
            background-color: #f0f8f4;
        }}
        
        .check.failure {{
            border-left-color: #dc3545;
            background-color: #fdf8f8;
        }}
        
        .check.warning {{
            border-left-color: #ffc107;
            background-color: #fffbf0;
        }}
        
        .check.info {{
            border-left-color: #17a2b8;
            background-color: #f0f7f9;
        }}
        
        .check-header {{
            font-weight: 500;
            margin-bottom: 5px;
        }}
        
        .status {{
            font-weight: bold;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 12px;
        }}
        
        .check.success .status {{
            background-color: #28a745;
            color: white;
        }}
        
        .check.failure .status {{
            background-color: #dc3545;
            color: white;
        }}
        
        .check.warning .status {{
            background-color: #ffc107;
            color: black;
        }}
        
        .check-details {{
            font-size: 13px;
            color: #666;
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px solid rgba(0,0,0,0.1);
        }}
        
        footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>PGPYCIS Security Assessment Report</h1>
            <p class="timestamp">Generated: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
        </header>
        
        <div class="summary">
            <h3>Executive Summary</h3>
            <div class="summary-stats">
                <div class="stat-box">
                    <div class="stat-value">{self.statistics['TOTAL']}</div>
                    <div class="stat-label">Total Checks</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value" style="color: #28a745;">{self.statistics['SUCCESS']}</div>
                    <div class="stat-label">Passed</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value" style="color: #dc3545;">{self.statistics['FAILURE']}</div>
                    <div class="stat-label">Failed</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value" style="color: #ffc107;">{self.statistics['WARNING']}</div>
                    <div class="stat-label">Warnings</div>
                </div>
            </div>
        </div>
        
        <h2>Detailed Assessment</h2>
        {chr(10).join(sections)}
        
        <footer>
            <p>This report was generated by PGPYCIS (PostgreSQL CIS Compliance Assessment Tool).</p>
            <p>For more information, visit: <a href="https://github.com/hexacluster/pgpycis">https://github.com/hexacluster/pgpycis</a></p>
        </footer>
    </div>
</body>
</html>"""
        
        return html_template
