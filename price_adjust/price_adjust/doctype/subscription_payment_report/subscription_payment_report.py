# Copyright (c) 2026, Abdelrahman Elsayed and contributors
# For license information, please see license.txt

# import frappe

import frappe
from frappe.model.document import Document
from frappe.model import child_table_fields
from erpnext.accounts.doctype.journal_entry.journal_entry import (
	get_payment_entry_against_invoice,
)
from erpnext.accounts.utils import get_balance_on
from collections import defaultdict
import json
from frappe.utils import get_date_str


class SubscriptionPaymentReport(Document):
	def validate(self):
		self.set("enteries", [])
		filters = self._get_filters()
		frappe.log(filters)
		enteries = self._get_enteries(filters)

		for entry in enteries:
			invoice = frappe.get_doc(entry.voucher_type, entry.voucher_no)
			items = defaultdict(list)
			for item in invoice.items:

				items["item_code"].append(item.item_code)
				items["item_name"].append(item.item_name)
				items["item_qty"].append(item.qty)
				items["item_rate"].append(item.rate)
				items["item_total"].append(item.net_amount)

			refs = frappe.get_all(
				"Payment Entry Reference",
				filters={
					"reference_doctype": "Sales Invoice",
					"reference_name": entry.voucher_no,
				},
				fields=[
					"parent as voucher_no",
					"allocated_amount",
					"outstanding_amount",
					"total_amount",
					"due_date",
				],
			)

			parents = list({r["voucher_no"] for r in refs})
			pe_map = {}
			if parents:
				pe_map = {
					d.name: d
					for d in frappe.get_all(
						"Payment Entry",
						filters={"name": ["in", parents], "docstatus": 1},
						fields=[
							"name",
							"posting_date",
							"paid_amount",
							"mode_of_payment",
						],
					)
				}
			for r in refs:
				pe = pe_map.get(r["voucher_no"])
				if pe:
					r["posting_date"] = get_date_str(pe["posting_date"])
					r["paid_amount"] = pe["paid_amount"]
					r["mode_of_payment"] = pe["mode_of_payment"]

			payments = json.dumps(refs, default=str, ensure_ascii=False)

			self.append(
				"enteries",
				{
					"customer": invoice.customer,
					"customer_name": frappe.get_value(
						"Customer", invoice.customer, "customer_name"
					),
					"voucher_type": entry.voucher_type,
					"voucher_no": entry.voucher_no,
					"voucher_status": invoice.status,
					"date": entry.posting_date,
					"amount": invoice.grand_total,
					"remarks": entry.remarks,
					"total_amount": invoice.grand_total,
					"total_quantity": invoice.total_qty,
					"items": json.dumps(items, ensure_ascii=False),
					"payments": payments,
				},
			)

		self.set_outstanding()

	def _get_enteries(self, filters):
		return frappe.db.get_all(
			"GL Entry",
			filters=filters,
			fields=[
				"voucher_no",
				"voucher_type",
				"voucher_subtype",
				"debit",
				"posting_date",
				"debit",
				"remarks",
			],
			order_by="posting_date",
		)

	def set_outstanding(self):
		if self.customer:
			self.outstanding_amount = get_balance_on(
				date=self.to_date, party_type="Customer", party=self.customer
			)

	def _get_filters(self):
		filters = {
			"voucher_type": "Sales Invoice",
			"party_type": "Customer",
		}
		if self.from_date and self.to_date:
			filters["posting_date"] = ["between", [self.from_date, self.to_date]]
		elif self.from_date:
			filters["posting_date"] = [">=", self.from_date]
		else:
			filters["posting_date"] = ["<=", self.to_date]
		if self.customer:
			filters["party"] = self.customer

		if self.ignore_cancelled:
			filters["is_cancelled"] = 0

		return filters

	def autoname(self):
		self.name = f"{self.customer} {self.from_date} {self.to_date}"

