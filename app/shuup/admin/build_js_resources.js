/**
 * This file is part of Shuup.
 *
 * Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
 *
 * This source code is licensed under the Shuup Commerce Inc -
 * SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
 * and the Licensee.
 */
const { getParcelBuildCommand, runBuildCommands } = require("shuup-static-build-tools");

const srcFiles = [
  { entry: "static_src/base/js/base.js" },
  { entry: "static_src/picotable/picotable.js" },
  { entry: "static_src/vendor/vendor.js" }
];

runBuildCommands(
  srcFiles.map(file => {
    return getParcelBuildCommand({
      cacheDir: "admin",
      entryFile: file.entry,
      outputFileName: (file.name !== 'undefined') ? file.name : null,
      outputDir: (file.entry.includes('.js')) ? "static/shuup_admin/js" : "static/shuup_admin/css"
    })
  })
);
