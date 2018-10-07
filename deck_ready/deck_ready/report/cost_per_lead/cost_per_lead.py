# Copyright (c) 2013, openetech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt,cstr
from erpnext.accounts.report.financial_statements import get_period_list

def execute(filters=None):
	columns, data = [], []
	columns = get_columns()
	data = get_data(filters)

	return columns, data

def get_columns():
	columns = [{
		"fieldname": "employee",
		"label": _("Agent"),
		"fieldtype": "Data",
		"width": 150
		},
		{
		"fieldname": "hours_per_lead",
		"label": _("Hours Per Lead"),
		"fieldtype": "Float",
		"width": 150
		},
		{
		"fieldname": "cost_per_lead",
		"label": _("Cost Per Lead"),
		"fieldtype": "Currency",
		"width": 150
		}
	]

	return columns

def get_data(filters):
	data = []
	from_date = filters["from_date"]
	to_date = filters["to_date"]
	employee_data = get_employees(from_date, to_date)

	for employee in employee_data:
		row = [employee["employee_name"]]
		hours_total = 0
		values = get_timsheet_data(employee["employee"], from_date, to_date)
		hours = 0
		pay_amt = 0
		pay_total = 0
		events = 0
		for value in values:
			hours += value["hours"]
		appt_data = get_appointment_data(employee["employee"], from_date, to_date)
		for app in appt_data:
			events += app["events"]
		hpl = 0
		if events > 0:
			hpl = round(hours / events,2)
			row.append(hpl)
		else:
			hpl = hours
			row.append(hpl)
		hours_total += hours

		pay_data = get_payroll_data(employee["employee"], from_date, to_date)
		for pay in pay_data:
			pay_amt += pay["pay"]
		cpl = 0
		if events > 0:
			cpl = round(pay_amt / events,2)
			row.append(cpl)
		else:
			cpl = pay_amt
			row.append(cpl)

		row.append(pay_amt)
		pay_total += pay_amt
		data.append(row)

	return data

def get_employees(from_date, to_date):
	employee_data = frappe.db.sql('''select 
										distinct tm.employee, tm.employee_name
									from
										`tabTimesheet` tm
									where
										tm.docstatus = 1
										and tm.end_date >= %s and tm.end_date <= %s''',
										 (from_date, to_date), as_dict=1)

	return employee_data

def get_timsheet_data(employee_id, from_date, to_date):
	timesheet_data = frappe.db.sql('''select 
										ifnull(sum(td.hours),0) as "hours"
									from
										`tabTimesheet` tm, `tabTimesheet Detail` td
									where
										tm.name = td.parent
										and tm.docstatus = 1
										and td.billable = 1
										and tm.employee = %s
										and tm.end_date >= %s and tm.end_date <= %s''',
										(employee_id, from_date, to_date), as_dict=1)

	return timesheet_data

def get_payroll_data(employee_id, from_date, to_date):
	payroll_data = frappe.db.sql('''select 
										ifnull(sum(ss.net_pay),0) as "pay"
									from
										`tabSalary Slip` ss
									where
										ss.docstatus = 1
										and ss.employee = %s
										and ss.end_date >= %s and ss.end_date <= %s''',
										(employee_id, from_date, to_date), as_dict=1)

	return payroll_data

def get_appointment_data(employee_id, from_date, to_date):
	appt_data = frappe.db.sql('''select 
										ifnull(count(ss.name),0) as "events"
									from
										`tabEvent` ss
									where
										ss.event_type = 'Public'
										and ss.owner in (select max(user_id)
														from `tabEmployee` 
														where name =%s)
										and ss.starts_on >= %s and ss.starts_on <= %s''',
										(employee_id, from_date, to_date), as_dict=1)

	return appt_data