frappe.ui.form.on("Occasion", {
    refresh(frm) {
        if (!frm.is_new()) {

            frm.add_custom_button(__("Generate All Cards"), function () {
                frappe.confirm(
                    __("Generate/regenerate QR code cards for all guests?"),
                    function () {
                        frappe.show_alert({ message: __("Generating cards..."), indicator: "blue" });
                        frm.call("generate_all_cards").then(r => {
                            const res = r.message;
                            frappe.show_alert({
                                message: __(`Done: ${res.success} success, ${res.failed} failed`),
                                indicator: res.failed > 0 ? "orange" : "green"
                            });
                            if (res.errors.length) {
                                frappe.msgprint({
                                    title: __("Errors"),
                                    message: res.errors.join("<br>"),
                                    indicator: "red"
                                });
                            }
                            frm.reload_doc();
                        });
                    }
                );
            }, __("Actions"));

            frm.add_custom_button(__("Send All WhatsApp"), function () {
                frappe.confirm(
                    __("Send WhatsApp invitations to all unsent guests?"),
                    function () {
                        frappe.show_alert({ message: __("Sending..."), indicator: "blue" });
                        frm.call("send_all_whatsapp").then(r => {
                            const res = r.message;
                            frappe.show_alert({
                                message: __(`Sent: ${res.success}, Failed: ${res.failed}`),
                                indicator: res.failed > 0 ? "orange" : "green"
                            });
                            if (res.errors.length) {
                                frappe.msgprint({
                                    title: __("WhatsApp Errors"),
                                    message: res.errors.join("<br>"),
                                    indicator: "red"
                                });
                            }
                        });
                    }
                );
            }, __("Actions"));

            // Stats dashboard banner
            const total    = frm.doc.guests.length;
            const confirmed = frm.doc.guests.filter(g => g.rsvp_status === "Confirmed").length;
            const pending   = frm.doc.guests.filter(g => g.rsvp_status === "Pending").length;
            const sent      = frm.doc.guests.filter(g => g.whatsapp_sent).length;
            const checkedIn = frm.doc.guests.filter(g => g.checked_in).length;

            frm.dashboard.add_comment(
                `<b>Total Guests:</b> ${total} &nbsp;|&nbsp;
                 <b style="color:green">Confirmed: ${confirmed}</b> &nbsp;|&nbsp;
                 <b style="color:orange">Pending: ${pending}</b> &nbsp;|&nbsp;
                 <b>WhatsApp Sent: ${sent}</b> &nbsp;|&nbsp;
                 <b>Checked In: ${checkedIn}</b>`,
                "blue", true
            );
        }
    }
});

// Per-row buttons in child table
frappe.ui.form.on("Occasion Guest", {
    generate_card(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        frappe.show_alert({ message: __("Generating card for " + row.guest_name), indicator: "blue" });
        frappe.call({
            method: "event_manager.utils.card_composer.compose_single_guest",
            args: { occasion_name: frm.doc.name, guest_name_field: row.guest_name },
            callback(r) {
                if (!r.exc) {
                    frappe.show_alert({ message: __("Card generated!"), indicator: "green" });
                    frm.reload_doc();
                }
            }
        });
    },

    send_whatsapp(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        frappe.confirm(
            __(`Send WhatsApp to ${row.guest_name} (${row.phone})?`),
            function () {
                frappe.call({
                    method: "event_manager.utils.whatsapp_sender.send_single",
                    args: { occasion_name: frm.doc.name, guest_code: row.guest_code },
                    callback(r) {
                        if (!r.exc) {
                            frappe.show_alert({ message: __("WhatsApp sent!"), indicator: "green" });
                            frm.reload_doc();
                        }
                    }
                });
            }
        );
    }
});
