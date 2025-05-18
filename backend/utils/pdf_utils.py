import markdown
from weasyprint import HTML

def md_to_pdf(md_text: str, pdf_path):
    """
    Converts markdown string to PDF at `pdf_path`.
    Very light HTML template for nicer styling.
    """
    html_body = markdown.markdown(md_text, extensions=["fenced_code", "tables"])
    full_html = f"""
    <html>
      <head>
        <meta charset="utf-8">
        <style>
          body {{ font-family: Helvetica, Arial, sans-serif; margin: 2rem; }}
          h1,h2,h3 {{ color: #2c3e50; }}
          code {{ background: #f5f5f5; padding: 2px 4px; }}
        </style>
      </head>
      <body>{html_body}</body>
    </html>
    """
    HTML(string=full_html).write_pdf(str(pdf_path))
