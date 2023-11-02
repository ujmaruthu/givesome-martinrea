/**
 * This file is part of Shuup.
 *
 * Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
 *
 * This source code is licensed under the Shuup Commerce Inc -
 * SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
 * and the Licensee.
 */

// adapted from
// https://github.com/jquery/jquery/blob/250a1990baa571de60325ab2c52eabb399c4cf9e/src/offset.js#L76-L116
export default function (elem) {
    if (!elem.getClientRects().length) {
        return null;
    }

    const rect = elem.getBoundingClientRect();

    if (!(rect.width || rect.height)) {
        return null;
    }
    const doc = elem.ownerDocument;
    const win = doc.defaultView || window;
    const docElem = doc.documentElement;

    return {
        top: rect.top + win.pageYOffset - docElem.clientTop,
        left: rect.left + win.pageXOffset - docElem.clientLeft,
        width: rect.width,
        height: rect.height
    };
}
