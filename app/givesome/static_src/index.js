// -*- coding: utf-8 -*-
// This file is part of Shuup.
//
// Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
//
// This source code is licensed under the Shuup Commerce Inc -
// SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
// and the Licensee.
import moment from 'moment-timezone';

import './styles/index.less';
import './scripts/index';
import stripeDonation from './views/stripe_checkout.js';
import givecardDonation from './views/givecard_checkout.js';
import handleOffPlatform from './views/off_platform_records.js';

window.moment = moment;
window.stripeDonation = stripeDonation;
window.givecardDonation = givecardDonation;
window.handleOffPlatform = handleOffPlatform;
