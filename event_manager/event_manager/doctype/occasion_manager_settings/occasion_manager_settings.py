import frappe
from frappe.model.document import Document


class OccasionManagerSettings(Document):
    def validate(self):
        if self.base_url and self.base_url.endswith("/"):
            self.base_url = self.base_url.rstrip("/")
