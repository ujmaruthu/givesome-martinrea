/**
 * This file is part of Shuup.
 *
 * Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
 *
 * This source code is licensed under the Shuup Commerce Inc -
 * SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
 * and the Licensee.
 */
import { handleActions } from "redux-actions";

export default handleActions({
    setShopChoices: ((state, { payload }) => Object.assign({}, state, { choices: payload })),
    setCountries: ((state, { payload }) => Object.assign({}, state, { countries: payload })),
    setShop: ((state, { payload }) => Object.assign({}, state, { selected: payload }))
}, {
    choices: [],
    countries: [],
    selected: null
});
