import frappe
import requests

WABA_BASE_URL = "https://notify-web-assistant-api.beagile.africa"


def get_credentials():
    api_token = frappe.conf.get("notify_africa_waba_token") or frappe.conf.get("notify_africa_api_token")
    if not api_token:
        frappe.throw("notify_africa_waba_token (or notify_africa_api_token) is not set in site_config.json")
    return api_token


def normalize_phone(phone: str) -> str:
    return phone.replace("+", "").replace(" ", "").replace("-", "")


def send_text(phone: str, text: str) -> dict:
    """Send a plain WhatsApp text message via the Notify Africa WABA API"""
    api_token = get_credentials()

    response = requests.post(
        f"{WABA_BASE_URL}/v1/waba-api/messages/text",
        headers={
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        },
        json={"to": [normalize_phone(phone)], "text": text},
        timeout=30,
    )
    if not response.ok:
        frappe.throw(f"Notify Africa WABA API error ({response.status_code}): {response.text}")
    return response.json()


def send_template(phone: str, template_name: str, template_parameters: dict) -> dict:
    """Send an approved WhatsApp template message via the Notify Africa WABA API"""
    api_token = get_credentials()

    response = requests.post(
        f"{WABA_BASE_URL}/v1/waba-api/messages/template",
        headers={
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        },
        json={
            "to": [normalize_phone(phone)],
            "template_name": template_name,
            "template_parameters": template_parameters,
        },
        timeout=30,
    )
    if not response.ok:
        frappe.throw(f"Notify Africa WABA API error ({response.status_code}): {response.text}")
    return response.json()


def build_invitation_message(occasion_doc, guest_row) -> str:
    """Build the Swahili WhatsApp text message for a guest invitation"""
    date_str = frappe.utils.formatdate(occasion_doc.occasion_date, "dd-MM-yyyy")
    base = frappe.utils.get_url().rstrip("/")
    download_url = f"{base}/invitee/download/occasion-card/{guest_row.guest_code}"

    dress_line = f" DRESS CODE: {occasion_doc.dress_code}." if occasion_doc.dress_code else ""

    contacts = ""
    if occasion_doc.contact_1 and occasion_doc.contact_2:
        contacts = f"{occasion_doc.contact_1} na {occasion_doc.contact_2}"
    elif occasion_doc.contact_1:
        contacts = occasion_doc.contact_1
    contacts_line = f" MAWASILIANO: {contacts}." if contacts else ""

    return (
        f"Habari {guest_row.guest_name}, Unakaribishwa kwenye {occasion_doc.occasion_name}, "
        f"Kadi yako ni {guest_row.card_type} Na Code yako ni {guest_row.guest_code}. "
        f"Tarehe: {date_str}, Ukumbi: {occasion_doc.venue_name}. "
        f"MUDA: Saa {occasion_doc.occasion_time} ALASIRI."
        f"{dress_line}"
        f"{contacts_line} "
        f"Fika na sms hii au Download card yako kwa kubonyeza link hii\n"
        f"{download_url}"
    )


def send_invitation(occasion_doc, guest_row) -> dict:
    """Send the invitation text (with card download link) to a guest via WhatsApp"""
    if not guest_row.phone:
        frappe.throw(f"No phone number for {guest_row.guest_name}")
    if not guest_row.card_image:
        frappe.throw(f"Card not generated for {guest_row.guest_name}. Run Generate All Cards first.")

    message = build_invitation_message(occasion_doc, guest_row)
    result = send_text(guest_row.phone, message)

    frappe.get_doc({
        "doctype": "Comment",
        "comment_type": "Info",
        "reference_doctype": "Occasion",
        "reference_name": occasion_doc.name,
        "content": f"WhatsApp sent to {guest_row.guest_name} ({guest_row.phone}). Response: {result}"
    }).insert(ignore_permissions=True)

    return result


@frappe.whitelist()
def send_single(occasion_name: str, guest_code: str):
    """Whitelisted: send WhatsApp invitation to one guest by guest_code"""
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
