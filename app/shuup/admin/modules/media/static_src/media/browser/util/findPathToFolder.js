/**
 * This file is part of Shuup.
 *
 * Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
 *
 * This source code is licensed under the Shuup Commerce Inc -
 * SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
 * and the Licensee.
 */
/* eslint-disable no-shadow,eqeqeq */
import _ from "lodash";

export default function (rootFolder, folderId) {
    var pathToFolder = null;

    function walk(folder, folderPath) {
        if (folder.id == folderId) {
            pathToFolder = folderPath.concat([folder]);
            return;
        }
        folderPath = [].concat(folderPath).concat([folder]);
        _.each(folder.children, function (folder) {
            if (!pathToFolder) {
                walk(folder, folderPath);
            }
        });
    }

    walk(rootFolder, []);
    return pathToFolder || [];
}
