// -*- coding: utf-8 -*-
// This file is part of Shuup.
//
// Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
//
// This source code is licensed under the Shuup Commerce Inc -
// SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
// and the Licensee.

function animateNumber(obj, start, end, duration) {
  let startTimestamp = null;

  const step = (timestamp) => {
    if (!startTimestamp) startTimestamp = timestamp;

    const progress = Math.min((timestamp - startTimestamp) / duration, 1);
    obj.innerHTML = Math.floor(progress * (end - start) + start);

    if (progress < 1) {
      window.requestAnimationFrame(step);
    }
  };

  window.requestAnimationFrame(step);
}

document.addEventListener("DOMContentLoaded", () => {
  const livesImpactedElem = document.getElementById("profile-lives-impacted");

  if (livesImpactedElem) {
    const livesImpactedAmount = livesImpactedElem.dataset.value;

    let livesImpactedAnimDuration = 3000;
    if (livesImpactedAmount < 5) {
      livesImpactedAnimDuration = 1000;
    }

    animateNumber(livesImpactedElem, 0, livesImpactedAmount, livesImpactedAnimDuration);
  }

  const projectsFundedElem = document.getElementById("profile-projects-funded");

  if (projectsFundedElem) {
    const projectsFundedAmount = projectsFundedElem.dataset.value;

    let projectsFundedAnimDuration = 3000;
    if (projectsFundedAmount < 5) {
      projectsFundedAnimDuration = 1000;
    }

    animateNumber(projectsFundedElem, 0, projectsFundedAmount, projectsFundedAnimDuration);
  }
});
