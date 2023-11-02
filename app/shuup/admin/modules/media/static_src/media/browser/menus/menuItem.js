/**
 * This file is part of Shuup.
 *
 * Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
 *
 * This source code is licensed under the Shuup Commerce Inc -
 * SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
 * and the Licensee.
 */
import _ from "lodash";
import m from "mithril";
import * as menuManager from "../util/menuManager";

export default function item(label, action, attrs = {}) {
    const tagBits = ["li"];
    if (attrs.disabled) {
        action = _.noop;
        tagBits.push("disabled");
        return;
    }
    return m(tagBits.join("."), m("a.dropdown-item", {
        href: "#", onclick: (event) => {
            event.preventDefault();
            action();
            menuManager.close();
        }
    }, label));
}
