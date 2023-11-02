/**
 * This file is part of Shuup.
 *
 * Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
 *
 * This source code is licensed under the Shuup Commerce Inc -
 * SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
 * and the Licensee.
 */
import { setShop, updateLines } from "../actions";
import { selectBox } from "./utils";

export function shopSelectView(store) {
    const { shop } = store.getState();
    return m("div.form-group", [
        m("label.control-label", gettext("Shop")),
        selectBox(shop.selected.id, function () {
            const newShop = _.find(shop.choices, { "id": parseInt(this.value) });
            store.dispatch(setShop(newShop));
            store.dispatch(updateLines());
        }, shop.choices)
    ]);
}
