/**
 * This file is part of Shuup.
 *
 * Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
 *
 * This source code is licensed under the Shuup Commerce Inc -
 * SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
 * and the Licensee.
 */
import { combineReducers } from "redux";
import lines from "./lines";
import productData from "./productData";
import shop from "./shop";
import customer from "./customer";
import customerData from "./customerData";
import customerDetails from "./customerDetails";
import methods from "./methods";
import order from "./order";
import comment from "./comment";
import quickAdd from "./quickAdd";

const childReducer = combineReducers({
    lines,
    productData,
    shop,
    customer,
    customerData,
    customerDetails,
    methods,
    order,
    comment,
    quickAdd
});

export default function (state, action) {
    if (action.type === "_replaceState") { // For debugging purposes.
        return action.payload;
    }
    state = childReducer(state, action);
    return state;
}
