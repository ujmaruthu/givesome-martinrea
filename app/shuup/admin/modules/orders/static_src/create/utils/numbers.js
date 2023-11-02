/**
 * This file is part of Shuup.
 *
 * Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
 *
 * This source code is licensed under the Shuup Commerce Inc -
 * SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
 * and the Licensee.
 */
function isNumeric(n) {
    return !isNaN(parseFloat(n)) && isFinite(n);
}

function ensureNumericValue(value, defaultValue = 0, asInteger = false) {
    if (!isNumeric(value)) {
        return defaultValue || 0;
    }
    if (Number.isInteger(value) || asInteger) {
        return parseInt(value, 10);
    }
    return parseFloat(value);
}

export default ensureNumericValue;
