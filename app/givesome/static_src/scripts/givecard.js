// -*- coding: utf-8 -*-
// This file is part of Shuup.
//
// Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
//
// This source code is licensed under the Shuup Commerce Inc -
// SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
// and the Licensee.

import { enableOpenModalFromAnother } from './modal.js';

$(document).ready(function() {
  function cleanCodeInput(code) {
    if (code.length !== 6) {
      return ""
    }
    return code.toUpperCase();
  }

  // Get givecard PIN <input> ID
  const $currentModal = $("#givecard-dialog")
  const $pinInputField = $('#givecard-pin-input');
  const $pinInputButton = $('#givecard-pin-button');
  const $pinInputWarning = $('#givecard-pin-error-text');
  const $redeemSpinner = $('#redeem-spinner');

  function redeem() {
    $redeemSpinner.show();
    let cancelBtn = $('#cancel-redemption');
    let cancelText = cancelBtn.text();
    cancelBtn.text('');

    const code = cleanCodeInput($pinInputField.val())
    if (code) {
      $pinInputWarning.text("")
      $.ajax({
        url: "/redeem/",
        type: "POST",
        dataType: "json",
        data: {
          givecard_code: code,
          csrfmiddlewaretoken: $('#givecard-pin-csrf-token').val()
        },
        success: function(response) {
          $pinInputWarning.text('');  // Clear any warnings
          $currentModal.modal('hide');
          $redeemSpinner.hide();
          // Wait until the old modal is closed
          $currentModal.on('hidden.bs.modal', function() {
            // Display campaign information on modal
            $("#givecard-success-campaign-image").attr("src", response.campaign_image)
            $("#givecard-success-campaign-name").text(response.campaign_name)
            $("#givecard-success-campaign-message").text(response.campaign_message)
            $("#givecard-success-amount").text("$" + response.preferred_currency_balance)
            $("#givecard-success-link").attr("href", response.next_url)
            if (response.is_expiring_soon === true){
              $("#givecard-success-expiry").text(gettext("Heads Up! These funds expire on ") + response.exp_date)
            }
            else{
              $("#givecard-success-expiry").text("") // Clear text
            }
            $("#show-givecard-dialog-btn").hide()
            $("#show-givecard-balance-dialog-btn").removeClass("hidden")

            // Increase total wallet value on "open wallet" button
            const walletButton = $("#givecard-total-value")
            walletButton.text(`$${parseFloat(walletButton.text().substring(1)) + response.balance}`)

            // Add redeemed Givecard to shown expiring Givecards, so a second expiry modal is not shown
            const localStorageKey = "expiring_givecards"

            var shownCodes = localStorage.getItem(localStorageKey)
            if (shownCodes !== null && shownCodes.length){
              localStorage.setItem(localStorageKey, [response.code, shownCodes].join(";"))
            } else {
              localStorage.setItem(localStorageKey, response.code)
            }

            // Save redirect url to localStorage, in case user registers to the website
            if (response.next_url !== "/") {
              localStorage.setItem("pin_redeem_next_url", response.next_url)
            }

            // Retrieve new wallet data
            $.ajax({
              url: "/wallet/",
              type: "GET",
              dataType: "html",
              success: function(response) {
                $("#givecard-balance-dialog").replaceWith(response)

                // "$ Redeem PIN" button functionality gets disabled when its overridden so we need to re-enable it
                enableOpenModalFromAnother()
              },
              error: function() {
                alert("Error retrieving Givecard Wallet data!")
              }
            })

            let success = $("#givecard-success-dialog");
            success.modal('show');
            // Ensure that this doesn't run multiple times and is only bound to this button click event
            $currentModal.off('hidden.bs.modal');
            // Enforce going to donation page
            success.on('hidden.bs.modal', function() {
              if(location.pathname !== response.next_url){
                localStorage.removeItem('pin_redeem_next_url') // User didn't exit the modal unexpectedly, clear
                location.href = response.next_url;
              }
            });
          })
        },
        error: function(data) {
          if (data?.responseJSON?.error) {
            $pinInputWarning.text(data.responseJSON.error);
          } else {
            $pinInputWarning.text(gettext("Unspecified error"));
          }
          $redeemSpinner.hide();
          cancelBtn.text(cancelText);
        }
      });
    } else {
      $pinInputWarning.text(gettext("Invalid code format"))
      $redeemSpinner.hide();
    }

    $currentModal.on('hidden.bs.modal', function() {
      // Clear any warnings
      $pinInputWarning.text("");
      $pinInputField.val("");
      $currentModal.off('hidden.bs.modal');
    })
  }

  // Submit on enter, but don't close modal
  $(window).keydown(function(e) {
    if (e.keyCode === 13) {
      e.preventDefault();
      redeem();
    }
  });

  $pinInputField.submit(function(e) {
    e.preventDefault();
    return false
  });

  $pinInputButton.on('click', function() {
    redeem();
  });
});

//# sourceURL=givecard.js
