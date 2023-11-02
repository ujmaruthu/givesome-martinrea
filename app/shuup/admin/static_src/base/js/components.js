/**
 * This file is part of Shuup.
 *
 * Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
 *
 * This source code is licensed under the Shuup Commerce Inc -
 * SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
 * and the Licensee.
 */
const ScrollToTopButton = {
    controller() {
        const ctrl = {
            visible: m.prop(false)
        };
        $(window).on("scroll", () => {
            const scrolled = (window.scrollY > 50);
            const changed = (ctrl.visible() !== scrolled);
            if (changed) {
                ctrl.visible(scrolled);
                if (scrolled) {
                    $("body").addClass("scrolled");
                } else {
                    $("body").removeClass("scrolled");
                }
                m.redraw();
            }
        });
        return ctrl;
    },
    view(ctrl) {
        if (!ctrl.visible()) {
            return m(".");
        }
        return (
            m(".scroll-to-top-button", {
                onclick(e) {
                    e.preventDefault();
                    const body = $("html, body");
                    body.stop().animate({ scrollTop: 0 }, 200, "swing");
                }
            }, m("i.fa.fa-chevron-up"))
        );
    }
};

(() => {
    if (document.getElementById("scroll-to-top")) {
        m.mount(document.getElementById("scroll-to-top"), ScrollToTopButton);
    }
})();
