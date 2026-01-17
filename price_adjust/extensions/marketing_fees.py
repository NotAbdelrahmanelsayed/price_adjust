from frappe.model.document import Document
from erpnext.accounts.doctype.subscription.subscription import Subscription
import frappe


class CustomSubscription(Subscription):
	def generate_invoice(
		self,
		from_date=None,
		to_date=None,
		posting_date=None,
	):
		invoice = self.create_invoice(from_date=from_date, to_date=to_date, posting_date=posting_date)
		if not self.get("custom_marketing_percentage", None):
			return invoice

		# Calculate the marketing fees
		plan_doc = frappe.get_doc("Subscription Plan", self.plans[0].plan)
		marketing_fees = plan_doc.cost * (self.custom_marketing_percentage / 100)


		# Validate Marketing Fees Item exists or create it
		if not frappe.db.exists("Item", "Marketing Fees"):
			item_group = frappe.get_value("Item", plan_doc.item, "item_group")
			marketing_item = frappe.get_doc({
				"doctype": "Item",
				"item_code":"Marketing Fees",
				"item_group": item_group
			})
			marketing_item.insert(ignore_permissions=True, ignore_mandatory=True)
		else:
			marketing_item = frappe.get_doc("Item", "Marketing Fees")



		# Append the `marketing fees` Item to the invoice.
		item = {
			"item_code": marketing_item.name,
			"item_name": marketing_item.item_name,
			"qty": 1,
			"uom": marketing_item.stock_uom,
			"rate": marketing_fees

		}
		invoice.append("items", item)
		invoice.save()
		return invoice

	def validate_not_submitable_invoice(self):
		if self.custom_marketing_percentage > 0 and self.submit_invoice == 1:
			frappe.throw("Can't add marketing fees if `Submit Generated Invoice` checked.")


	def validate(self):
		super().validate()
		self.validate_not_submitable_invoice()
