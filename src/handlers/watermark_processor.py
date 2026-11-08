import os
import shutil
from urllib.parse import unquote_plus
import boto3
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    for record in event['Records']:
        bucket_name = record['s3']['bucket']['name']
        object_key = unquote_plus(record['s3']['object']['key'])
        
        # Skip if not inside uploads/ or is a folder marker
        if not object_key.startswith('uploads/') or object_key.endswith('/'):
            continue
            
        file_name = os.path.basename(object_key)
        file_id = os.path.splitext(file_name)[0]
        
        download_path = os.path.join('/tmp', file_name)
        output_filename = f"{file_id}.pdf"
        output_path = os.path.join('/tmp', f"watermarked_{output_filename}")
        
        # 1. Fetch PDF from S3 into /tmp
        s3_client.download_file(bucket_name, object_key, download_path)
        
        # 2. Apply watermark logic
        apply_watermark_to_pdf(download_path, output_path, watermark_text="DOCUSEAL VERIFIED")
        
        # 3. Upload output to processed/ prefix
        destination_key = f"processed/{output_filename}"
        s3_client.upload_file(output_path, bucket_name, destination_key)
        
        print(f"Successfully watermarked and processed {object_key} to {destination_key}")
        
    return {"status": "200 OK"}

def create_watermark_pdf(text, width, height):
    """Generates a single-page PDF canvas containing the semi-transparent text watermark."""
    packet = BytesIO()
    # Create a canvas matching the target page dimensions
    c = canvas.Canvas(packet, pagesize=(width, height))
    
    # Set font, size, and transparency (alpha)
    c.setFont("Helvetica-Bold", 40)
    c.setFillColorRGB(0.5, 0.5, 0.5, alpha=0.3)  # Gray with 30% opacity
    
    # Save state, translate, and rotate for a diagonal watermark banner
    c.saveState()
    c.translate(width / 2.0, height / 2.0)
    c.rotate(45)
    c.drawCentredString(0, 0, text)
    c.restoreState()
    
    c.save()
    packet.seek(0)
    return PdfReader(packet)

def apply_watermark_to_pdf(input_path, output_path, watermark_text="CONFIDENTIAL"):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    
    # Pre-generate the watermark layout for standard dimensions or handle per page
    for page in reader.pages:
        mediabox = page.mediabox
        width = float(mediabox.width)
        height = float(mediabox.height)
        
        watermark_reader = create_watermark_pdf(watermark_text, width, height)
        watermark_page = watermark_reader.pages[0]
        
        # Merge watermark layer onto the existing page
        page.merge_page(watermark_page)
        writer.add_page(page)
        
    with open(output_path, "wb") as output_file:
        writer.write(output_file)