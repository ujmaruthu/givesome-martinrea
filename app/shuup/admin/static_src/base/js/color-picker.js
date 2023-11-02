/**
 * This file is part of Shuup.
 *
 * Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
 *
 * This source code is licensed under the Shuup Commerce Inc -
 * SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
 * and the Licensee.
 */

var inputChangeTimeout;
function activateColorPicker(el) {
    $(el).colorpicker({
        format: "hex",
        horizontal: true,
        autoInputFallback: false,
    }).unbind("keyup").on("keyup", function (event) {
        window.clearTimeout(inputChangeTimeout);
        inputChangeTimeout = window.setTimeout(function () {
            $(event.target).trigger("change");
        }, 1000);
    });
}
window.activateColorPicker = activateColorPicker;

$(function () {
    $(".hex-color-picker").each((index, el) => {
        activateColorPicker(el);
    });
});
