import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image, ImageDraw, ImageFont
import io

OUTPUT_DIR = "test_data"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

INVOICE_TEXT = [
    "Invoice #: INV-2026-001",
    "Date: 2026-08-25",
    "Bill To: Mittelstand GmbH",
    "--------------------------------------------------",
    "Item 1: Software License      $ 1,500.00",
    "Item 2: Implementation        $ 2,000.00",
    "Item 3: Cloud Hosting (1 yr)  $   500.00",
    "--------------------------------------------------",
    "Subtotal:                     $ 4,000.00",
    "Tax (19%):                    $   760.00",
    "Total:                        $ 4,760.00"
]

def create_clean_pdf():
    filepath = os.path.join(OUTPUT_DIR, "clean_invoice.pdf")
    c = canvas.Canvas(filepath, pagesize=letter)
    c.setFont("Helvetica", 12)
    
    y = 750
    c.drawString(100, 800, "Acme Tech Solutions - Official Invoice")
    
    for line in INVOICE_TEXT:
        c.drawString(100, y, line)
        y -= 20
        
    c.save()
    print(f"Created {filepath}")

def create_scanned_pdf():
    # To simulate a scanned PDF, we draw text to an image, then save the image as a PDF.
    # This ensures there is NO text layer, forcing the vision fallback.
    filepath = os.path.join(OUTPUT_DIR, "scanned_invoice.pdf")
    
    # Create a white image
    img = Image.new('RGB', (800, 1000), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    
    # Draw text (using default font since we don't assume TTF fonts are installed)
    y = 50
    d.text((50, 20), "Acme Tech Solutions - Official Invoice", fill=(0, 0, 0))
    for line in INVOICE_TEXT:
        d.text((50, y), line, fill=(0, 0, 0))
        y += 15
        
    # Save as PDF
    img.save(filepath, "PDF", resolution=100.0)
    print(f"Created {filepath}")

if __name__ == "__main__":
    create_clean_pdf()
    create_scanned_pdf()
    print("Test data generation complete.")
