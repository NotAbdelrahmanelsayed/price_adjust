import frappe
from frappe.utils import add_days, add_months, add_years, today
from datetime import date
def auto_increase_by_interval():
	subscriptions = frappe.get_all(
		"Subscription",
		filters={
			"status": ["not in", ["Completed","Cancelled"]],
			"custom_auto_increase_by_interval": 1,
			"custom_next_fee_increase_date": ["<=", today()],
		},
		pluck="name",
	)

	if subscriptions:
		for sub in subscriptions:
			doc = frappe.get_doc("Subscription", sub)
			apply_increase_and_set_next_date(doc)

def validate_increase_by_interval(doc, method=None):
	if doc.get("custom_auto_increase_by_interval") != 1:
		return

	if not doc.custom_increase_interval:
		frappe.throw("Please Select Increase Interval (day, month, year)")

	if not doc.custom_increase_duration_count or int(doc.custom_increase_duration_count) <= 0:
		frappe.throw("increase duration count cannot be less than 1")

	if doc.custom_increase_percentage <= 0:
		frappe.throw("Increase percentage must be greater than 0")

def apply_increase_and_set_next_date(doc, method=None):
	if not doc.get("plans") or not doc.get("custom_increase_duration_count"):
		return

	if doc.get("custom_auto_increase_by_interval") != 1:
		return

	# Adjust subscription
	if doc.custom_increase_percentage:
		rows = doc.plans
		for row in rows:

			plan = frappe.get_doc("Subscription Plan", row.plan)
			cost = plan.cost * (1 + (doc.custom_increase_percentage / 100))
			frappe.db.set_value("Subscription Plan", plan.name, "cost", cost)

	init_next_increase_date(doc)

	return doc


def init_next_increase_date(doc, method=None):
	if doc.custom_auto_increase_by_interval != 1:
		return

	base_date = doc.custom_next_fee_increase_date or doc.start_date or today()
	n = int(doc.custom_increase_duration_count or 0)
	interval = doc.custom_increase_interval

	if not interval or n <= 0:
		return

	if interval == "Day":
		next_date = add_days(base_date, n)
	elif interval == "Week":
		next_date = add_days(base_date, n * 7)
	elif interval == "Month":
		next_date = add_months(base_date, n)
	elif interval == "Year":
		next_date = add_years(base_date, n)
	frappe.db.set_value("Subscription", doc.name, "custom_next_fee_increase_date", next_date)

@frappe.whitelist()
def force_increase(docname):
	doc = frappe.get_doc("Subscription", docname)
	apply_increase_and_set_next_date(doc)
	return doc.custom_next_fee_increase_date
