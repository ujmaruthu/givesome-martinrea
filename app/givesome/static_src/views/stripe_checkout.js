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
  displayErrors,
  processGivesome,
  processPreSubmit,
  setUpCustomInputListeners,
  setUpRadioListeners
} from './checkout.js'

// Create a card UI element and a Stripe instance.
let createElements = function(pubKey) {
  let stripe = Stripe(pubKey);
  let elements = stripe.elements();

  let style = {
    base: {
      color: '#32325d',
      fontFamily: '"Open Sans", sans-serif',
      fontSmoothing: 'antialiased',
      fontSize: '16px',
      '::placeholder': {
        color: '#aab7c4'
      }
    },
    invalid: {
      color: '#fa755a',
      iconColor: '#fa755a'
    }
  };

  let card = elements.create('card', {style: style});

  return {
    'stripe': stripe,
    'card': card
  }
}

// Handle real-time validation errors from the card Element.
let cardErrorHandler = function(event) {
  let displayError = document.getElementById('card-errors');
  if (event.error) {
    displayError.textContent = event.error.message;
  } else {
    displayError.textContent = '';
  }
}

// Stripe payment processing
let stripeSubmit = function (url, stripe, card, submitBtn) {

  // Step 1: initiate payment by asking for a Stripe token
  stripe.createToken(card).then(function(result) {
    if (result.error) {
      // Inform the user if there was an error in the CC number input.
      displayErrors(result.error.message, 'card-errors', submitBtn);
    } else {
      let token = result.token;

      // Step 2: get a PaymentMethod.
      let method = stripe.createPaymentMethod({
        type: 'card',
        card: card
      });
      method.then(function(result){
        if (result.paymentMethod) {

          // Stripe conversation as complete as it can be for now, so hand it over to Givesome.
          let submitKwargs = {
            'submitBtn': submitBtn,
            'url': url,
            'form': $('#givesome-stripe-donation'),
            'payment_method_id': result.paymentMethod.id,
            'token': token,
            'inputName': 'amount',
            'donationType': 'stripe'
          }
          // donated = processGivesome(submitKwargs);
          processGivesome(submitKwargs);
        } else {

          // Stripe's attempt to process a PaymentMethod failed
          displayErrors(result.error.message, 'card-errors', submitBtn);
        }
      }); // End paymentMethod call
    }
  }); // End token call
}

var stripeDonation = function(){

  return {
    // Create dynamic elements and listeners
    init: function (kwargs) {
      // If the user can donate via Givecard, stripe donations are not allowed right now (but may be
      // needed later). Hide everything.
      if (kwargs['usable_givecards_sum']) {
        $('#credit-card').hide();
        $('#checkout').hide();
      }

      let elements = createElements(kwargs['public_key'])
      let stripe = elements['stripe'];
      let card = elements['card'];
      let showCreditCard = kwargs['showCreditCard']
      let url = kwargs['url'];

      // Add the credit card inputs
      card.mount('#stripe-checkout');
      card.on('change', (event) => {
        cardErrorHandler(event);
      })
      let cardContainer = $('#stripe-container');
      cardContainer.hide();

      // Disallow donating to specified projects
      if (!kwargs['allowDonations']) {
        disallowDonation($('#fund-project'), kwargs['btnText'])
      } else {
        $('#fund-project').attr("disabled", false)
      }

      // Set up form submission behavior for one-off donations
      let submitBtn = $('#givesome-submit');
      let saveCardInfo = $('#save-card');
      submitBtn.on('click', (event) => {
        let ok = processPreSubmit(event, submitBtn, 'amount', 'card-errors');
        if (ok) stripeSubmit(url, stripe, card, submitBtn, kwargs['paymentMethodId']);
      });
      saveCardInfo.hide();
      submitBtn.hide();

      // Set up form submission behavior for donating with saved card information.
      let savedPaymentBtn = $('#saved-card-submit');
      savedPaymentBtn.on('click', (event) => {
        submitBtn = savedPaymentBtn;
        let ok = processPreSubmit(event, submitBtn, 'amount', 'card-errors');
        let submitKwargs = {
            'submitBtn': submitBtn,
            'url': url,
            'form': $('#givesome-stripe-donation'),
            'payment_method_id': kwargs['paymentMethodId'],
            'inputName': 'amount',
            'donationType': 'stripe'
          }
        if (ok) processGivesome(submitKwargs);
      });

      // User wants to enter card details.
      showCreditCard.on('click', () => {
        cardContainer.show();
        submitBtn.show();
        saveCardInfo.show();
        showCreditCard.hide();
        // Remove anything directly related to saved payment methods, if applicable
        savedPaymentBtn.hide();
        kwargs['paymentMethodId'] = '';
        card.focus();
      });

      // The user wants (or doesn't want) to enter a custom amount.
      let radio = $('input[name="amount"]').parents().filter('div.radio');
      setUpRadioListeners($('#custom'), radio, 'amount');

      // If there is a pay-with-saved-card method, dynamically show user how much will be donated
      radio.on('change', () => {
        let paymentAmount = $(('input[name="amount"]:checked')).val()
        $('#dynamic-amt').text('$' + (paymentAmount || 0) + ' ');
      });
      setUpCustomInputListeners('', $('#dynamic-amt'));
      // Note: givecard_checkout.js sets up the event listeners for the Thank You modal.
    }
  }
}

export default stripeDonation
