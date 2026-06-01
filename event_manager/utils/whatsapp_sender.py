import frappe
import requests
from frappe.utils import formatdate, get_url


def build_message(occasion_doc, guest_row, settings) -> str:
    """Build the Swahili WhatsApp text message as seen in the screenshot"""
    date_str = formatdate(occasion_doc.occasion_date, "dd-MM-yyyy")
    base = (settings.base_url or get_url()).rstrip("/")
    path = (settings.download_path or "/invitee/download/occasion-card").rstrip("/")
    download_url = f"{base}{path}/{guest_row.guest_code}"

    dress_line = f" DRESS CODE: {occasion_doc.dress_code}." if occasion_doc.dress_code else ""

    contacts = ""
    if occasion_doc.contact_1 and occasion_doc.contact_2:
        contacts = f"{occasion_doc.contact_1} na {occasion_doc.contact_2}"
    elif occasion_doc.contact_1:
        contacts = occasion_doc.contact_1
    contacts_line = f" MAWASILIANO: {contacts}." if contacts else ""

    message = (
        f"Habari {guest_row.guest_name}, Unakaribishwa kwenye {occasion_doc.occasion_name}, "
        f"Kadi yako ni {guest_row.card_type} Na Code yako ni {guest_row.guest_code}. "
        f"Tarehe: {date_str}, Ukumbi: {occasion_doc.venue_name}. "
        f"MUDA: Saa {occasion_doc.occasion_time} ALASIRI."
        f"{dress_line}"
        f"{contacts_line} "
        f"Fika na sms hii au Download card yako kwa kubonyeza link hii\n"
        f"{download_url}"
    )

    if settings.sender_label:
        message += f"\n\nSENT BY: {settings.sender_label}"

    return message


def get_card_absolute_url(guest_row, settings) -> str:
    """Return absolute public URL for the guest card image"""
    if not guest_row.card_image:
        return None
    base = (settings.base_url or get_url()).rstrip("/")
    url = guest_row.card_image
    return url if url.startswith("http") else f"{base}{url}"


def _send_fonnte(phone, message, image_url, token, api_url):
    url = api_url or "https://api.fonnte.com/send"
    headers = {"Authorization": token}
    if image_url:
        requests.post(url, headers=headers,
                      data={"target": phone, "message": image_url, "type": "image"},
                      timeout=30).raise_for_status()
    r = requests.post(url, headers=headers,
                      data={"target": phone, "message": message},
                      timeout=30)
    r.raise_for_status()
    return r.json()


def _send_wablas(phone, message, image_url, token, api_url):
    base = (api_url or "https://solo.wablas.com/api").rstrip("/")
    headers = {"Authorization": token, "Content-Type": "application/json"}
    if image_url:
        requests.post(f"{base}/send-image", headers=headers,
                      json={"phone": phone, "image": image_url, "caption": ""},
                      timeout=30).raise_for_status()
    r = requests.post(f"{base}/send-message", headers=headers,
                      json={"phone": phone, "message": message},
                      timeout=30)
    r.raise_for_status()
    return r.json()


def _send_custom(phone, message, image_url, token, api_url):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    r = requests.post(api_url, headers=headers,
                      json={"phone": phone, "message": message, "image": image_url or ""},
                      timeout=30)
    r.raise_for_status()
    return r.json()


def send_invitation(occasion_doc, guest_row):
    """Send card image + text message to a guest via WhatsApp"""
    settings = frappe.get_single("Occasion Manager Settings")

    if not settings.whatsapp_api_token:
        frappe.throw("WhatsApp API Token not set. Configure in Occasion Manager Settings.")
    if not settings.whatsapp_api_url:
        frappe.throw("WhatsApp API URL not set. Configure in Occasion Manager Settings.")
    if not guest_row.phone:
        frappe.throw(f"No phone number for {guest_row.guest_name}")
    if not guest_row.card_image:
        frappe.throw(f"Card not generated for {guest_row.guest_name}. Run Generate All Cards first.")

    phone     = guest_row.phone.replace("+", "").replace(" ", "").replace("-", "")
    message   = build_message(occasion_doc, guest_row, settings)
    image_url = get_card_absolute_url(guest_row, settings)
    token     = settings.get_password("whatsapp_api_token")
    api_url   = settings.whatsapp_api_url
    provider  = settings.whatsapp_provider or "Fonnte"

    if provider == "Fonnte":
        result = _send_fonnte(phone, message, image_url, token, api_url)
    elif provider == "WaBlas":
        result = _send_wablas(phone, message, image_url, token, api_url)
    else:
        result = _send_custom(phone, message, image_url, token, api_url)

    # Log to Comments
    frappe.get_doc({
        "doctype": "Comment",
        "comment_type": "Info",
        "reference_doctype": "Occasion",
        "reference_name": occasion_doc.name,
        "content": f"WhatsApp sent to {guest_row.guest_name} ({phone}). Response: {result}"
    }).insert(ignore_permissions=True)

    return result


@frappe.whitelist()
def send_single(occasion_name: str, guest_code: str):
    """Whitelisted: send WhatsApp to one guest by guest_code"""
    occasion = frappe.get_doc("Occasion", occasion_name)
    for guest in occasion.guests:
        if guest.guest_code == guest_code:
            result = send_invitation(occasion, guest)
            frappe.db.set_value("Occasion Guest", guest.name, {
                "whatsapp_sent": 1,
                "sent_at": frappe.utils.now()
            })
            return {"success": True, "result": result}
    frappe.throw(f"Guest with code '{guest_code}' not found in occasion '{occasion_name}'")
