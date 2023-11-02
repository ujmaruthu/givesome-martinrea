// -*- coding: utf-8 -*-
// This file is part of Shuup.
//
// Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
//
// This source code is licensed under the Shuup Commerce Inc -
// SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
// and the Licensee.

export let finalQty = '0';
export let donated = '';

// Setter for client scripts
export function resetDonated() {
  donated = '';
}

const alreadyFundedMsg = "Thank you for your generosity! However, another user's donation just met " +
            "the project's funding goals, so your donation did not go through.";

let addPromoterData = function(finalPostData) {
  let type = window.location.search.match(/type=([^&]*)/);
  let id = window.location.search.match(/id=([^&]*)/);
  finalPostData['promoter_type'] = type ? type[1] : null;
  finalPostData['promoter_id'] = id ? id[1] : null;
  return finalPostData
}

let addPromoterDataSerialized = function(serializedString) {
  let type = window.location.search.match(/type=([^&]*)/);
  let id = window.location.search.match(/id=([^&]*)/);
  type = type ? `&${type[0]}` : '';
  id = id ? `&${id[0]}` : '';
  return `${serializedString}${type}${id}`
}

// Disable the funding button. Tell the user why they can't donate.
export function disallowDonation(btn, txt) {
  btn = $('#fund-project');
  btn.text(txt);
  btn.prop('disabled', true);
}

export function displayErrors(msg, errorID, submitBtn) {
  let errorElement = document.getElementById(errorID);
  // Most error messages are pretty user-friendly, but not this one:
  if (msg.toLowerCase().includes("forbidden")) {
    msg = gettext(
        "An error occurred and your donation did not go through. Please refresh the page and try again."
    );
  }
  errorElement.textContent = msg;
  $("#submit-loader").hide();
  if (typeof submitBtn !== "undefined") submitBtn.show(); // Show the submit button again if there was an error so that we can try to submit again
  const $currentModal = $('#fund-dialog')
  $currentModal.on('hidden.bs.modal', function() {
    $currentModal.off('hidden.bs.modal');
    errorElement.textContent=''
  });
}

// Check that it's safe to proceed with the donation
export function processPreSubmit(event, submitBtn, inputName, errorID) {
  event.preventDefault();
  if ($(`input[name=${inputName}]:checked`).length === 0) {
    displayErrors('Please select an amount', errorID, submitBtn);
    return false;
  }
  submitBtn.hide();
  $("#submit-loader").show();
  return true;
}

// Set up form data needed for a Stripe payment
let setUpPayment = function(qty, paymentMethodId, token) {
  let stripeForm = $('#payment-form');

  if (typeof token !== 'undefined') {
    let hiddenInput = document.createElement('input');
    hiddenInput.setAttribute('type', 'hidden');
    hiddenInput.setAttribute('name', 'stripeToken');
    hiddenInput.setAttribute('value', token.id);
    stripeForm.append(hiddenInput);
  }
  let paymentMethodInput = document.createElement('input')
  paymentMethodInput.setAttribute('type', 'hidden');
  paymentMethodInput.setAttribute('name', 'payment_method_id');
  paymentMethodInput.setAttribute('value', paymentMethodId);
  stripeForm.append(paymentMethodInput);

  qty.clone().appendTo(stripeForm);
  let saveCardInfo = $('#save_for_later');
  if (saveCardInfo.prop('checked')) stripeForm.append(saveCardInfo);
  return stripeForm
}

// Set up show/hide functionality for the custom radio inputs.
export function setUpRadioListeners(customContainer, radio, inputName) {
  var expand_element = radio[0]
  var expand_element_label = $(expand_element).find("> label")
  $(radio).each(function(){
    if($(this) !== $(expand_element)){
      $(this).on('click', ()=>{
        customContainer.hide();
      });
    }
  })
  $([expand_element, expand_element_label]).on('click', (e)=>{
    e.preventDefault() // need this or is called for both parent and child
    if(customContainer.is(':visible')) {
      customContainer.hide()
    }
    else {
      customContainer.show()
    }
  });
  $(`input[id*=id_${inputName}]`).each(function() {
    $(this).closest('div.radio').on('click', ()=>{
      var selected_element = $(this);
      var submission_btn = $('#givesome-givecard-submit');
      var curr_donation_value = $(this).val();
      // reset other checkboxes when one is clicked, and make the selected element checked
      $(`*[id*=id_${inputName}]`).each(function(k, v) {
        if ($(this) !== selected_element){
          $(this).prop('checked', false);
          selected_element.prop('checked', true);
          submission_btn.html(`${gettext('Donate')} <b>$${curr_donation_value}</b>`);
        }
      });
    });
  });
}

// Update the custom form input value to match user custom input
// `extraNode` being anything that also needs its text updated.
export function setUpCustomInputListeners(inputSuffix, extraNode) {
  $(document).on('keyup', `#id_custom${inputSuffix}`,() => {
    let custom = $(`#id_custom${inputSuffix}`);
    let submission_btn = $('#givesome-givecard-submit');
    if (typeof extraNode !== "undefined") extraNode.text(`\$${(custom.val() || 0)} `);
    let customRadioChoice = $(`#id_amount${inputSuffix}_3`);
    customRadioChoice.val(custom.val());
    customRadioChoice.prop("checked", true);
    submission_btn.html(`${gettext('Donate')} <b>$${custom.val()}</b>`);
  });
}

