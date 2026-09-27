import os
from PIL import Image, ImageDraw, ImageFont

# Create a clean white receipt canvas
width, height = 800, 1100
img = Image.new('RGB', (width, height), color='#ffffff')
draw = ImageDraw.Draw(img)

# Try loading standard system font, or default
try:
    font_title = ImageFont.truetype('arial.ttf', 36)
    font_subtitle = ImageFont.truetype('arial.ttf', 20)
    font_body_bold = ImageFont.truetype('arialbd.ttf', 20)
    font_body = ImageFont.truetype('arial.ttf', 19)
    font_small = ImageFont.truetype('arial.ttf', 16)
except Exception:
    font_title = ImageFont.load_default()
    font_subtitle = font_title
    font_body_bold = font_title
    font_body = font_title
    font_small = font_title

# Header
draw.rectangle([(0, 0), (width, 140)], fill='#0f172a')
draw.text((40, 35), 'TECHWORLD ELECTRONICS', fill='#38bdf8', font=font_title)
draw.text((40, 85), 'Official Purchase Receipt and Tax Invoice', fill='#94a3b8', font=font_subtitle)

# Invoice Details Box
draw.rectangle([(40, 170), (760, 320)], fill='#f8fafc', outline='#e2e8f0', width=2)
draw.text((60, 190), 'INVOICE NUMBER:', fill='#64748b', font=font_small)
draw.text((60, 215), 'INV-2024-88492', fill='#0f172a', font=font_body_bold)

draw.text((420, 190), 'PURCHASE DATE:', fill='#64748b', font=font_small)
draw.text((420, 215), '2024-03-15', fill='#0f172a', font=font_body_bold)

draw.text((60, 255), 'CUSTOMER NAME:', fill='#64748b', font=font_small)
draw.text((60, 280), 'Ahmed Bilal Khan', fill='#0f172a', font=font_body)

draw.text((420, 255), 'PAYMENT STATUS:', fill='#64748b', font=font_small)
draw.text((420, 280), 'PAID - Credit Card (Visa 4242)', fill='#16a34a', font=font_body_bold)

# Table Header
y = 360
draw.rectangle([(40, y), (760, y + 45)], fill='#1e293b')
draw.text((60, y + 12), 'ITEM DESCRIPTION', fill='#ffffff', font=font_body_bold)
draw.text((420, y + 12), 'SERIAL NUMBER', fill='#ffffff', font=font_body_bold)
draw.text((640, y + 12), 'TOTAL', fill='#ffffff', font=font_body_bold)

# Table Rows
y += 45
items = [
    ('Smart 4K Ultra HD Display 55 inch', 'SN-98234-AX', '$749.00'),
    ('Extended 2-Year Full Protection Warranty', 'WAR-2YR-EL', '$100.00'),
]

for idx, (name, sn, price) in enumerate(items):
    row_bg = '#ffffff' if idx % 2 == 0 else '#f8fafc'
    draw.rectangle([(40, y), (760, y + 55)], fill=row_bg, outline='#f1f5f9', width=1)
    draw.text((60, y + 16), name, fill='#1e293b', font=font_body)
    draw.text((420, y + 16), sn, fill='#475569', font=font_body)
    draw.text((640, y + 16), price, fill='#0f172a', font=font_body_bold)
    y += 55

# Financial summary
y += 30
draw.line([(400, y), (760, y)], fill='#cbd5e1', width=1)
y += 15

draw.text((440, y), 'Subtotal:', fill='#64748b', font=font_body)
draw.text((640, y), '$849.00', fill='#1e293b', font=font_body)
y += 35

draw.text((440, y), 'Tax (8%):', fill='#64748b', font=font_body)
draw.text((640, y), '$67.92', fill='#1e293b', font=font_body)
y += 35

draw.rectangle([(420, y), (760, y + 55)], fill='#eff6ff', outline='#bfdbfe', width=2)
draw.text((440, y + 15), 'TOTAL AMOUNT:', fill='#1d4ed8', font=font_body_bold)
draw.text((640, y + 15), '$916.92', fill='#1d4ed8', font=font_body_bold)

# Footer & Warranty Note
y += 100
draw.rectangle([(40, y), (760, y + 130)], fill='#f0fdf4', outline='#bbf7d0', width=2)
draw.text((60, y + 18), 'ASSUREX VERIFIED PURCHASE & ELIGIBLE FOR WARRANTY', fill='#15803d', font=font_body_bold)
draw.text((60, y + 50), 'This invoice verifies genuine purchase and valid manufacturer serial activation.', fill='#166534', font=font_small)
draw.text((60, y + 75), 'Serial ID: SN-98234-AX | Item Code: ELEC-TV-55-4K | Status: ACTIVE', fill='#166534', font=font_small)
draw.text((60, y + 100), 'Store: TechWorld Flagship Store #104 | Authorized Retailer', fill='#166534', font=font_small)

# Save to paths
dest1 = os.path.abspath('frontend/public/mock_invoice.png')
dest2 = os.path.expanduser('~/Desktop/mock_invoice.png')
os.makedirs(os.path.dirname(dest1), exist_ok=True)
img.save(dest1, 'PNG')
try:
    img.save(dest2, 'PNG')
except Exception:
    pass

print(f'SAVED_TO: {dest1} and {dest2}')
