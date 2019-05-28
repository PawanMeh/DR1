# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "deck_ready"
app_title = "Deck Ready"
app_publisher = "openetech"
app_description = "custom app"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "hello@openetech.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/deck_ready/css/deck_ready.css"
# app_include_js = "/assets/deck_ready/js/deck_ready.js"

# include js, css files in header of web template
# web_include_css = "/assets/deck_ready/css/deck_ready.css"
# web_include_js = "/assets/deck_ready/js/deck_ready.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "deck_ready.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "deck_ready.install.before_install"
# after_install = "deck_ready.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "deck_ready.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }
doc_events = {
        "Sales Order": {
                "on_submit": "deck_ready.custom_method.create_project"

        },
	"Task" : {
		"on_update": "deck_ready.custom_method.update_project_status"
	}
}
# Scheduled Tasks
# ---------------

scheduler_events = {
# 	"all": [
# 		"deck_ready.tasks.all"
# 	],
# 	"daily": [
# 		"deck_ready.tasks.daily"
# 	],
	"daily": [
		"deck_ready.custom_method.update_project_warranty_status"
	]
# 	"weekly": [
# 		"deck_ready.tasks.weekly"
# 	]
# 	"monthly": [
# 		"deck_ready.tasks.monthly"
# 	]
}

# Testing
# -------

# before_tests = "deck_ready.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "deck_ready.event.get_events"
# }

