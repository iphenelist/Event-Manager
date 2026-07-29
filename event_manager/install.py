import frappe


def after_install():
    # Create Occasion Manager role
    if not frappe.db.exists("Role", "Occasion Manager"):
        r = frappe.new_doc("Role")
        r.role_name = "Occasion Manager"
        r.insert(ignore_permissions=True)

    frappe.db.commit()
    print("✅ Occasion Manager installed successfully!")
