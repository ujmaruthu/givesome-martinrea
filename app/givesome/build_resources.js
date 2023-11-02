const { getParcelBuildCommand, runBuildCommands } = require("shuup-static-build-tools");

runBuildCommands([
    getParcelBuildCommand({
        cacheDir: "givesome",
        outputDir: "static/givesome",
        outputFileName: "givesome",
        entryFile: "static_src/index.js"
    }),
    getParcelBuildCommand({
        cacheDir: "givesome",
        outputDir: "static/givesome",
        outputFileName: "admin_scripts",
        entryFile: "static_src/scripts/admin_scripts.js"
    }),
]);
