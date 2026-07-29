import frappe
import os
import io
import json
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


def compose_card_image(occasion_doc, name_text: str, type_text: str, code_text: str, layout_override: dict = None) -> Image.Image:
    """Build the composited card image for the given display text.

    Used both for real guest cards and for the layout designer's preview
    (with sample text and, optionally, an in-progress unsaved layout).
    """
    card_img = load_card_image(occasion_doc.card_design)
    width, height = card_img.size

    draw = ImageDraw.Draw(card_img)

    layout = layout_override
    if layout is None and occasion_doc.card_layout:
        try:
            layout = json.loads(occasion_doc.card_layout)
        except (ValueError, TypeError):
            layout = None

    if layout:
        # Custom positions from the drag-and-drop designer, stored as % of
        # image width (x, font_size, qr size) / height (y).
        def pct(cfg, key, default):
            try:
                return float(cfg.get(key, default))
            except (TypeError, ValueError):
                return default

        name_cfg = layout.get("guest_name", {})
        type_cfg = layout.get("card_type", {})
        code_cfg = layout.get("guest_code", {})
        qr_cfg   = layout.get("qr", {})

        name_font_size = max(int(width * pct(name_cfg, "font_size", 4.5) / 100), 6)
        type_font_size = max(int(width * pct(type_cfg, "font_size", 2.5) / 100), 6)
        code_font_size = max(int(width * pct(code_cfg, "font_size", 1.75) / 100), 6)

        name_rgb = hex_to_rgb(name_cfg.get("color") or occasion_doc.name_color or "#8B6914")
        type_rgb = hex_to_rgb(type_cfg.get("color") or occasion_doc.card_type_color or "#C8960C")
        code_rgb = hex_to_rgb(code_cfg.get("color") or "#555555")

        name_font = get_font(name_font_size, bold=True)
        type_font = get_font(type_font_size, bold=True)
        code_font = get_font(code_font_size, bold=False)

        name_x, name_y = int(width * pct(name_cfg, "x", 5) / 100), int(height * pct(name_cfg, "y", 88) / 100)
        type_x, type_y = int(width * pct(type_cfg, "x", 5) / 100), int(height * pct(type_cfg, "y", 92) / 100)
        code_x, code_y = int(width * pct(code_cfg, "x", 5) / 100), int(height * pct(code_cfg, "y", 95.5) / 100)

        draw.text((name_x, name_y), name_text, font=name_font, fill=name_rgb)
        draw.text((type_x, type_y), type_text, font=type_font, fill=type_rgb)
        draw.text((code_x, code_y), code_text, font=code_font, fill=code_rgb)

        qr_size = max(int(width * pct(qr_cfg, "size", 22) / 100), 20)
        qr_x = int(width * pct(qr_cfg, "x", 75) / 100)
        qr_y = int(height * pct(qr_cfg, "y", 74) / 100)
    else:
        name_font_size = int(occasion_doc.name_font_size or 36)
        name_color     = occasion_doc.name_color or "#8B6914"
        type_color     = occasion_doc.card_type_color or "#C8960C"
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

        draw.text((name_x, name_y), name_text, font=name_font, fill=name_rgb)
        draw.text((name_x, type_y), type_text, font=type_font, fill=type_rgb)
        draw.text((name_x, code_y), code_text, font=code_font, fill=code_rgb)

        # Position 2 — bottom right: QR code
        qr_size = int(width * 0.22)
        qr_x    = width - qr_size - int(width * 0.03)
        qr_y    = height - qr_size - int(height * 0.04)

    qr_buffer = generate_qr(code_text, occasion_doc.name)
    qr_img = Image.open(qr_buffer).convert("RGBA")
    qr_img = qr_img.resize((qr_size, qr_size), Image.LANCZOS)
    card_img.paste(qr_img, (qr_x, qr_y), qr_img)

    return card_img


def compose_card(occasion_doc, guest_row):
    card_img = compose_card_image(
        occasion_doc, guest_row.guest_name, guest_row.card_type, f"Code: {guest_row.guest_code}"
    )

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

    base = frappe.utils.get_url().rstrip("/")
    guest_row.download_url = f"{base}/invitee/download/occasion-card/{guest_row.guest_code}"

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


@frappe.whitelist()
def generate_preview(occasion_name: str, layout: str = None):
    """Whitelisted: (re)generate the styled sample preview shown as Card Design Preview.

    Uses placeholder guest text so it can run any time — even before any real
    guests exist. If `layout` (JSON string) is passed, it previews that
    in-progress layout instead of what's already saved on the Occasion.
    """
    occasion = frappe.get_doc("Occasion", occasion_name)
    if not occasion.card_design:
        frappe.throw("Please upload a Card Design image first.")

    layout_override = json.loads(layout) if layout else None
    card_img = compose_card_image(
        occasion, "Jina la Mgeni", "SINGLE", "Code: 000000", layout_override=layout_override
    )

    output_buffer = io.BytesIO()
    card_img.convert("RGB").save(output_buffer, format="JPEG", quality=90)
    output_buffer.seek(0)

    # Clean up the previous preview file so these don't pile up
    if occasion.card_preview_image:
        old_file = frappe.db.get_value("File", {"file_url": occasion.card_preview_image}, "name")
        if old_file:
            frappe.delete_doc("File", old_file, ignore_permissions=True, force=True)

    file_doc = frappe.get_doc({
        "doctype": "File",
        "file_name": f"card_preview_{occasion.name}.jpg",
        "content": output_buffer.read(),
        "is_private": 0,
        "folder": "Home/Attachments",
    })
    file_doc.save(ignore_permissions=True)

    frappe.db.set_value("Occasion", occasion.name, "card_preview_image", file_doc.file_url)
    frappe.db.commit()
    return file_doc.file_url
