// -*- coding: utf-8 -*-
// This file is part of Shuup.
//
// Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
//
// This source code is licensed under the Shuup Commerce Inc -
// SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
// and the Licensee.

export function enableOpenModalFromAnother(){
  $('.open-modal-from-another').on('click', function() {
    // Hide the currently open modal
    var currentModal = $(this).closest('.modal');
    currentModal.modal('hide');

    // Get the ID for the modal to be shown
    var targetModal = $(this).data('target');

    // Wait until the old modal is closed
    currentModal.on('hidden.bs.modal', function() {
      // Show the new modal
      $(targetModal).modal('show');

      // Ensure that this doesn't run multiple times and is only bound to this button click event
      currentModal.off('hidden.bs.modal');
    });
  });
}

$(document).ready(function() {
  // Get givecard PIN <input> ID
  const $pinInput = $('#givecard-pin-input');

  if ($pinInput) {
    // Wait until modal is shown
    $('#givecard-dialog').on('shown.bs.modal', function() {
      // Focus on the givecard input
      $pinInput.focus();
    });
  }

  enableOpenModalFromAnother()
});

