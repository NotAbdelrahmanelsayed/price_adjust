// Copyright (c) 2026, Abdelrahman Elsayed and contributors
// For license information, please see license.txt

frappe.ui.form.on("Subscription Payment Report", {
	refresh(frm) {
		$(".layout-side-section").hide();
		frm.add_custom_button(__("Print"), function () {
			frm.print_doc();
		});
	},
	validate(frm) {
		frm.set_value("enteries", []);
	},
});
