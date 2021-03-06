from __future__ import unicode_literals
import frappe, json
import frappe.desk.form.meta
import frappe.desk.form.load

from frappe import _
from frappe.utils import add_months, today, date_diff, getdate, add_days, flt, nowdate

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

@frappe.whitelist()
def create_maint_event(owner,subject,description,start_date,end_date,reference_name,reference_type,booking_date,call_source,responsible,subcontractor_assigned):
	if responsible:
		user = frappe.db.sql("""select full_name from `tabUser` where name = %s""", responsible)
		full_name = user [0]
	event = frappe.get_doc({	
		"doctype": "Event",
		"owner": owner,
		"subject": subject,
		"description": description,
		"starts_on":  start_date,
		"ends_on": end_date,
		"event_type": "Maintenance Visit",
		"ref_name": reference_name,
		"ref_type": reference_type,
		"color": "#5e3aa8",
		"event_date":start_date,
		"booking_source":call_source,
		"booking_date":booking_date,
		"create_event":1,
		"responsible":responsible,
		"full_name":full_name,
		"subcontractor_assigned": subcontractor_assigned
		
	})
	event.insert(ignore_permissions=True)

@frappe.whitelist()
def create_warranty_event(owner,subject,description,start_date,end_date,reference_name,reference_type,booking_date,call_source,responsible,subcontractor_assigned):
	if responsible:
		user = frappe.db.sql("""select full_name from `tabUser` where name = %s""", responsible)
		full_name = user [0]
	event = frappe.get_doc({	
		"doctype": "Event",
		"owner": owner,
		"subject": subject,
		"description": description,
		"starts_on":  start_date,
		"ends_on": end_date,
		"event_type": "Warranty Claim",
		"ref_name": reference_name,
		"ref_type": reference_type,
		"color": "#5e3aa8",
		"event_date":start_date,
		"booking_source":call_source,
		"booking_date":booking_date,
		"create_event":1,
		"responsible":responsible,
		"full_name":full_name,
		"subcontractor_assigned": subcontractor_assigned
		
	})
	event.insert(ignore_permissions=True)

def update_project_warranty_status():
	projects = frappe.db.sql('''select name, warranty_period_end_date, project_completion_date
							from `tabProject`''',as_dict=1)

	for project in projects:
		if project["warranty_period_end_date"] and project["project_completion_date"]:
			if date_diff(project["warranty_period_end_date"],nowdate()) >= 0:
				project_doc = frappe.get_doc("Project", project["name"])
				project_doc.warranty_status = "Active"
				project_doc.save()
			else:
				if date_diff((getdate(add_months(project["project_completion_date"], 120))), nowdate()) >= 0:
					project_doc = frappe.get_doc("Project", project["name"])
					project_doc.warranty_status = "Limited Stain Warranty"
					project_doc.save()
				else:
					project_doc = frappe.get_doc("Project", project["name"])
					project_doc.warranty_status = "No Warranty"
					project_doc.save()

def create_project(self, method):
	#Don't create project if it already exists
	name_string = self.name [:8]
	project_name = self.customer + " - "+ name_string
	project = frappe.db.sql("""select name from `tabProject` where name = %s """,project_name)
	if project:
		pass
	else:
		project = frappe.new_doc("Project")
		project.project_name = self.customer + " - "+ self.name
		project.owner = self.owner
		project.expected_start_date = self.transaction_date
		project.expected_end_date = self.delivery_date
		project.customer = self.customer
		project.sales_order = self.name
		project.project_type = "External"
		project.insert(ignore_permissions=True)
		tasks = frappe.db.sql('''select distinct task_name, task_owner 
					from `tabTask Template` 
					where project_type = %s''', (project.project_type), as_dict = 1)
		for task in tasks:
			task_doc = frappe.new_doc("Task")
			task_doc.subject = task["task_name"]
			task_doc.task_owner = task["task_owner"]
			task_doc.project = project.name
			task_doc.insert(ignore_permissions=True)

		sender_email = "notifications@deckready.net"
		msg = """ Hi, <br><br> Tasks related to Project: %s have been assigned to you. <br><br> 
				Please login to the ERP and complete your tasks."""%(project.name)
		task_owners = frappe.db.sql('''select distinct task_owner 
						from `tabTask Template` 
						where project_type = %s and task_owner IS NOT NULL''', (project.project_type), as_dict = 1)
		email_ids = ""
		for task in task_owners:
			email = task["task_owner"] + ";"
			email_ids += email
		frappe.sendmail(sender = sender_email, recipients = email_ids, subject = "Tasks assigned for Project - %s"%(project.name), content = msg)


def update_project_status(self, method):
	if self.project:
		status = frappe.db.sql('''select status 
						from `tabProject` 
						where name = %s''', (self.project))
		if status[0][0] in ["Open", "Ready to schedule"]:
			task_status = frappe.db.sql('''select status 
							from `tabTask` 
							where project = %s and status != "Completed"''', (self.project))
			if task_status:
				frappe.db.sql('''update `tabProject` set status = "Open" where name = %s''',(self.project))
				#project_doc = frappe.get_doc("Project", self.project)
				#project_doc.status = "Open"
				#project_doc.save()
			else:
				frappe.db.sql('''update `tabProject` set status = "Ready to schedule" where name = %s''',(self.project))
				#project_doc = frappe.get_doc("Project", self.project)
				#project_doc.status = "Ready to schedule"
				#project_doc.save()
