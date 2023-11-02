// -*- coding: utf-8 -*-
// This file is part of Shuup.
//
// Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
//
// This source code is licensed under the Shuup Commerce Inc -
// SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
// and the Licensee.

$(function() {
    $("#show-more-content").on("click", function() {
        $("#truncated-content").hide();
        $("#full-content").show();
    });
    $("#show-less-content").on("click", function() {
        $("#full-content").hide();
        $("#truncated-content").show();
    });
})