// If a user donates from a stale page, explain that the donation didn't go through.
export function showAlreadyFunded(data, errorID) {
  displayErrors(alreadyFundedMsg, errorID);
  disallowDonation($('#fund-project'), data['btnText']);
  disallowDonation($('#givesome-submit'), data['btnText']);
  updatePage(data);
}

// Trigger the thank-you modal and update the page (without refreshing)
export function thankTheDonor(newTotals) {
  $('#fund-dialog').modal('hide');
  updatePage(newTotals);
}

// Update funding state displayed on page without refreshing.
export function updatePage(newTotals) {
  $('#current-amount').text('$' + newTotals['new_current_amt_preferred_currency']);
  $('#current-percentage').text(newTotals['new_current_percent'] + '%');
  if (newTotals.hasOwnProperty('order_id')) {
    let registerUrl = $('#register-url');
    if (registerUrl.length) {
      let newUrl = registerUrl.attr('href').replace(/\d+/, newTotals['order_id']);
      registerUrl.attr('href', newUrl);
    }
  }
  if (newTotals['available'] === "false") disallowDonation($('#fund-project'), newTotals['btnText']);

  // Offer Stripe checkout if the user has no more eligible givecards
  if (!newTotals['givecard_donation_possible']) {
    $('#credit-card').show();
    $('#checkout').show();
    $('#givecard-title').hide();
    $('#givecard-checkout').hide();
  }
}

// The donation form clears after form submit. But since the page doesn't actually refresh, we need
// to be able to find it again without re-rendering the page.
function findToken(form) {
  let paymentForm = $('#payment-form');
  let tokenInput = form.find('input[name="csrfmiddlewaretoken"]');
  if (tokenInput.val() === "") {
    // The form has been submitted once already. Find it where we stored it earlier.
    let token = paymentForm.find('div[id="csrfmiddlewaretoken"]').val()
    tokenInput.val(token);
  } else {
    // Save the token in the payment form (we don't know what `form` is, but they share a token)
    // so it doesn't vanish forever.
    let div = $("<div>").addClass("invisible").prop("id", "csrfmiddlewaretoken").val(tokenInput.val());
    paymentForm.append(div);
  }
  return tokenInput.val();
}

// Givesome donation processing.
export function processGivesome(kwargs) {
  let submitBtn = kwargs['submitBtn'];
  let url = kwargs['url'];
  let givesomeForm = kwargs['form'];
  let donationType = kwargs['donationType']
  let errorID = donationType === 'stripe' ? 'card-errors' : 'givecard-errors';
  let csrfToken = findToken(givesomeForm);

  let finalPostData = {
    'amt': $(`input[name=${kwargs['inputName']}]:checked`).val(),
    'csrfmiddlewaretoken': csrfToken,
  };
  finalPostData = addPromoterData(finalPostData);

  // Only Stripe payments will have a `payment_method_id`.
  let finalForm = givesomeForm;
  if (kwargs.hasOwnProperty('payment_method_id')) {
    let payment_method_id = kwargs['payment_method_id'];
    finalPostData['payment_method_id'] = payment_method_id;

    let qty = givesomeForm.find(`input[name=${kwargs['inputName']}]`);
    let wantReceipt = $("#givesome-stripe-donation").find("input[name='receipt']");
    if (wantReceipt.prop("checked")) {
      finalPostData["receipt"] = wantReceipt.val();
    }
    finalForm = setUpPayment(qty, payment_method_id, kwargs['token']);
    findToken(finalForm);
  }
  $.ajax({
    url: url,
    type: 'POST',
    data: addPromoterDataSerialized(finalForm.serialize()),
    success: function(data) {
      // Check if the project has been fully funded since this donation process started.
      if (data.hasOwnProperty('funded')) {
        showAlreadyFunded(data, errorID)
      } else {
        let available = data['available'];
        let btnText = data['btnText'];

        // Step 4: Let Givesome do some housekeeping.
        finalPostData['order_id'] = data['order_id'];

        // If paying via Stripe and user wants to save CC info, then save CC info.
        if (kwargs.hasOwnProperty('payment_method_id')) {
          if ($('#save_for_later').prop('checked')) {
            finalPostData['save_for_later'] = true;
          }
        }

        $.ajax({
          url: data['finalize_url'],
          type: 'POST',
          data: finalPostData,
          success: function (data) {
            data['available'] = available;
            data['btnText'] = btnText;
            donated = donationType;
            let nodeName = donated === 'givecard' ? 'amount-gc' : 'amount';
            let qtyNode = $(`input[name=${nodeName}]:checked`);
            finalQty = qtyNode.val();
            thankTheDonor(data);
            submitBtn.show();
          },

          // Givesome's attempt to update statuses, etc. after a successful donation failed.
          error: function (data, status, err) {
            let msg = data.hasOwnProperty('responseJSON') ? data.responseJSON['error'] : err
            let warn = 'The donation was submitted successfully, but an error occurred during the final ' +
                'housekeeping details and the donation may not have been fully updated in our system. '
            displayErrors(warn + msg, errorID, submitBtn);
          }
        });
      }
    },

    // Givesome's attempt to create and process the donation failed.
    error: function(data, status, err) {
      let msg = data.hasOwnProperty('responseJSON') ? data.responseJSON['error'] : err
      displayErrors(msg, errorID, submitBtn)
    }
  });
}

//# sourceURL=checkout.js
