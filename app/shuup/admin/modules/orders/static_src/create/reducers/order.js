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

function updateTotals(state, { payload }) {
    const updates = {};
    const { lines } = payload();
    var total = 0;
    _.map(lines, (line) => {
        total += line.total;
    });
    updates.total = +total.toFixed(2);
    return _.assign({}, state, updates);
}

export default handleActions({
    beginCreatingOrder: ((state) => _.assign(state, { creating: true })),
    endCreatingOrder: ((state) => _.assign(state, { creating: false })),
    updateTotals,
    setOrderId: ((state, { payload }) => _.assign(state, { id: payload })),
    setOrderSource: ((state, { payload }) => _.assign(state, { source: payload })),
    clearOrderSourceData: ((state) => _.assign(state, { source: null }))
}, {
    id: null,
    creating: false,
    source: null,
    total: 0
});
