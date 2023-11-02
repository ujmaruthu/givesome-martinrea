/**
 * This file is part of Shuup.
 *
 * Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
 *
 * This source code is licensed under the Shuup Commerce Inc -
 * SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
 * and the Licensee.
 */
$(function () {
    "use strict";
    function update() {
        $(".timesince").each(function () {
            const $el = $(this);
            const ts = $el.data("ts");
            if (!ts) {
                return;
            }
            const time = moment(ts);
            if (!time.isValid()) {
                return;
            }
            $el.text(time.fromNow());
        });
    }
    update();
    setInterval(update, 60000);
});
