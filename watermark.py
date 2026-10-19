import io
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_watermark_pdf(text, width, height):
    """Generates a single-page PDF containing the watermark text."""
    packet = io.BytesIO()
    # Create a canvas matching the target page dimensions
    c = canvas.Canvas(packet, pagesize=(width, height))
    
    # Configure watermark style (e.g., semi-transparent gray, angled text)
    c.saveState()
    c.setFont("Helvetica-Bold", 50)
    c.setFillColorRGB(0.6, 0.6, 0.6, alpha=0.4) # Light grey with 40% opacity
    
    # Translate and rotate for a diagonal watermark across the page center
    c.translate(width / 2, height / 2)
    c.rotate(45)
    c.drawCentredString(0, 0, text)
    c.restoreState()
    
    c.save()
    packet.seek(0)
    return PdfReader(packet)

def add_watermark(input_pdf_path, output_pdf_path, watermark_text="CONFIDENTIAL"):
    """Reads an input PDF, applies the watermark to all pages, and writes to output."""
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    # Generate the watermark template based on the first page's dimensions
    first_page = reader.pages[0]
    # Handle rotation if necessary, but standard mediabox works for most cases
    width = float(first_page.mediabox.width)
    height = float(first_page.mediabox.height)
    
    watermark_reader = create_watermark_pdf(watermark_text, width, height)
    watermark_page = watermark_reader.pages[0]

    # Merge watermark onto every page
    for page in reader.pages:
        page.merge_page(watermark_page)
        writer.add_page(page)

    with open(output_pdf_path, "wb") as output_file:
        writer.write(output_file)
    
    print(f"Successfully watermarked '{input_pdf_path}' -> saved as '{output_pdf_path}'")