import frappe
from frappe.utils import add_days, add_months, add_years, today
from datetime import date


def auto_increase_by_interval():
	subscriptions = frappe.get_all(
		"Subscription",
		filters={
			"status": "Active",
			"custom_auto_increase_by_interval": 1,
			"custom_next_fee_increase_date": ["<=", today()],
		},
		pluck="name",
	)

	if subscriptions:
		for sub in subscriptions:
			doc = frappe.get_doc("Subscription", sub)
			apply_increase_and_set_next_date(doc)
			doc.save(ignore_permissions=True)

def validate_increase_by_interval(doc, method=None):
	if doc.get("custom_auto_increase_by_interval") != 1:
		return

	if not doc.custom_increase_interval:
		frappe.throw("Please Select Increase Interval (day, month, year)")

	if not doc.custom_increase_duration_count or int(doc.custom_increase_duration_count) <= 0:
		frappe.throw("increase duration count cannot be less than 1")

	if doc.custom_increase_percentage <= 0:
		frappe.throw("increase duration count cannot be less than 0")

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
			plan.cost = plan.cost * (1 + (doc.custom_increase_percentage / 100))
			plan.save(ignore_permissions=True)

	# Compute the next date
	base_date = doc.get("custom_next_fee_increase_date") or doc.start_date
	n = int(doc.custom_increase_duration_count)

	if doc.custom_increase_interval == "Day":
		doc.custom_next_fee_increase_date = add_days(base_date, n)

	elif doc.custom_increase_interval == "Week":
		doc.custom_next_fee_increase_date = add_days(
			base_date, n * 7
		)

	elif doc.custom_increase_interval == "Month":
		doc.custom_next_fee_increase_date = add_months(
			base_date, n
		)

	elif doc.custom_increase_interval == "Year":
		doc.custom_next_fee_increase_date = add_years(base_date, n)

	return doc


def init_next_increase_date(doc, method=None):
    if doc.custom_auto_increase_by_interval != 1:
        return

    if doc.custom_next_fee_increase_date:
        return

    base_date = doc.start_date or today()
    n = int(doc.custom_increase_duration_count or 0)
    interval = doc.custom_increase_interval

    if not interval or n <= 0:
        return

    if interval == "Day":
        doc.custom_next_fee_increase_date = add_days(base_date, n)
    elif interval == "Week":
        doc.custom_next_fee_increase_date = add_days(base_date, n * 7)
    elif interval == "Month":
        doc.custom_next_fee_increase_date = add_months(base_date, n)
    elif interval == "Year":
        doc.custom_next_fee_increase_date = add_years(base_date, n)
