import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from watermark import add_watermark

def generate_dummy_pdf(filename="sample.pdf"):
    """Creates a quick sample PDF to test against if you don't have one handy."""
    c = canvas.Canvas(filename, pagesize=letter)
    c.drawString(100, 700, "This is a test document to verify PDF watermarking.")
    c.save()

if __name__ == "__main__":
    sample_file = "sample.pdf"
    output_file = "output.pdf"

    # Generate a dummy test PDF if none exists in the folder
    if not os.path.exists(sample_file):
        generate_dummy_pdf(sample_file)

    # Run the watermarker
    add_watermark(sample_file, output_file, watermark_text="CONFIDENTIAL")