# Copyright (c) 2013, openetech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt,cstr
from erpnext.accounts.report.financial_statements import get_period_list

def execute(filters=None):
	year = filters["Year"]
	period_list = get_period_list(year, year,"Monthly")
	columns, data = [], []
	columns = get_columns("Monthly", period_list)
	data = get_data(period_list, filters)

	return columns, data

def get_columns(periodicity, period_list):
	columns = [{
		"fieldname": "employee",
		"label": _("Agent"),
		"fieldtype": "Link",
		"options": "Employee",
		"width": 150
	}]
	for period in period_list:
		columns.append({
			"fieldname": period.key,
			"label": period.label,
			"fieldtype": "Float",
			"width": 150
		})
	if periodicity!="Yearly":
		columns.append({
			"fieldname": "total",
			"label": _("Total"),
			"fieldtype": "Float",
			"width": 150
		})

	return columns

def get_data(period_list, filters):
	data = []
	year = filters["Year"]
	year_dates = frappe.db.sql('''select 
										year_start_date, year_end_date
									from
										`tabFiscal Year`
									where
										year = %s''', (year), as_dict = 1)
	from_date, to_date = '',''
	for year in year_dates:
		from_date = year["year_start_date"]
		to_date = year["year_end_date"]

	employee_data = get_employees(from_date, to_date)

	for employee in employee_data:
		row = [employee["employee_name"]]
		pay_total = 0
		for period in period_list:
			values = get_payroll_data(employee["employee"], period["from_date"], period["to_date"])
			pay = 0
			for value in values:
				pay += value["pay"]
			row.append(pay)
			pay_total += pay
		row.append(pay_total)
		data.append(row)

	row = [""]
	data.append(row)
	row = ["Total Payments"]
	pay_total = 0
	for period in period_list:
		values = get_payroll_amounts(period["from_date"], period["to_date"])
		pay = 0
		for value in values:
			pay += value["pay"]
		row.append(pay)
		pay_total += pay
	row.append(pay_total)
	data.append(row)

	return data

def get_employees(from_date, to_date):
	employee_data = frappe.db.sql('''select 
										distinct tm.employee, tm.employee_name
									from
										`tabSalary Slip` tm
									where
										tm.docstatus = 1
										and tm.end_date >= %s and tm.end_date <= %s''',
										 (from_date, to_date), as_dict=1)

	return employee_data

def get_payroll_data(employee_id, from_date, to_date):
	timesheet_data = frappe.db.sql('''select 
										ifnull(sum(ss.net_pay),0) as "pay"
									from
										`tabSalary Slip` ss
									where
										ss.docstatus = 1
										and ss.employee = %s
										and ss.end_date >= %s and ss.end_date <= %s''',
										(employee_id, from_date, to_date), as_dict=1)

	return timesheet_data

def get_payroll_amounts(from_date, to_date):
	timesheet_data_hours = frappe.db.sql('''select 
										ifnull(sum(ss.net_pay),0) as "pay"
									from
										`tabSalary Slip` ss
									where
										ss.docstatus = 1
										and ss.end_date >= %s and ss.end_date <= %s''',
										(from_date, to_date), as_dict=1)
	
	return timesheet_data_hours