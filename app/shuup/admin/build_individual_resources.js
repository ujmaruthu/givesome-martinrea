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
  { entry: "static_src/contact_group/edit-members.js", name: "contact-group" },
  { entry: "static_src/dashboard/js/dashboard.js" },
  { entry: "modules/media/static_src/media/browser/Browser.js", name: "media-browser" },
  { entry: "modules/orders/static_src/create/index.js", name: "order-creator" },
  { entry: "static_src/product/edit_media.js", name: "product" },
  { entry: "static_src/wizard/js/wizard.js" },
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
