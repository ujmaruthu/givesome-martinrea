const { getParcelBuildCommand, runBuildCommands } = require("shuup-static-build-tools");

runBuildCommands([
    getParcelBuildCommand({
        cacheDir: "givesome",
        outputDir: "static/givesome_admin",
        outputFileName: "givesome_admin",
        entryFile: "static_src/index.js"
    }),
]);
