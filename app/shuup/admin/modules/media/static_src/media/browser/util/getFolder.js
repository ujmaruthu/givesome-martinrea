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

export default function (folderPath, folderId) {

  var folder = folderPath.find(obj => {
    return obj.id === folderId
  })

  return folder;
}
