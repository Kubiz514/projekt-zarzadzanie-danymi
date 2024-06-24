from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from typing import List
from datetime import datetime
from .schemas import DeviceReading

def generate_device_readings_pdf(readings: List[DeviceReading]) -> BytesIO:
    buffer = BytesIO()

    # Create a canvas
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Set up the title and headers
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(300, 750, "Device Readings Report")
    c.setFont("Helvetica", 12)
    c.drawString(50, 700, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Draw the table headers
    table_headers = ["ID", "Device ID", "Reading Date", "Value"]
    row_height = 20
    start_y = 650
    col_widths = [50, 100, 250, 100]

    c.setFont("Helvetica-Bold", 12)
    for i, header in enumerate(table_headers):
        c.drawString(50 + sum(col_widths[:i]), start_y, header)

    c.setFont("Helvetica", 12)
    y = start_y - row_height
    for reading in readings:
        data_row = [str(reading.id), str(reading.device_id), str(reading.reading_date), str(reading.value)]
        for i, data in enumerate(data_row):
            c.drawString(50 + sum(col_widths[:i]), y, data)
        y -= row_height

    # Save the PDF
    c.save()
    buffer.seek(0)
    return buffer
