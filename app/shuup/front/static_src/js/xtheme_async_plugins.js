/**
 * This file is part of Shuup.
 *
 * Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
 *
 * This source code is licensed under the Shuup Commerce Inc -
 * SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
 * and the Licensee.
 */

window.SHUUP_FRONT_ASYNC_PRODUCT_CAROUSEL_CONFIG = {
    0: {
        items: 1,
        slideBy: 1
    },
    540: {
        items: 2,
        slideBy: 1
    },
    768: {
        items: 3,
        slideBy: 2
    },
    992: {
        items: 4,
        slideBy: 2
    },
    1200: {
        items: 5,
        slideBy: 3
    }
}

$(document).ready(function () {
    $('.async-xtheme-product-carousel-plugin').each(function (index, value) {
        const url = $(this).data("url");
        if (url) {
            $(this).find(
                '.ajax-content'
            ).html(
                '<div class="text-primary text-center spinner"><i class="fa fa-3x fa-spin fa-spinner"></i></div>'
            ).show();

            const that = $(this);
            $.ajax({
                url,
                method: "GET",
                success: function (data) {
                    that.find('.ajax-content').html(data).owlCarousel({
                        margin: 20,
                        nav: true,
                        navText: [
                            "<i class='fa fa-angle-left'></i>",
                            "<i class='fa fa-angle-right'></i>"
                        ],
                        responsiveClass: true,
                        responsive: window.SHUUP_FRONT_ASYNC_PRODUCT_CAROUSEL_CONFIG
                    });
                },
                error: function (error) {
                    that.find('.ajax-content').html("")
                }
            });
        }
    });
});
