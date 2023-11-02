/**
 * This file is part of Shuup.
 *
 * Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
 *
 * This source code is licensed under the Shuup Commerce Inc -
 * SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
 * and the Licensee.
 */
import m from "mithril";
import getPickId from "../util/getPickId";

export default function (file, tag = "a", content = file.name) {
    const attrs = { href: file.url, target: "_blank" };
    const pickId = getPickId();
    if (pickId) {
        attrs.onclick = function (event) {
            window.opener.postMessage({
                "pick": {
                    "id": pickId,
                    "object": {
                        "id": file.id,
                        "text": file.name,
                        "url": file.url,
                        "thumbnail": file.thumbnail
                    }
                }
            }, "*");
            event.preventDefault();
            return false;
        };
    }
    return m(tag, attrs, content);
}
