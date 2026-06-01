import frappe
import os
import io
from PIL import Image, ImageDraw, ImageFont
from event_manager.utils.qr_generator import generate_qr


def get_font(size: int, bold: bool = False):
    """Load best available serif font, fall back to default"""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
        "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def load_card_image(url: str) -> Image.Image:
    """Load card design image from Frappe file URL"""
    if url.startswith("/"):
        site_path = frappe.get_site_path()
        file_path = os.path.join(site_path, "public", url.lstrip("/"))
        if not os.path.exists(file_path):
            file_path = os.path.join(site_path, url.lstrip("/"))
        if not os.path.exists(file_path):
            frappe.throw(f"Card design file not found at: {url}")
        return Image.open(file_path).convert("RGBA")
    else:
        import requests
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return Image.open(io.BytesIO(response.content)).convert("RGBA")


def hex_to_rgb(hex_color: str):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def compose_card(occasion_doc, guest_row):
    settings = frappe.get_single("Occasion Manager Settings")

    card_img = load_card_image(occasion_doc.card_design)
    width, height = card_img.size

    draw = ImageDraw.Draw(card_img)

    name_font_size = int(settings.name_font_size or 36)
    name_color     = settings.name_color or "#8B6914"
    type_color     = settings.card_type_color or "#C8960C"
    code_color     = "#555555"

    name_rgb = hex_to_rgb(name_color)
    type_rgb = hex_to_rgb(type_color)
    code_rgb = hex_to_rgb(code_color)

    name_font = get_font(name_font_size, bold=True)
    type_font = get_font(int(name_font_size * 0.55), bold=True)
    code_font = get_font(int(name_font_size * 0.38), bold=False)

    # Position 1 — bottom left: guest name, card type, code
    name_x = int(width * 0.05)
    name_y = int(height * 0.88)
    type_y = name_y + name_font_size + 8
    code_y = type_y + int(name_font_size * 0.55) + 6

    draw.text((name_x, name_y), guest_row.guest_name, font=name_font, fill=name_rgb)
    draw.text((name_x, type_y), guest_row.card_type, font=type_font, fill=type_rgb)
    draw.text((name_x, code_y), f"Code: {guest_row.guest_code}", font=code_font, fill=code_rgb)

    # Position 2 — bottom right: QR code
    qr_size = int(width * 0.22)
    qr_x    = width - qr_size - int(width * 0.03)
    qr_y    = height - qr_size - int(height * 0.04)

    qr_buffer = generate_qr(guest_row.guest_code, occasion_doc.name)
    qr_img = Image.open(qr_buffer).convert("RGBA")
    qr_img = qr_img.resize((qr_size, qr_size), Image.LANCZOS)
    card_img.paste(qr_img, (qr_x, qr_y), qr_img)

    # Save final card as JPEG
    output_buffer = io.BytesIO()
    card_img.convert("RGB").save(output_buffer, format="JPEG", quality=93)
    output_buffer.seek(0)

    filename = f"occasion_card_{guest_row.guest_code}.jpg"

    file_doc = frappe.get_doc({
        "doctype": "File",
        "file_name": filename,
        "content": output_buffer.read(),
        "is_private": 0,
        "folder": "Home/Attachments",
    })
    file_doc.save(ignore_permissions=True)

    guest_row.card_image = file_doc.file_url

    base = (settings.base_url or frappe.utils.get_url()).rstrip("/")
    path = (settings.download_path or "/invitee/download/occasion-card").rstrip("/")
    guest_row.download_url = f"{base}{path}/{guest_row.guest_code}"

    frappe.db.commit()
    return file_doc.file_url


@frappe.whitelist()
def compose_single_guest(occasion_name: str, guest_name_field: str):
    """Whitelisted: compose card for a single guest by name"""
    occasion = frappe.get_doc("Occasion", occasion_name)
    for guest in occasion.guests:
        if guest.guest_name == guest_name_field:
            compose_card(occasion, guest)
            occasion.save()
            return {"success": True, "card_image": guest.card_image}
    frappe.throw(f"Guest '{guest_name_field}' not found in occasion '{occasion_name}'")
