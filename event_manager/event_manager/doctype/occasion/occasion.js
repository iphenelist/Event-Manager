frappe.ui.form.on("Occasion", {
    refresh(frm) {
        if (!frm.is_new()) {
            render_occasion_statistics(frm);
        }
    },

    generate_cards_btn(frm) {
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
    },

    design_layout_btn(frm) {
        if (!frm.doc.card_design) {
            frappe.msgprint(__("Please upload a Card Design image first."));
            return;
        }
        open_card_layout_designer(frm);
    },

    send_whatsapp_btn(frm) {
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
    },

    send_sms_btn(frm) {
        frappe.confirm(
            __("Send SMS invitations to all unsent guests?"),
            function () {
                frappe.show_alert({ message: __("Sending..."), indicator: "blue" });
                frm.call("send_all_sms").then(r => {
                    const res = r.message;
                    frappe.show_alert({
                        message: __(`Sent: ${res.success}, Failed: ${res.failed}`),
                        indicator: res.failed > 0 ? "orange" : "green"
                    });
                    if (res.errors.length) {
                        frappe.msgprint({
                            title: __("SMS Errors"),
                            message: res.errors.join("<br>"),
                            indicator: "red"
                        });
                    }
                });
            }
        );
    }
});

function render_occasion_statistics(frm) {
    const $wrapper = frm.get_field("statistics_html").$wrapper;
    const guests = frm.doc.guests || [];

    const total     = guests.length;
    const confirmed = guests.filter(g => g.rsvp_status === "Confirmed").length;
    const pending    = guests.filter(g => g.rsvp_status === "Pending").length;
    const declined   = guests.filter(g => g.rsvp_status === "Declined").length;
    const sent       = guests.filter(g => g.whatsapp_sent).length;
    const checkedIn  = guests.filter(g => g.checked_in).length;
    const notCheckedIn = total - checkedIn;

    // Validated categorical/status palette — see dataviz skill references/palette.md.
    // Stat tiles use text-safe steps; the two pies use the fixed status triad
    // (good/warning/critical) and a highlight-vs-neutral pair, both legend-labeled.
    const stats = [
        { label: __("Total Guests"),   value: total,     v: "--stat-blue" },
        { label: __("Confirmed"),      value: confirmed, v: "--stat-good" },
        { label: __("Pending"),        value: pending,   v: "--stat-orange" },
        { label: __("Declined"),       value: declined,  v: "--stat-critical" },
        { label: __("WhatsApp Sent"),  value: sent,       v: "--stat-aqua" },
        { label: __("Checked In"),     value: checkedIn, v: "--stat-yellow" }
    ];

    const cardsHtml = stats
        .map(
            s => `
        <div class="occ-stat-card">
            <div class="occ-stat-num" style="color:var(${s.v});">${s.value}</div>
            <div class="occ-stat-label">${s.label}</div>
        </div>`
        )
        .join("");

    $wrapper.html(`
        <style>
            .occasion-stats {
                --stat-blue:     #2a78d6;
                --stat-orange:   #eb6834;
                --stat-aqua:     #1baf7a;
                --stat-yellow:   #eda100;
                --stat-good:     #006300;
                --stat-warning:  #fab219;
                --stat-critical: #d03b3b;
                --stat-neutral:  #c3c2b7;
                padding: 6px 0 16px;
            }
            @media (prefers-color-scheme: dark) {
                :root:where(:not([data-theme="light"])) .occasion-stats {
                    --stat-blue: #3987e5; --stat-orange: #d95926; --stat-aqua: #199e70;
                    --stat-yellow: #c98500; --stat-good: #0ca30c; --stat-warning: #fab219;
                    --stat-critical: #d03b3b; --stat-neutral: #383835;
                }
            }
            [data-theme="dark"] .occasion-stats {
                --stat-blue: #3987e5; --stat-orange: #d95926; --stat-aqua: #199e70;
                --stat-yellow: #c98500; --stat-good: #0ca30c; --stat-warning: #fab219;
                --stat-critical: #d03b3b; --stat-neutral: #383835;
            }
            .occ-stat-row { display:flex; gap:12px; flex-wrap:wrap; margin-bottom:22px; }
            .occ-stat-card {
                flex:1; min-width:130px; background:var(--card-bg,#fff);
                border:1px solid var(--border-color,#d1d5db); border-radius:10px;
                padding:14px 12px; text-align:center;
            }
            .occ-stat-num { font-size:26px; font-weight:800; line-height:1.2; }
            .occ-stat-label { font-size:12px; color:var(--text-muted,#6b7280); margin-top:4px; font-weight:600; }
            .occ-chart-row { display:flex; gap:24px; flex-wrap:wrap; }
            .occ-chart-col { flex:1; min-width:280px; }
            .occ-chart-title { font-size:13px; font-weight:700; margin-bottom:6px; }
        </style>
        <div class="occasion-stats">
            <div class="occ-stat-row">${cardsHtml}</div>
            <div class="occ-chart-row">
                <div class="occ-chart-col">
                    <div class="occ-chart-title">${__("RSVP Status")}</div>
                    <div id="occasion-rsvp-chart"></div>
                </div>
                <div class="occ-chart-col">
                    <div class="occ-chart-title">${__("Gate Check-in")}</div>
                    <div id="occasion-checkin-chart"></div>
                </div>
            </div>
        </div>
    `);

    if (total === 0) {
        $wrapper.find(".occasion-stats").append(
            `<p class="text-muted small" style="margin-top:12px;">${__("Add guests to see statistics.")}</p>`
        );
        return;
    }

    const isDark = document.documentElement.getAttribute("data-theme") === "dark"
        || (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches
            && document.documentElement.getAttribute("data-theme") !== "light");

    // Status triad (good/warning/critical) — fixed, never themed, same hex both modes.
    new frappe.Chart("#occasion-rsvp-chart", {
        data: {
            labels: [__("Confirmed"), __("Pending"), __("Declined")],
            datasets: [{ values: [confirmed, pending, declined] }]
        },
        type: "pie",
        height: 220,
        colors: ["#0ca30c", "#fab219", "#d03b3b"]
    });

    // Highlight (categorical blue) vs. neutral (chrome gray) — binary state.
    new frappe.Chart("#occasion-checkin-chart", {
        data: {
            labels: [__("Checked In"), __("Not Yet")],
            datasets: [{ values: [checkedIn, notCheckedIn] }]
        },
        type: "pie",
        height: 220,
        colors: isDark ? ["#3987e5", "#383835"] : ["#2a78d6", "#c3c2b7"]
    });
}

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
                    method: "event_manager.api.whatsapp.send_single",
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
    },

    send_sms(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        frappe.confirm(
            __(`Send SMS to ${row.guest_name} (${row.phone})?`),
            function () {
                frappe.call({
                    method: "event_manager.api.sms.send_single",
                    args: { occasion_name: frm.doc.name, guest_code: row.guest_code },
                    callback(r) {
                        if (!r.exc) {
                            frappe.show_alert({ message: __("SMS sent!"), indicator: "green" });
                            frm.reload_doc();
                        }
                    }
                });
            }
        );
    }
});

