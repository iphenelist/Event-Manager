import frappe
from frappe import _

no_cache = 1


def get_context(context):
    if frappe.session.user == "Guest":
        # Sends guests to /login without confirming whether the event exists.
        frappe.throw(_("Please log in to view this event."), frappe.PermissionError)

    occasion_name = frappe.form_dict.occasion
    if not occasion_name:
        raise frappe.DoesNotExistError

    try:
        doc = frappe.get_doc("Occasion", occasion_name)
    except frappe.DoesNotExistError:
        frappe.clear_last_message()
        raise frappe.DoesNotExistError

    # Same clean 404 for "not yours" and "does not exist": no information
    # leakage via URL probing.
    if not doc.has_permission("read"):
        raise frappe.DoesNotExistError

    guests = sorted(doc.guests, key=lambda g: (g.guest_name or ""))

    context.no_cache = 1
    context.doc = doc
    context.guests = guests
    context.total = len(guests)
    context.confirmed = sum(1 for g in guests if g.rsvp_status == "Confirmed")
    context.pending = sum(1 for g in guests if g.rsvp_status == "Pending")
    context.declined = sum(1 for g in guests if g.rsvp_status == "Declined")
    context.checked_in = sum(1 for g in guests if g.checked_in)
    context.title = doc.occasion_name
    return context
