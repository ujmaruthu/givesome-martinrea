/**
 * This file is part of Shuup.
 *
 * Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
 *
 * This source code is licensed under the Shuup Commerce Inc -
 * SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
 * and the Licensee.
 */
import { compose, createStore, applyMiddleware } from "redux";
import { autoRehydrate } from "redux-persist";
import reducer from "./reducers";

const thunk = function ({ dispatch, getState }) {
    // h/t redux-thunk :)
    return next => action =>
        typeof action === "function" ?
            action(dispatch, getState) :
            next(action);
};

const createLoggedStore = compose(autoRehydrate(), applyMiddleware(thunk))(createStore);
const store = createLoggedStore(reducer);

export default store;
