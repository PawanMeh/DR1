# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt,cstr

def execute(filters=None):
	columns, data = [], []
	columns=get_columns()
	data=get_event_data(filters)
	total_inbound, total_outbound, confirmed_inbound, confirmed_outbound, cancelled_inbound, cancelled_outbound, total_bookings = 0,0,0,0,0,0,0
	for row in data:
		total_inbound = total_inbound + row["Total Inbound"]
		total_outbound = total_outbound + row["Total Outbound"]
		confirmed_inbound = confirmed_inbound + row["Confirmed Inbound"]
		confirmed_outbound = confirmed_outbound + row["Confirmed Outbound"]
		cancelled_inbound = cancelled_inbound + row["Cancelled Inbound"]
		cancelled_outbound = cancelled_outbound + row["Cancelled Outbound"]
		total_bookings = total_bookings + row["Total Bookings"]
	data.append({})
	data.append({'Total Inbound': total_inbound, 'Confirmed Inbound': confirmed_inbound, 
	'Responsible': 'Totals', 'Cancelled Outbound': cancelled_outbound, 'Total Bookings': total_bookings, 
	'Total Outbound': total_outbound, 'Confirmed Outbound': confirmed_outbound, 'Cancelled Inbound': cancelled_inbound})
	return columns, data
	
def get_columns():
	columns = [_("Full Name") + ":data:150", 
				_("Total Inbound") + ":Int:120",
				_("Total Outbound") + ":Int:120",
				_("Confirmed Inbound") + ":Int:150",
				_("Confirmed Outbound") + ":Int:150",
				_("Cancelled Inbound") + ":Int:150",
				_("Cancelled Outbound") + ":Int:150",
				 _("Total Bookings") + ":Int:120",
				_("Booking %") + ":Float:100",
				_("Booking % Over Total") + ":Float:120"
	]
	return columns

def get_event_data(filters):
	conditions=""
	if filters.from_date:
		conditions += " and date(creation) >= %(from_date)s"
	if filters.to_date:
		conditions += " and date(creation) <= %(to_date)s"

	data = frappe.db.sql("""select 
								distinct responsible as "Responsible", full_name as "Full Name"
							from 
								`tabEvent` 
							where ref_type in ('Lead', 'Opportunity', 'Customer') 
									and responsible is not null and responsible != '' %s"""
							% (conditions,),filters, as_dict=1)
	dl=list(data)
	overall_total_inbound_outbound = get_overall_total_inbound_outbound()
	for row in dl:
		row["Total Inbound"] = get_total_inbound(row["Responsible"])
		row["Total Outbound"]= get_total_outbound(row["Responsible"])
		row["Confirmed Inbound"] = get_confirmed_inbound(row["Responsible"])
		row["Confirmed Outbound"] = get_confirmed_outbound(row["Responsible"])
		row["Cancelled Inbound"] = get_cancelled_inbound(row["Responsible"])
		row["Cancelled Outbound"] = get_cancelled_outbound(row["Responsible"])
		row["Total Bookings"] = get_total_bookings(row["Responsible"])

		if row["Total Inbound"] + row["Total Outbound"] == 0:
			total_bookings = 1
		else:
			total_bookings = row["Total Inbound"] + row["Total Outbound"]

		if overall_total_inbound_outbound == 0:
			overall_total_inbound_outbound = 1
		else:
			overall_total_inbound_outbound

		row["Booking %"] = row["Total Bookings"] / total_bookings * 100
		row["Booking % Over Total"] = row["Total Bookings"] / (overall_total_inbound_outbound) * 100

	return dl
	
def get_total_inbound(responsible):
	count = frappe.db.sql("""select 
								count(name) 
							from 
								`tabEvent` 
							where ref_type in ('Lead', 'Opportunity', 'Customer')
								and responsible = %s
								and booking_source = 'Inbound'
								and status in ('Confirmed', 'Cancelled', 'Rescheduled')""",responsible)
	return flt(count[0][0]) if count else 0
	
def get_total_outbound(responsible):
	count = frappe.db.sql("""select 
								count(name) 
							from 
								`tabEvent` 
							where ref_type in ('Lead', 'Opportunity', 'Customer')
								and responsible = %s
								and booking_source = 'Outbound'
								and status in ('Confirmed', 'Cancelled', 'Rescheduled')""",responsible)
	return flt(count[0][0]) if count else 0

def get_confirmed_inbound(responsible):
	count = frappe.db.sql("""select 
								count(name) 
							from 
								`tabEvent` 
							where ref_type in ('Lead', 'Opportunity', 'Customer')
								and responsible = %s
								and booking_source = 'Inbound'
								and status = 'Confirmed'""",responsible)
	return flt(count[0][0]) if count else 0

def get_confirmed_outbound(responsible):
	count = frappe.db.sql("""select 
								count(name) 
							from 
								`tabEvent` 
							where ref_type in ('Lead', 'Opportunity', 'Customer')
								and responsible = %s
								and booking_source = 'Outbound'
								and status = 'Confirmed'""",responsible)
	return flt(count[0][0]) if count else 0

def get_cancelled_inbound(responsible):
	count = frappe.db.sql("""select 
								count(name) 
							from 
								`tabEvent` 
							where ref_type in ('Lead', 'Opportunity', 'Customer')
								and responsible = %s
								and booking_source = 'Outbound'
								and status = 'Cancelled'""",responsible)
	return flt(count[0][0]) if count else 0

def get_cancelled_outbound(responsible):
	count = frappe.db.sql("""select 
								count(name) 
							from 
								`tabEvent` 
							where ref_type in ('Lead', 'Opportunity', 'Customer')
								and responsible = %s
								and booking_source = 'Outbound'
								and status = 'Cancelled'""",responsible)
	return flt(count[0][0]) if count else 0

def get_total_bookings(responsible):
	count = frappe.db.sql("""select 
								count(name) 
							from 
								`tabEvent` 
							where ref_type in ('Lead', 'Opportunity', 'Customer')
								and responsible = %s
								and booking_source in ('Inbound', 'Outbound')	
								and status = 'Confirmed'""",responsible)
	return flt(count[0][0]) if count else 0

def get_overall_total_inbound_outbound():
	count = frappe.db.sql("""select 
								count(name) 
							from 
								`tabEvent` 
							where ref_type in ('Lead', 'Opportunity', 'Customer')
								and booking_source in ('Inbound', 'Outbound')	
								and status = 'Confirmed'""")
	return flt(count[0][0]) if count else 0
