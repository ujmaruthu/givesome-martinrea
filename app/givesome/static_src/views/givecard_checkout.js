// -*- coding: utf-8 -*-
// This file is part of Shuup.
//
// Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
//
// This source code is licensed under the Shuup Commerce Inc -
// SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
// and the Licensee.

import {
  disallowDonation,
  donated,
  finalQty,
  processGivesome,
  processPreSubmit,
  resetDonated,
  setUpCustomInputListeners,
  setUpRadioListeners
} from './checkout.js'
import {enableOpenModalFromAnother} from '../scripts/modal';

var givecardDonation = function() {
  return {
    // Create dynamic elements and listeners
    init: function(kwargs) {
      if (!kwargs['usable_givecards_sum']) {
        $('#givecard-title').hide();
        $('#givecard-checkout').hide();

        // Givecard checkout is not possible, but user has Givecards
        if(kwargs["total_givecards_sum"]){
          $('#checkout-help-text').text("You have Givecard funds, but they can only be used on specific page(s).");
        }
      } else {
        if (kwargs['usable_givecards_sum'] !== kwargs["total_givecards_sum"]) {
          let text = "Some of your Givecard funds can only be used on specific page(s). You can use $" + kwargs['usable_givecards_sum'] + " from your Givecard wallet on this page."
          $('#checkout-help-text').text(text);
        }
      }

      let url = kwargs['url'];

      // TODO: hide givecard checkout when subscribing

      // Disallow donating to specified projects
      if (!kwargs['allowDonations']) {
        disallowDonation($('#fund-project'), kwargs['btnText'])
      } else {
        $('#fund-project').attr("disabled", false)
      }

      let radio = $('input[name="amount-gc"]').parents().filter('div.radio');
      setUpRadioListeners($('#custom-gc'), radio, 'amount');

      // Set up form submission behavior for one-off donations
      let submitBtn = $('#givesome-givecard-submit');
      submitBtn.on('click', (event) => {
        let ok = processPreSubmit(event, submitBtn, 'amount-gc', 'givecard-errors');
        let submitKwargs = {
          'submitBtn': submitBtn,
          'url': url,
          'form': $('#givesome-givecard-donation'),
          'inputName': 'amount-gc',
          'donationType': 'givecard'
        }
        if (ok) processGivesome(submitKwargs);
      });

      setUpCustomInputListeners('-gc');

      // Trigger a thank-you modal when the payment modal is closed, and reset everything.
      $('#fund-dialog').on('hidden.bs.modal', () => {
        // Resets all entered values
        $('#givesome-givecard-donation:checkbox, :radio').prop('checked', false);
        $('#givesome-givecard-donation') > $('#custom').css('display', "none");
        $('#givesome-givecard-donation') > $('input').val('');

        // Open thank-you modal
        if (donated) {
          $("#submit-loader").hide();
          $('#thank-you').modal('toggle');
        }
      });
      $('#thank-you').on('shown.bs.modal', () => {
        if (donated) {
          $('#contribution').text(finalQty);
        }
        if (donated === 'givecard') {
          // Retrieve new wallet data
          $.ajax({
            url: "/wallet/",
            type: "GET",
            dataType: "html",
            success: function(response) {
              $("#givecard-balance-dialog").replaceWith(response)
              enableOpenModalFromAnother()

              // Increase total wallet value on "open wallet" button
              const walletButton = $("#givecard-total-value")
              walletButton.text($("#givecard-wallet-total-value").text())
            },
            error: function() {
              alert("Error retrieving Givecard Wallet data!")
            }
          });
        }
        resetDonated();
      });
    }
  }

}

export default givecardDonation
