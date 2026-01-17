frappe.ui.form.on("Subscription", {
	refresh(frm) {
		frm.add_custom_button(
			__("<b>Force Increase Percentage</b>"),
			() =>
				frappe.call({
					method: "price_adjust.extensions.subscription.force_increase",
					args: { docname: frm.doc.name },
					callback() {
						frm.reload_doc();
					},
				}),
			__("Actions"),
		);
	},
});
