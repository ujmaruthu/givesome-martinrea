// -*- coding: utf-8 -*-
// This file is part of Shuup.
//
// Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
//
// This source code is licensed under the Shuup Commerce Inc -
// SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
// and the Licensee.


let CardTemplate = class {
  constructor(editUrl, deleteUrl, identifier, translatedTerm) {
    this.editUrl = editUrl;
    this.deleteUrl = deleteUrl;
    this.identifier = identifier;
    this.translatedTerm = translatedTerm;
  }
}

// Turn `card` into the same kind of form used for adding new cards.
function convertToForm(card, cardTemplate, itemId) {
  let form = card.siblings('form').clone();

  // Pre-fill the visible fields with the original values;
  let valueString = card.children().first().text();
  let value = valueString.match(/\d+(\.\d+)?/);
  form.children('.form-group')
      .children('.form-input-group')
      .children('input[name="amount"], input[name="hours"]')
      .val(value[0]);
  // TODO: adjust date formatting if needed.
  let date = valueString.match(/\d{4}-\d{2}-\d{2}/);
  form.children('.form-group').children('.form-input-group')
      .children('input[name*="_on"]')
      .val(date[0]);
  let description = card.children().last().text();
  form.children('.form-group').children('.form-input-group')
      .children('input[name="description"]')
      .val(description);

  // Remember the pre-filled data.
  let formData = form.serializeArray();
  let originalData = {};
  $.each(formData, (index, field) => {
    const [key, val] = Object.entries(field);
    originalData[key[1]] = val[1];
  });

  // Set up event listeners on new buttons.
  form.children('button.cancel-contribution').on('click', function() {
    card.replaceWith(createCard(originalData, cardTemplate));
  })
  form.children('button.edit-contribution').on('click', function(event) {
    let targetUrl = cardTemplate.editUrl.replace(/\d+/, itemId);
    updateRecords(event, form, targetUrl, cardTemplate, updateCard, card);
  });
  form.children('button.delete-contribution').on('click', function(event) {
    let targetUrl = cardTemplate.deleteUrl.replace(/\d+/, itemId);
    updateRecords(event, form, targetUrl, cardTemplate, removeCard, card);
  });

  // Replace original card contents
  card.empty();
  card.append(form);
  form.children('button.submit-contribution').hide();
  form.children('button.delete-contribution').show();
  form.children('button.edit-contribution').show();
  form.show();
}

// Create a new list group item containing the provided off-platform donation information.
function createCard(item, cardTemplate) {
  let fmt_qty = '';
  if (cardTemplate.translatedTerm) {
    fmt_qty = `${item["hours"]} ${cardTemplate.translatedTerm}`;
  } else {
    fmt_qty = `\$ ${item["amount"]}`;
  }
  let child = $('<div></div>').attr('class', 'list-group-item').prop('id', item["pk"]);

  // Create the 'Edit' link
  let edit = $('<span>Edit</span>').attr('class', 'edit')
      .css('float', 'right')
      .css('color', 'blue')
      .css('cursor', 'pointer');
  edit.on('click', function(){
    convertToForm($(this).parent().parent(), cardTemplate, item["pk"]);
  });

  // Put together the thing donated, the date, and the description; and add the 'Edit' link.
  let given = $(`<p>${fmt_qty} - ${item[`${cardTemplate.identifier}_on`]}</p>`);
  given.append(edit);
  child.append(given);
  child.append(`<p>${item["description"]}</p>`)
  return child;
}

// Add a new card.
function appendCard(data, cardTemplate) {
  $(`#${cardTemplate.identifier}`).prepend(createCard(data, cardTemplate));
}

// Redraw the card
function updateCard(data, cardTemplate, card) {
  card.replaceWith(createCard(data, cardTemplate));
}

// Delete the card
function removeCard(data, cardTemplate, card) {
  card.remove();
}

// POST to Givesome to do whatever the user wanted to do.
function updateRecords(event, form, targetUrl, cardTemplate, callback, targetElement) {
  event.preventDefault();
  $.ajax({
    url: targetUrl,
    type: 'POST',
    data: form.serialize(),
    success: function(object) {
      object = $.parseJSON(object);
      if (object.length > 0) object[0].fields["pk"] = object[0].pk;
      callback(object[0].fields, cardTemplate, targetElement);
    }
  });
}

// Fetch off platform records
function loadRecords(url, cardTemplate) {
  $.ajax({
    url: url,
    type: 'GET',
    success: function(objects) {
      objects = $.parseJSON(objects);
      $.each(objects, (index, object) => {
        object.fields["pk"] = object.pk;
        $(`#${cardTemplate.identifier}`).append(createCard(object.fields, cardTemplate));
      });
    }
  });
}

// Correctly format the url types
function formatUrlType(url, divId) {
  return url.replace('type', divId === 'donated' ? 'OffPlatformDonation' : 'VolunteerHours')
}

// Since submission is handled manually, check for required fields first.
function checkSubmission(form) {
  let valid = true
  form.children('div').find('input').each(function() {
    if (!$(this).val() && valid) valid = false;
  });
  return valid;
}

var handleOffPlatform = function() {
  return {
    init: function(kwargs) {
      const term = kwargs['hours'];
      const divId = kwargs['div_id']
      const list = formatUrlType(kwargs['list_url'], divId);
      const create = formatUrlType(kwargs['create_url'], divId);
      const update = formatUrlType(kwargs['update_url'], divId);
      const del = formatUrlType(kwargs['delete_url'], divId);
      
      // Use this template to work with cards.
      let cardTemplate = new CardTemplate(update, del, divId, term);

      // Start off by setting up the Create forms
      const form = $(`#${divId}-form`);
      form.hide();
      form.children('button.delete-contribution').hide();
      form.children('button.edit-contribution').hide()
      form.children('div.form-group').children('div.form-input-group').children('.date').datepicker()

      // Set up card headers to be clickable to show the hidden forms.
      let cardHeader = form.parent().siblings('.card-header');
      cardHeader.css('cursor', 'pointer');
      cardHeader.on('click', function() {
        form.show();
      });
      // Reset buttons should hide their respective forms.
      form.children('button[type="reset"]').on('click', function() {
        form.hide();
      });

      // Submit buttons should be handled via ajax. Set other events as the elements are created.
      form.children('button.submit-contribution').on('click', function(event) {
        let ok = checkSubmission(form);
        if (ok) {
          updateRecords(event, form, create, cardTemplate, appendCard);
          form.children('div.form-group')
              .children('div.form-input-group')
              .children('input')
              .val('');
          form.hide();
        }
      });

      // Render volunteer data and set up event listeners on newly created elements
      loadRecords(list, cardTemplate);
    }
  }
}

export default handleOffPlatform;

//# sourceURL=off_platform.js
