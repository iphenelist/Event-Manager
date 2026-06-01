import frappe


def after_install():
    # Create default Occasion Manager Settings
    if not frappe.db.exists("Occasion Manager Settings", "Occasion Manager Settings"):
        s = frappe.new_doc("Occasion Manager Settings")
        s.whatsapp_provider  = "Fonnte"
        s.download_path      = "/invitee/download/occasion-card"
        s.checkin_page_title = "Occasion Gate Check-in"
        s.name_font_size     = 36
        s.name_color         = "#8B6914"
        s.card_type_color    = "#C8960C"
        s.insert(ignore_permissions=True)

    # Create Event Manager role
    if not frappe.db.exists("Role", "Event Manager"):
        r = frappe.new_doc("Role")
        r.role_name = "Event Manager"
        r.insert(ignore_permissions=True)

    frappe.db.commit()
    print("✅ Occasion Manager installed successfully!")
