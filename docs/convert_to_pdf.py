#!/usr/bin/env python3
"""
PDF Generation Script for TicketZero AI Documentation
Converts markdown documents to professional PDF format
"""

import os
import sys
from pathlib import Path
import markdown
from weasyprint import HTML, CSS
from datetime import datetime

def create_pdf_css():
    """Create professional CSS styling for PDF documents"""
    return CSS(string="""
        @page {
            margin: 1in;
            @top-center {
                content: "TicketZero AI - Confidential Business Documentation";
                font-size: 10px;
                color: #666;
            }
            @bottom-right {
                content: "Page " counter(page);
                font-size: 10px;
                color: #666;
            }
        }

        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 12px;
            line-height: 1.6;
            color: #333;
            max-width: none;
        }

        h1 {
            color: #2c3e50;
            font-size: 24px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-top: 30px;
            page-break-before: auto;
        }

        h2 {
            color: #34495e;
            font-size: 18px;
            margin-top: 25px;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }

        h3 {
            color: #2c3e50;
            font-size: 16px;
            margin-top: 20px;
        }

        h4 {
            color: #34495e;
            font-size: 14px;
            margin-top: 15px;
        }

        p {
            margin-bottom: 12px;
            text-align: justify;
        }

        ul, ol {
            margin: 10px 0;
            padding-left: 25px;
        }

        li {
            margin-bottom: 5px;
        }

        pre {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 4px;
            padding: 15px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 11px;
            overflow-x: auto;
            white-space: pre-wrap;
        }

        code {
            background-color: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 11px;
        }

        table {
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
        }

        th, td {
            border: 1px solid #dee2e6;
            padding: 8px 12px;
            text-align: left;
        }

        th {
            background-color: #f8f9fa;
            font-weight: bold;
            color: #2c3e50;
        }

        blockquote {
            border-left: 4px solid #3498db;
            background-color: #f8f9fa;
            padding: 15px;
            margin: 15px 0;
            font-style: italic;
        }

        .executive-summary {
            background-color: #e8f4fd;
            border: 2px solid #3498db;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }

        .financial-highlight {
            background-color: #d4edda;
            border: 2px solid #28a745;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
        }

        .warning {
            background-color: #fff3cd;
            border: 2px solid #ffc107;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
        }

        .page-break {
            page-break-before: always;
        }
    """)

def markdown_to_pdf(md_file_path, output_pdf_path):
    """Convert markdown file to professional PDF"""

    # Read markdown content
    with open(md_file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert markdown to HTML
    html_content = markdown.markdown(
        md_content,
        extensions=['tables', 'fenced_code', 'toc', 'codehilite']
    )

    # Add professional header
    html_with_header = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>TicketZero AI - Business Documentation</title>
    </head>
    <body>
        <div class="document-header">
            <h1 style="text-align: center; color: #2c3e50; border-bottom: 3px solid #3498db;">
                TicketZero AI - Professional Documentation
            </h1>
            <p style="text-align: center; color: #666; font-style: italic;">
                Generated on {datetime.now().strftime('%B %d, %Y')} | Confidential Business Information
            </p>
            <hr style="border: 1px solid #3498db; margin: 20px 0;">
        </div>
        {html_content}
        <div class="document-footer" style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ccc;">
            <p style="text-align: center; color: #666; font-size: 10px;">
                TicketZero AI © 2025 | Lead Developer: James | Status: Production Ready
            </p>
        </div>
    </body>
    </html>
    """

    # Generate PDF
    HTML(string=html_with_header).write_pdf(
        output_pdf_path,
        stylesheets=[create_pdf_css()]
    )

    print(f"✅ Generated PDF: {output_pdf_path}")

def main():
    """Generate all PDF documents"""
    docs_dir = Path(__file__).parent
    pdf_dir = docs_dir / "pdfs"
    pdf_dir.mkdir(exist_ok=True)

    # List of documents to convert
    documents = [
        ("TECHNICAL_WORKFLOW_DOCUMENTATION.md", "TicketZero_AI_Technical_Documentation.pdf")
    ]

    print("🚀 Starting PDF generation for TicketZero AI documentation...")
    print("=" * 80)

    for md_file, pdf_file in documents:
        md_path = docs_dir / md_file
        pdf_path = pdf_dir / pdf_file

        if md_path.exists():
            try:
                markdown_to_pdf(md_path, pdf_path)
            except Exception as e:
                print(f"❌ Error generating {pdf_file}: {e}")
        else:
            print(f"⚠️  Markdown file not found: {md_file}")

    print("=" * 80)
    print("✅ PDF generation complete!")
    print(f"📁 PDFs saved to: {pdf_dir.absolute()}")
    print()
    print("📋 Generated Documents:")
    for _, pdf_file in documents:
        pdf_path = pdf_dir / pdf_file
        if pdf_path.exists():
            print(f"   • {pdf_file}")

    print()
    print("🎯 Ready for presentation!")

if __name__ == "__main__":
    main()