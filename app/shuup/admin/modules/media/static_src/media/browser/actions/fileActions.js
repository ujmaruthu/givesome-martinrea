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
import * as remote from "../util/remote";

export function promptRenameFile(controller, file) {
    const { id, name } = file;
    const newName = _.trim(prompt(gettext("New file name?"), name) || "");
    if (newName && name !== newName) {
        remote.post({ action: "rename_file", id, name: newName }).then(function (response) {
            remote.handleResponseMessages(response);
            controller.reloadFolderContents();
        });
    }
}

export function promptDeleteFile(controller, file) {
    const { id, name } = file;
    if (confirm(interpolate(gettext("Are you sure you want to delete the file %s?"), [name]))) {
        remote.post({ action: "delete_file", id }).then(function (response) {
            remote.handleResponseMessages(response);
            controller.reloadFolderContents();
        });
    }
}

export function moveFile(controller, fileId, newFolderId) {
    remote.post({ action: "move_file", "file_id": fileId, "folder_id": newFolderId }).then(function (response) {
        remote.handleResponseMessages(response);
        controller.reloadFolderContents();
    });
}
