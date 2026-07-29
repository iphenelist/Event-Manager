import frappe
from frappe import _

no_cache = 1


def get_context(context):
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Please log in to view your events."), frappe.PermissionError)

    context.no_cache = 1
    context.occasions = get_client_occasions(user)
    context.title = _("My Events")
    return context


def get_client_occasions(user: str):
    """The permission hooks already isolate rows, but filter explicitly too:
    defense in depth."""
    occasions = frappe.get_all(
        "Occasion",
        filters={"client_user": user},
        fields=["name", "occasion_name", "couple_names", "occasion_date", "venue_name", "status", "card_preview_image"],
        order_by="occasion_date desc, creation desc",
    )

    for occasion in occasions:
        stats = frappe.db.get_all(
            "Occasion Guest",
            filters={"parent": occasion.name},
            fields=["checked_in"],
        )
        occasion.guest_count = len(stats)
        occasion.checked_in_count = sum(1 for g in stats if g.checked_in)

    return occasions
