// -*- coding: utf-8 -*-
// This file is part of Shuup.
//
// Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
//
// This source code is licensed under the Shuup Commerce Inc -
// SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
// and the Licensee.

$(document).ready(function () {
    if (window.location.href.indexOf("profile") !== -1 ){
        newUrl = "#"
        $("#nav-log-in").attr("href", newUrl);
        $("#nav-log-in").addClass("dropdown-toggle");
    }
    else{
        if (window.dashboard_url){
            newUrl = window.dashboard_url;
            $("#nav-log-in").removeClass("dropdown-toggle");
            $("#nav-log-in").removeAttr("data-toggle"); 
            $("#nav-log-in").removeAttr("aria-expanded"); 
            $("#nav-log-in").attr("href", newUrl);    
        }
    }
});