// -----------------------------------------------------------------------
// Drag-and-drop invitation card layout designer
// -----------------------------------------------------------------------

const CARD_DESIGNER_DEFAULT_LAYOUT = {
    guest_name: { x: 5,   y: 88,   font_size: 4.5,  color: "#8B6914" },
    card_type:  { x: 5,   y: 92,   font_size: 2.5,  color: "#C8960C" },
    guest_code: { x: 5,   y: 95.5, font_size: 1.75, color: "#555555" },
    qr:         { x: 75,  y: 74,  size: 22 }
};

const CARD_DESIGNER_HTML = `
<div class="card-designer">
  <p class="text-muted small">${__("Buruta vipengele (guest name, card type, code, QR) kwenye kadi ili kuvipanga. Tumia rangi/slider chini kubadilisha maandishi. Buruta pembe ya kijani kubadilisha ukubwa wa QR.")}</p>
  <div id="cd-canvas" style="position:relative; max-width:640px; margin:0 auto; border:1px solid #d1d5db; user-select:none;">
    <img id="cd-bg-img" style="display:block; width:100%; height:auto; pointer-events:none;" />
    <div class="cd-layer" data-key="guest_name" style="position:absolute; cursor:move; font-weight:bold; white-space:nowrap; padding:2px 4px; border:1px dashed #D4A017; background:rgba(255,255,255,.2); line-height:1.2;">Jina la Mgeni</div>
    <div class="cd-layer" data-key="card_type" style="position:absolute; cursor:move; font-weight:bold; white-space:nowrap; padding:2px 4px; border:1px dashed #D4A017; background:rgba(255,255,255,.2); line-height:1.2;">Aina ya Kadi</div>
    <div class="cd-layer" data-key="guest_code" style="position:absolute; cursor:move; white-space:nowrap; padding:2px 4px; border:1px dashed #D4A017; background:rgba(255,255,255,.2); line-height:1.2;">Code: 000000</div>
    <div class="cd-layer" data-key="qr" style="position:absolute; cursor:move; border:2px dashed #16a34a; background:rgba(22,163,74,.15); display:flex; align-items:center; justify-content:center; color:#16a34a; font-size:11px; font-weight:700; box-sizing:border-box;">
      QR
      <div class="cd-resize-handle" style="position:absolute; right:-7px; bottom:-7px; width:14px; height:14px; background:#16a34a; border-radius:50%; cursor:nwse-resize;"></div>
    </div>
  </div>
  <div class="cd-controls" style="display:flex; gap:20px; flex-wrap:wrap; margin-top:16px;">
    <div class="cd-control" data-key="guest_name">
      <label class="small text-muted">${__("Jina la Mgeni")}</label><br>
      <input type="color" class="cd-color">
      <input type="range" class="cd-size" min="1.5" max="8" step="0.1" style="width:110px; vertical-align:middle;">
    </div>
    <div class="cd-control" data-key="card_type">
      <label class="small text-muted">${__("Aina ya Kadi")}</label><br>
      <input type="color" class="cd-color">
      <input type="range" class="cd-size" min="1" max="6" step="0.1" style="width:110px; vertical-align:middle;">
    </div>
    <div class="cd-control" data-key="guest_code">
      <label class="small text-muted">${__("Namba (Code)")}</label><br>
      <input type="color" class="cd-color">
      <input type="range" class="cd-size" min="0.8" max="4" step="0.1" style="width:110px; vertical-align:middle;">
    </div>
  </div>
</div>`;

