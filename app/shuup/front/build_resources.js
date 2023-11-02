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

runBuildCommands([
    getParcelBuildCommand({
        cacheDir: "front",
        outputDir: "static/shuup/front/js",
        entryFile: "static_src/js/vendor.js"
    }),
    getParcelBuildCommand({
        cacheDir: "front",
        outputDir: "static/shuup/front/js",
        outputFileName: "scripts",
        entryFile: "static_src/js/index.js"
    }),
    getParcelBuildCommand({
        cacheDir: "front",
        outputDir: "static/shuup/front/css",
        entryFile: "static_src/less/style.css"
    })
]);
