from __future__ import unicode_literals
import frappe, json
import frappe.desk.form.meta
import frappe.desk.form.load

from frappe import _

@frappe.whitelist()
def add_interaction(doc):
	"""allow any logged user to post a comment"""
	doc = frappe.get_doc(json.loads(doc))

 	if doc.doctype != "Interaction Log":
		frappe.throw(_("This method can only be used to create a Interaction Log"))

	doc.insert(ignore_permissions = True)

	return doc.as_dict()

@frappe.whitelist()
def create_todo(owner, assigned_by, description, date,reference_name,reference_type):
	"""allow any logged user to post toDo via interaction master"""
	todo = frappe.new_doc("ToDo")
	todo.owner = owner
	todo.assigned_by = assigned_by
	todo.description = description
	todo.date = date
	todo.reference_type = reference_type
	todo.reference_name = reference_name
	todo.role = "Sales User"
	todo.insert(ignore_permissions=True)

@frappe.whitelist()
def create_event(owner, subject, description, date,reference_type,reference_name,color, project_type, project_type_2,booking_date, call_source, responsible):
	if responsible:
		user = frappe.db.sql("""select full_name from `tabUser` where name = %s""", responsible)
		full_name = user [0]
	event = frappe.get_doc({	
		"doctype": "Event",
		"owner": owner,
		"subject": subject,
		"description": description,
		"starts_on":  date,
		"event_type": "Public",
		"ref_type": reference_type,
		"ref_name": reference_name,
		"color":color,
		"project_type":project_type,
		"project_type_2":project_type_2,
		"booking_date":booking_date,
		"event_date":date,
		"booking_source":call_source,
		"create_event":1,
		"responsible":responsible,
		"full_name":full_name
	})
	event.insert(ignore_permissions=True)