from __future__ import unicode_literals
import frappe, json
import frappe.desk.form.meta
import frappe.desk.form.load

from frappe import _

@frappe.whitelist()
def add_new_customer(customer_name, lead_name):
	if frappe.db.exists("Customer",{"customer_name": customer_name}):
		pass
	else:
		doc = frappe.new_doc("Customer")
		doc.customer_name = customer_name
		doc.lead_name = lead_name
		doc.insert()

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

@frappe.whitelist()
def make_warranty_from_communication(communication):
	if communication:
		comm_doc = frappe.get_doc("Communication", communication)
		if comm_doc.sender:
			contact = frappe.db.sql("""select name 
									from `tabContact`
									where email_id = %s""", (comm_doc.sender))
			if contact:
				contact_name = contact [0][0]
			else:
				frappe.throw(_("Contact does not exist for the sender of this email in the system"))
		else:
			frappe.throw(_("The communication document does not contain a valid sender"))
			
		if contact_name:
			customer = frappe.db.sql("""select link_name from `tabDynamic Link`
									where link_doctype = 'Customer'
									and parent = %s""", (contact_name))
		if customer:
			customer_name = customer [0][0]
		else:
			frappe.throw(_("The sender email ID is not a customer in the system. Hence warranty claim cannot be raised"))

		warranty_claim = frappe.get_doc({
			"doctype": "Warranty Claim",
			"customer": customer_name,
			"subject": comm_doc.subject,
			"complaint": comm_doc.content
		}).insert(ignore_permissions=True)

		comm_doc.reference_doctype = "Warranty Claim"
		comm_doc.reference_name = warranty_claim.name
		comm_doc.status = "Linked"
		comm_doc.save(ignore_permissions=True)

	return warranty_claim.name