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
    $("[data-toggle=\"tooltip\"]").tooltip({
        delay: { "show": 750, "hide": 100 }
    });
    $("#dropdownMenu").tooltip({
        delay: { "show": 750, "hide": 100 }
    });
}());
