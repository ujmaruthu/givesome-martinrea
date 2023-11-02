/**
 * This file is part of Shuup.
 *
 * Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
 *
 * This source code is licensed under the Shuup Commerce Inc -
 * SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
 * and the Licensee.
 */
/* eslint-disable no-bitwise */
import menuItem from "./menuItem";
import * as folderActions from "../actions/folderActions";

export default function (controller) {
    return function () {
        const isRoot = (0 | controller.currentFolderId()) === 0;
        return [
            menuItem(gettext("New folder"), () => {
                folderActions.promptCreateFolderHere(controller);
            }, { disabled: controller.isMenuDisabled("folder-new") }),
            menuItem(gettext("Rename folder"), () => {
                folderActions.promptRenameCurrentFolder(controller);
            }, { disabled: isRoot || controller.isMenuDisabled("folder-rename") }),
            menuItem(gettext("Delete folder"), () => {
                folderActions.promptDeleteCurrentFolder(controller);
            }, { disabled: isRoot || controller.isMenuDisabled("folder-delete") }),
            menuItem(gettext("Edit folder access"), () => {
                folderActions.editAccessCurrentFolder(controller);
            }, { disabled: isRoot || controller.isMenuDisabled("folder-edit") })
        ]; ``
    };
}
