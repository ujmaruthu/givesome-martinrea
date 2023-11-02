/**
 * This file is part of Shuup.
 *
 * Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
 *
 * This source code is licensed under the Shuup Commerce Inc -
 * SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
 * and the Licensee.
 */
import menuItem from "./menuItem";
import * as fileActions from "../actions/fileActions";

export default function (controller, file) {
    return function () {
        return [
            menuItem(gettext("Rename file"), () => {
                fileActions.promptRenameFile(controller, file);
            }, { disabled: controller.isFileMenuDisabled("rename-file", file) }),
            menuItem(gettext("Delete file"), () => {
                fileActions.promptDeleteFile(controller, file);
            }, { disabled: controller.isFileMenuDisabled("delete-file", file) })
        ];
    };
}
