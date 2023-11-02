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
    retrieveCustomerDetails: _.identity,
    receiveCustomerDetails: (state, { payload }) => {
        return _.assign(state, {
            customerInfo: payload.data.customer_info,
            orderSummary: payload.data.order_summary,
            recentOrders: payload.data.recent_orders
        });
    },
    showCustomerModal: ((state, { payload }) => _.assign(state, { showCustomerModal: payload }))
}, {});
