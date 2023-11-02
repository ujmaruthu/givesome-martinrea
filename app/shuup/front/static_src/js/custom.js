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
    $(".selectpicker").selectpicker();
});

$(document).ready(function () {
    $(".btn-variation").on("click", function (e) {
        e.preventDefault();
        var level = $(this).data("level");
        $(".btn-variation").each(function (i, elem) {
            if ($(elem).data("level") === level) {
                $(elem).removeClass("btn-active");
            }
        });
        $(this).addClass("btn-active");
        var productId = $(this).data("target-product");
        var variationId = $(this).data("product-id");
        var parentProduct = $(this).data("primary-product");
        if ($("#var_" + productId).length) {
            $("#var_" + productId).val(variationId);
        } else {
            $("#product-variations-" + productId).val(variationId);
        }
        var id = (parentProduct) ? parentProduct : productId;
        window.updatePrice(id);
    });
});
