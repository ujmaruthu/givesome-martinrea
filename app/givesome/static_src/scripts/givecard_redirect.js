// -*- coding: utf-8 -*-
// This file is part of Shuup.
//
// Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
//
// This source code is licensed under the Shuup Commerce Inc -
// SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
// and the Licensee.

$(document).ready(function () {
    // Get redirect url from localStorage
    let next_url = localStorage.getItem("pin_redeem_next_url")

    if (next_url && (location.pathname === "/" || location.pathname === next_url)) {
        if (location.pathname !== next_url){
            // Redirect user to the page defined in the Givecard
            location.href = next_url;
        }
        localStorage.removeItem('pin_redeem_next_url')
    }
});
