import io
from xhtml2pdf import pisa
html_template = """<html><body>Test</body></html>"""
dest = io.BytesIO()
pisa.CreatePDF(html_template, dest=dest)
print("Success")
