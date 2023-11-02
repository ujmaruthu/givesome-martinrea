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
import responsiveUploadHint from "./responsiveUploadHint";
import { uploadIndicator } from "./images";

export default function (ctrl, folder) {  // eslint-disable-line no-unused-vars
    return m("div.empty-folder", [
        m("div.empty-image",
            m("img", { src: uploadIndicator })
        ),
        m("div.empty-text", responsiveUploadHint)
    ]);
}
