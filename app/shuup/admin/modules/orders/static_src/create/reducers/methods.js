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
import _ from "lodash";

export default handleActions({
    setShippingMethod: ((state, { payload }) => _.assign(state, { shippingMethod: payload })),
    setShippingMethodChoices: ((state, { payload }) => _.assign(state, { shippingMethodChoices: payload })),
    setPaymentMethod: ((state, { payload }) => _.assign(state, { paymentMethod: payload })),
    setPaymentMethodChoices: ((state, { payload }) => _.assign(state, { paymentMethodChoices: payload }))
}, {
    shippingMethodChoices: [],
    shippingMethod: null,
    paymentMethodChoices: [],
    paymentMethod: null
});
