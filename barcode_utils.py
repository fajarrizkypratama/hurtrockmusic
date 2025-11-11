
import io
import base64
from reportlab.graphics.barcode import code128, qr
from reportlab.graphics import renderPM
from reportlab.lib.units import mm
import qrcode
from PIL import Image, ImageDraw, ImageFont

def generate_code128_barcode(data, width=200, height=50):
    """
    Generate Code 128 barcode and return as base64 image
    """
    try:
        # Create barcode
        barcode = code128.Code128(data, barWidth=1.5, barHeight=height, humanReadable=True)
        
        # Convert to image
        img_buffer = io.BytesIO()
        renderPM.drawToFile(barcode, img_buffer, fmt='PNG', dpi=300)
        img_buffer.seek(0)
        
        # Convert to base64
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_base64}"
        
    except Exception as e:
        print(f"Barcode generation error: {e}")
        return None

def generate_qr_code(data, size=100):
    """
    Generate QR code and return as base64 image
    """
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=4,
            border=2,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")
        img = img.resize((size, size), Image.Resampling.LANCZOS)
        
        # Convert to base64
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_base64}"
        
    except Exception as e:
        print(f"QR code generation error: {e}")
        return None

def create_shipping_barcode_image(tracking_number, width=250, height=60):
    """
    Create a professional shipping barcode image similar to courier services
    """
    try:
        # Create white background
        img = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)
        
        # Generate barcode pattern (simplified)
        barcode_width = width - 40
        bar_width = 2
        space_width = 1
        x_pos = 20
        
        # Simple barcode pattern based on tracking number
        for i, char in enumerate(tracking_number):
            # Convert character to pattern
            char_value = ord(char) % 10
            pattern = format(char_value, '04b')  # 4-bit binary
            
            for bit in pattern:
                if bit == '1':
                    draw.rectangle([x_pos, 10, x_pos + bar_width, height - 20], fill='black')
                x_pos += bar_width + space_width
                
                if x_pos > width - 20:
                    break
            
            if x_pos > width - 20:
                break
        
        # Add tracking number text
        try:
            # Try to use a standard font
            font = ImageFont.truetype("arial.ttf", 12)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 12)
            except:
                font = ImageFont.load_default()
        
        # Calculate text position
        text_bbox = draw.textbbox((0, 0), tracking_number, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = (width - text_width) // 2
        
        draw.text((text_x, height - 18), tracking_number, fill='black', font=font)
        
        # Convert to base64
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_base64}"
        
    except Exception as e:
        print(f"Shipping barcode generation error: {e}")
        return None

def generate_order_qr_data(order):
    """
    Generate QR code data for order tracking
    """
    return f"""HURTROCK MUSIC STORE
Order ID: {order.id:08d}
Tracking: {order.tracking_number or f'HRT{order.id:08d}'}
Customer: {order.user.name}
Total: {order.formatted_total}
Date: {order.created_at.strftime('%d/%m/%Y')}
Status: {order.status.upper()}
Items: {len(order.order_items)} produk
Website: hurtrock.com"""
