import frappe


def get_context(context):
    context.page_title = "Occasion Gate Check-in"
    context.no_cache = 1
    code = frappe.form_dict.get("code")
    occasion = frappe.form_dict.get("occasion")
    context.auto_scan = bool(code)
    context.scan_code = code or ""
    context.scan_occasion = occasion or ""


@frappe.whitelist(allow_guest=True)
def validate_guest(guest_code: str, occasion_name: str = None):
    """Validate a guest QR code at the gate"""
    if not guest_code:
        return {"valid": False, "status": "Invalid", "message": "❌ Invalid QR Code", "color": "red"}

    filters = {"guest_code": guest_code}
    if occasion_name:
        filters["parent"] = occasion_name

    results = frappe.db.get_all(
        "Occasion Guest",
        filters=filters,
        fields=[
            "name", "guest_name", "card_type", "guest_code",
            "checked_in", "check_in_time", "rsvp_status", "parent"
        ],
        limit=1
    )

    if not results:
        return {
            "valid": False,
            "status": "Invalid",
            "message": "❌ Mgeni huyu hayupo kwenye orodha.",
            "color": "red"
        }

    guest = results[0]
    allow_reentry = frappe.db.get_value("Occasion", guest["parent"], "allow_reentry")

    if guest["checked_in"] and not allow_reentry:
        return {
            "valid": False,
            "status": "Already Used",
            "message": f"⚠️ Ameshaingia tayari saa {frappe.utils.format_datetime(guest['check_in_time'])}",
            "guest_name": guest["guest_name"],
            "card_type": guest["card_type"],
            "color": "orange"
        }

    # Mark checked in
    frappe.db.set_value("Occasion Guest", guest["name"], {
        "checked_in": 1,
        "check_in_time": frappe.utils.now(),
        "check_in_status": "Valid"
    })
    frappe.db.commit()

    occasion = frappe.db.get_value(
        "Occasion", guest["parent"],
        ["occasion_name", "couple_names"], as_dict=True
    )

    return {
        "valid": True,
        "status": "Valid",
        "message": f"✅ Karibu, {guest['guest_name']}!",
        "guest_name": guest["guest_name"],
        "card_type": guest["card_type"],
        "guest_code": guest["guest_code"],
        "occasion_name": occasion.occasion_name if occasion else "",
        "couple_names": occasion.couple_names if occasion else "",
        "color": "green"
    }
