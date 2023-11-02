/**
 * This file is part of Shuup.
 *
 * Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
 *
 * This source code is licensed under the Shuup Commerce Inc -
 * SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
 * and the Licensee.
 */
window.changeLanguage = function changeLanguage() {
  $.ajax({
    url: "/set-language/",
    method: "POST",
    data: {
      language: $(this).data("value"),
    },
    success: function (data) {
      window.location.reload();
    },
  });
};

$(function () {
  $(".languages li a").click(window.changeLanguage);
});
