// -*- coding: utf-8 -*-
// This file is part of Shuup.
//
// Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
//
// This source code is licensed under the Shuup Commerce Inc -
// SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
// and the Licensee.

$(window).on("load", function() {
    $(".owl-loading-indicator").hide();

    $(".project-carousel").owlCarousel({
        nav: true,
        dots: true,
        navText: [
            "<i class='fa fa-angle-left' aria-label='Prev'></i>",
            "<i class='fa fa-angle-right' aria-label='Next'></i>"
        ],
        responsiveClass: true,
        rewind: false,
        items: 1,
        responsive: {
            0: { // breakpoint from 0 up
                items: 1,
                margin: 0,
            },
            550: { // breakpoint from 550 up
                items: 2,
                margin: 0,
            },
            992: { // breakpoint from 992 up
                items: 3,
                margin: 20,
            }
        }
    });

    $(".video-carousel").owlCarousel({
        nav: true,
        dots: true,
        navText: [
            "<i class='fa fa-angle-left' aria-label='Prev'></i>",
            "<i class='fa fa-angle-right' aria-label='Next'></i>"
        ],
        responsiveClass: true,
        rewind: false,
        responsive: {
            0: { // breakpoint from 0 up
                items: 1,
                margin: 0,
            },
            640: { // breakpoint from 640 up
                items: 2,
                margin: 0,
            },
            992: { // breakpoint from 992 up
                items: 3,
                margin: 20,
            }
        }
    });

    $(".logo-carousel").owlCarousel({
        nav: false,
        dots: true,
        responsiveClass: true,
        rewind: false,
        margin: 0,
        responsive: {
            0: { // breakpoint from 0 up
                items: 2,
            },
            550: {
                items: 3,
            },
            768: { // breakpoint from 768 up
                items: 4,
            },
        }
    });
});
