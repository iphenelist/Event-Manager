import frappe

PRIVILEGED = {"System Manager", "Event Manager"}


def _is_privileged(user: str) -> bool:
    return user == "Administrator" or bool(PRIVILEGED & set(frappe.get_roles(user)))


def occasion_query_conditions(user=None):
    """permission_query_conditions hook for Occasion.

    Applied to every list query (Desk, REST /api/resource, frappe.get_list).
    Staff (System Manager / Event Manager) see everything, exactly as before.
    Everyone else (client/vendor portal users) only see the Occasion(s) they
    were manually assigned to via the client_user field.
    """
    user = user or frappe.session.user
    if _is_privileged(user):
        return ""

    return f"`tabOccasion`.`client_user` = {frappe.db.escape(user)}"


def occasion_has_permission(doc, ptype=None, user=None):
    """has_permission hook for Occasion.

    Guards single-document access. Controller hooks can only deny, never
    grant, so returning True simply means "no objection".
    """
    user = user or frappe.session.user
    if _is_privileged(user):
        return True

    if ptype in (None, "read", "select"):
        return doc.client_user == user

    # Client/vendor portal users never get write/create/delete/etc.
    return False
