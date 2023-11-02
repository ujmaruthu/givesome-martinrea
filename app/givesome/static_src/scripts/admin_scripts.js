// -*- coding: utf-8 -*-
// This file is part of Shuup.
//
// Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
//
// This source code is licensed under the Shuup Commerce Inc -
// SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
// and the Licensee.

function _togglePromote(event, productId, chooserId, chooserType, url) {
    event.preventDefault();
    event.stopPropagation();
    $.ajax({
        url: url,
        type: "POST",
        dataType: "json",
        data: {
            productId,
            chooserId,
            csrfmiddlewaretoken: window.ShuupAdminConfig.csrf
        },
        success: function(response) {
            const onPromoteToggleButton = $(`#toggle-${chooserType}-promote-${productId}`);
            if (onPromoteToggleButton.length > 0) {
                if (response.is_promoting) {
                    onPromoteToggleButton
                        .addClass("btn-danger")
                        .removeClass("btn-success")
                        .text(gettext("Stop promoting this project"));

                    window.Messages.enqueue({
                        tags: "success",
                        text: gettext("Project is now being promoted!")
                    });
                } else {
                    onPromoteToggleButton
                        .addClass("btn-success")
                        .removeClass("btn-danger")
                        .text(gettext("Start promoting this project"));

                    window.Messages.enqueue({
                        tags: "success",
                        text: gettext("Project removed from being promoted!")
                    });
                }
            }
        },
        error: function() {
            window.Messages.enqueue({
                tags: "error",
                text: gettext("An error has occurred while promoting project, please try again.")
            });
        }
    });
}

function toggleOfficePromote(event, productId, officeId) {
    _togglePromote(event, productId, officeId, "office", "/admin/multivendor/office_promote/toggle-promote/");
}

function toggleVendorPromote(event, productId, vendorId) {
    _togglePromote(event, productId, vendorId, "vendor", "/admin/multivendor/vendor_promote/toggle-promote/")
}


function _setPrimary(event, productId, chooserId, chooserType, url) {
    event.preventDefault();
    event.stopPropagation();
    $.ajax({
        url: url,
        type: "POST",
        dataType: "json",
        data: {
            productId,
            chooserId,
            csrfmiddlewaretoken: window.ShuupAdminConfig.csrf
        },
        success: function(response) {
            const setPrimaryButton = $(`#set-${chooserType}-primary-${productId}`);
            if (setPrimaryButton.length > 0) {
                let chooser = chooserType[0].toUpperCase() + chooserType.slice(1, chooserType.length);

                if (response.is_primary) {
                    setPrimaryButton
                        .addClass("btn-danger")
                        .removeClass("btn-success")
                        .text(gettext("Remove as primary project"));

                    window.Messages.enqueue({
                        tags: "success",
                        text: gettext(`Project set as ${chooser}'s primary!`)
                    });

                    // Mark all other buttons as non-primary
                    $(`.set-${chooserType}-primary-btn`).each(function() {
                        if ($(this).attr('id') !== setPrimaryButton.attr('id')) {
                            $(this).addClass("btn-success")
                                .removeClass("btn-danger")
                                .text(gettext("Set as primary project"));
                        }
                    })
                } else {
                    setPrimaryButton
                        .addClass("btn-success")
                        .removeClass("btn-danger")
                        .text(gettext("Set as primary project"));

                    window.Messages.enqueue({
                        tags: "success",
                        text: gettext(`Project is no longer ${chooser}'s primary!`)
                    });
                }
            }
        },
        error: function() {
            window.Messages.enqueue({
                tags: "error",
                text: gettext("An error has occurred while setting project as primary, please try again.")
            });
        }
    });
}

function setOfficePrimary(event, productId, officeId) {
    _setPrimary(event, productId, officeId, "office", "/admin/multivendor/office_promote/set-primary/");
}

function setVendorPrimary(event, productId, vendorId) {
    _setPrimary(event, productId, vendorId, "vendor", "/admin/multivendor/vendor_promote/set-primary/")
}

function orderPromotedProjects(event, productId, promoterId, vendorKind) {
    $.ajax({
        url: `/admin/multivendor/vendor_promote/set-order/${vendorKind}/${promoterId}/${productId}/`,
        type: "POST",
        dataType: "json",
        data: {
            csrfmiddlewaretoken: window.ShuupAdminConfig.csrf,
            vendor_id: promoterId,
            shop_product_id: productId,
            position: event.target.value,
        },
        success: function () {
            window.Messages.enqueue({
                tags: "success",
                text: gettext(`Project re-ordered!`)
            });
        },
        error: function () {
            window.Messages.enqueue({
                tags: "error",
                text: gettext("An error has occurred while setting the project's order. Please try again.")
            });
        }
    });
}


function generateGivecards(batchId) {
    $.ajax({
        url: "/admin/givecard_batch/generate/",
        type: "POST",
        dataType: "json",
        data: {
            batchId,
            csrfmiddlewaretoken: window.ShuupAdminConfig.csrf
        },
        success: function(response) {
            const generateButton = $(".givecard_toolbar_button");
            if (generateButton.length > 0) {
                // Convert `Generate` button to `View Givecards` button
                generateButton.contents().last().replaceWith(gettext('View Givecards'))
                generateButton.attr('href', `/admin/givecard_batch/${batchId}/givecards`)
                generateButton.attr('onclick', "").unbind("click")
                window.Messages.enqueue({
                    tags: "success",
                    text: gettext("Givecards successfully generated!")
                });
            }
        },
        error: function() {
            const generateButton = $(".givecard_toolbar_button");
            if (generateButton.length > 0) {
                generateButton.addClass("btn-danger").removeClass("btn-inverse")
            }
            window.Messages.enqueue({
                tags: "error",
                text: gettext("Error generating givecards!")
            });
        }
    });
}


window.toggleOfficePromote = toggleOfficePromote;
window.toggleVendorPromote = toggleVendorPromote;
window.setOfficePrimary = setOfficePrimary;
window.generateGivecards = generateGivecards;
window.setVendorPrimary = setVendorPrimary;
window.orderPromotedProjects = orderPromotedProjects;
