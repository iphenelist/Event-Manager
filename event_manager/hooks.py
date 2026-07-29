app_name = "event_manager"
app_title = "Event Manager"
app_publisher = "Innocent P Metumba"
app_description = "A frappe custom app which enables to automate invitations via whatsapp and SMS"
app_email = "innocentphenelist@gmail.com"
app_license = "mit"

# Fixtures
# --------
# Ship the client/vendor portal role with the app so migrate creates it on a
# fresh site (mirrors gallery_store's "Gallery Client" role fixture).
fixtures = [
	{"dt": "Role", "filters": [["name", "in", ["Occasion Client"]]]},
]

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "event_manager",
# 		"logo": "/assets/event_manager/logo.png",
# 		"title": "Event Manager",
# 		"route": "/event_manager",
# 		"has_permission": "event_manager.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/event_manager/css/event_manager.css"
app_include_js = "/assets/event_manager/js/event_manager.js"

# include js, css files in header of web template
# web_include_css = "/assets/event_manager/css/event_manager.css"
# web_include_js = "/assets/event_manager/js/event_manager.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "event_manager/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "event_manager/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# Send Occasion Client users to their portal after login (they have no Desk access).
role_home_page = {
	"Occasion Client": "my-occasions",
}

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "event_manager.utils.jinja_methods",
# 	"filters": "event_manager.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "event_manager.install.before_install"
# after_install = "event_manager.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "event_manager.uninstall.before_uninstall"
# after_uninstall = "event_manager.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "event_manager.utils.before_app_install"
# after_app_install = "event_manager.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "event_manager.utils.before_app_uninstall"
# after_app_uninstall = "event_manager.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "event_manager.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "event_manager.notifications.get_notification_config"

# Permissions
# -----------
# Row-level isolation for Occasion:
# - permission_query_conditions filters every list query (Desk, REST
#   /api/resource, frappe.get_list) down to the logged-in client's own
#   assigned Occasion(s). Staff (System Manager / Event Manager) are
#   unrestricted, exactly as before.
# - has_permission guards single-document access.
permission_query_conditions = {
	"Occasion": "event_manager.permissions.occasion_query_conditions",
}

has_permission = {
	"Occasion": "event_manager.permissions.occasion_has_permission",
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Occasion Guest": {
        "before_insert": "event_manager.utils.qr_generator.before_insert_guest",
    }
}

website_route_rules = [
    {"from_route": "/invitee/download/occasion-card/<guest_code>", "to_route": "invitee/download/occasion-card"},
    {"from_route": "/gate-checkin", "to_route": "gate-checkin"},
    {"from_route": "/my-event/<path:occasion>", "to_route": "my-occasion"},
]
# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"event_manager.tasks.all"
# 	],
# 	"daily": [
# 		"event_manager.tasks.daily"
# 	],
# 	"hourly": [
# 		"event_manager.tasks.hourly"
# 	],
# 	"weekly": [
# 		"event_manager.tasks.weekly"
# 	],
# 	"monthly": [
# 		"event_manager.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "event_manager.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "event_manager.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "event_manager.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "event_manager.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["event_manager.utils.before_request"]
# after_request = ["event_manager.utils.after_request"]

# Job Events
# ----------
# before_job = ["event_manager.utils.before_job"]
# after_job = ["event_manager.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"event_manager.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

