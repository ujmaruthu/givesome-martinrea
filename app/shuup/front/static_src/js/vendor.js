/**
 * This file is part of Shuup.
 *
 * Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
 *
 * This source code is licensed under the Shuup Commerce Inc -
 * SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
 * and the Licensee.
 */
const $ = require("jquery");
window.$ = window.jQuery = $;

require("bootstrap");
require("bootstrap-select/dist/js/bootstrap-select.js");

$.fn.selectpicker.Constructor.BootstrapVersion = '3';
$.fn.selectpicker.Constructor.DEFAULTS["noneSelectedText"] = gettext('Nothing selected');
$.fn.selectpicker.Constructor.DEFAULTS["noneResultsText"] = gettext('No results matched {0}');
$.fn.selectpicker.Constructor.DEFAULTS["selectAllText"] = gettext('Select All');
$.fn.selectpicker.Constructor.DEFAULTS["deselectAllText"] = gettext('Deselect All');

require("jquery.easing");
require("owl.carousel");
const select2 = require("select2");
select2(window.$);
require("simplelightbox");
window.Dropzone = require('dropzone');
Dropzone.autoDiscover = false;
