/**
 * This file is part of Shuup.
 *
 * Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
 *
 * This source code is licensed under the Shuup Commerce Inc -
 * SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
 * and the Licensee.
 */

//-- jQuery
var jquery = require("jquery");
window.$ = window.jQuery = jquery;
const select2 = require("select2");
select2($);

const _ = require('lodash');
window._ = _;

const Sortable = require('sortablejs');
window.Sortable = Sortable.default || Sortable;

require('bootstrap');
require("summernote/dist/summernote.js");
require("../../../admin/static_src/base/js/browse-widget.js");