function open_card_layout_designer(frm) {
    let currentLayout = null;
    try {
        currentLayout = frm.doc.card_layout ? JSON.parse(frm.doc.card_layout) : null;
    } catch (e) {
        currentLayout = null;
    }
    const layout = Object.assign(
        {},
        CARD_DESIGNER_DEFAULT_LAYOUT,
        currentLayout
            ? {
                  guest_name: Object.assign({}, CARD_DESIGNER_DEFAULT_LAYOUT.guest_name, currentLayout.guest_name),
                  card_type: Object.assign({}, CARD_DESIGNER_DEFAULT_LAYOUT.card_type, currentLayout.card_type),
                  guest_code: Object.assign({}, CARD_DESIGNER_DEFAULT_LAYOUT.guest_code, currentLayout.guest_code),
                  qr: Object.assign({}, CARD_DESIGNER_DEFAULT_LAYOUT.qr, currentLayout.qr)
              }
            : {}
    );

    const dialog = new frappe.ui.Dialog({
        title: __("Design Card Layout"),
        size: "extra-large",
        fields: [{ fieldtype: "HTML", fieldname: "designer_html", options: CARD_DESIGNER_HTML }],
        primary_action_label: __("Save Layout"),
        primary_action() {
            const newLayout = collect_layout();
            dialog.set_primary_action(__("Saving..."), null);
            frm.set_value("card_layout", JSON.stringify(newLayout));
            frm.save().then(() => {
                frappe.call({
                    method: "event_manager.utils.card_composer.generate_preview",
                    args: { occasion_name: frm.doc.name },
                    callback() {
                        dialog.hide();
                        frm.reload_doc();
                        frappe.show_alert({ message: __("Card layout saved"), indicator: "green" });
                    },
                    error() {
                        dialog.hide();
                        frappe.show_alert({ message: __("Layout saved, but preview generation failed"), indicator: "orange" });
                    }
                });
            });
        },
        secondary_action_label: __("Reset to Default"),
        secondary_action() {
            apply_layout(CARD_DESIGNER_DEFAULT_LAYOUT);
        }
    });

    dialog.show();

    const $wrapper = dialog.$wrapper;
    const $canvas = $wrapper.find("#cd-canvas");
    const $img = $wrapper.find("#cd-bg-img");

    function apply_layout(lay) {
        const cw = $canvas.width();
        const ch = $canvas.height();
        ["guest_name", "card_type", "guest_code"].forEach(key => {
            const cfg = lay[key];
            const $el = $wrapper.find(`.cd-layer[data-key="${key}"]`);
            $el.css({
                left: (cfg.x / 100) * cw + "px",
                top: (cfg.y / 100) * ch + "px",
                fontSize: (cfg.font_size / 100) * cw + "px",
                color: cfg.color
            });
            $wrapper.find(`.cd-control[data-key="${key}"] .cd-color`).val(cfg.color);
            $wrapper.find(`.cd-control[data-key="${key}"] .cd-size`).val(cfg.font_size);
        });
        const qcfg = lay.qr;
        const qsize = (qcfg.size / 100) * cw;
        $wrapper.find('.cd-layer[data-key="qr"]').css({
            left: (qcfg.x / 100) * cw + "px",
            top: (qcfg.y / 100) * ch + "px",
            width: qsize + "px",
            height: qsize + "px"
        });
    }

    function collect_layout() {
        const cw = $canvas.width();
        const ch = $canvas.height();
        const result = {};
        ["guest_name", "card_type", "guest_code"].forEach(key => {
            const $el = $wrapper.find(`.cd-layer[data-key="${key}"]`);
            const pos = $el.position();
            result[key] = {
                x: +((pos.left / cw) * 100).toFixed(2),
                y: +((pos.top / ch) * 100).toFixed(2),
                font_size: +((parseFloat($el.css("font-size")) / cw) * 100).toFixed(2),
                color: $wrapper.find(`.cd-control[data-key="${key}"] .cd-color`).val()
            };
        });
        const $qr = $wrapper.find('.cd-layer[data-key="qr"]');
        const qpos = $qr.position();
        result.qr = {
            x: +((qpos.left / cw) * 100).toFixed(2),
            y: +((qpos.top / ch) * 100).toFixed(2),
            size: +(($qr.width() / cw) * 100).toFixed(2)
        };
        return result;
    }

    $img.on("load", () => apply_layout(layout));
    $img.attr("src", frm.doc.card_design);
    if ($img[0].complete && $img[0].naturalWidth) {
        apply_layout(layout);
    }

    let dragEl = null, dragOffsetX = 0, dragOffsetY = 0;
    let resizeEl = null, resizeStartSize = 0, resizeStartX = 0;

    $wrapper.find(".cd-layer").on("pointerdown", function (e) {
        if ($(e.target).hasClass("cd-resize-handle")) return;
        dragEl = $(this);
        dragOffsetX = e.clientX - dragEl.offset().left;
        dragOffsetY = e.clientY - dragEl.offset().top;
        e.preventDefault();
    });

    $wrapper.find(".cd-resize-handle").on("pointerdown", function (e) {
        resizeEl = $(this).closest(".cd-layer");
        resizeStartSize = resizeEl.width();
        resizeStartX = e.clientX;
        e.preventDefault();
        e.stopPropagation();
    });

    $(document).on("pointermove.cardDesigner", function (e) {
        if (dragEl) {
            const canvasOffset = $canvas.offset();
            let left = e.clientX - canvasOffset.left - dragOffsetX;
            let top = e.clientY - canvasOffset.top - dragOffsetY;
            left = Math.max(0, Math.min(left, $canvas.width() - dragEl.outerWidth()));
            top = Math.max(0, Math.min(top, $canvas.height() - dragEl.outerHeight()));
            dragEl.css({ left: left + "px", top: top + "px" });
        }
        if (resizeEl) {
            let newSize = Math.max(20, resizeStartSize + (e.clientX - resizeStartX));
            const maxSize = $canvas.width() - resizeEl.position().left;
            newSize = Math.min(newSize, maxSize, $canvas.height() - resizeEl.position().top);
            resizeEl.css({ width: newSize + "px", height: newSize + "px" });
        }
    });

    $(document).on("pointerup.cardDesigner", function () {
        dragEl = null;
        resizeEl = null;
    });

    $wrapper.find(".cd-color").on("input", function () {
        const key = $(this).closest(".cd-control").data("key");
        $wrapper.find(`.cd-layer[data-key="${key}"]`).css("color", $(this).val());
    });

    $wrapper.find(".cd-size").on("input", function () {
        const key = $(this).closest(".cd-control").data("key");
        const cw = $canvas.width();
        $wrapper.find(`.cd-layer[data-key="${key}"]`).css("fontSize", ($(this).val() / 100) * cw + "px");
    });

    dialog.$wrapper.on("hidden.bs.modal", () => {
        $(document).off("pointermove.cardDesigner pointerup.cardDesigner");
    });
}
