/**
 * This file is part of Shuup.
 *
 * Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
 *
 * This source code is licensed under the Shuup Commerce Inc -
 * SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
 * and the Licensee.
 */
function isTouchDevice() {
    return ("ontouchstart" in window || navigator.maxTouchPoints);
}

$(function () {
    "use strict";
    $("[data-toggle='popover']").each(function (idx, elem) {
        if ($(elem).data("trigger") !== "manual") {
            $(elem).popover();
        } else if (!isTouchDevice()) {
            $(elem).on("mouseenter", function () {
                $(elem).popover("show");
            });
            $(elem).on("mouseleave", function () {
                $(elem).popover("hide");
            });
        } else {
            // unbind all hover related from manual popovers on touch device
            $(elem).unbind("hover mouseenter mouseleave");
        }
    });
}());
