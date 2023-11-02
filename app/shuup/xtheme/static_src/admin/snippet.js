/**
 * This file is part of Shuup.
 *
 * Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
 *
 * This source code is licensed under the Shuup Commerce Inc -
 * SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
 * and the Licensee.
 */
function getModeFromSnippetType(type) {
    if (type === "inline_css") {
        return "css";
    } else if (type === "inline_js") {
        return "javascript";
    }
    return "htmlmixed";
}

window.addEventListener("load", () => {
    Array.from(document.getElementsByClassName("xtheme-code-editor-textarea")).forEach(el => {
        const $snippetType = $(el).closest("form").find("[name='snippet_type']");
        function createCodeMirror(mode) {
            window.ShuupCodeMirror.createCodeMirror(el, {
                mode: getModeFromSnippetType(mode)
            });
        }
        $snippetType.change((evt) => {
            createCodeMirror(evt.target.value);
        });

        createCodeMirror($snippetType.val());
    });
});
