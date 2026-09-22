// Diagnostic isolation only. Alternate UI modes are not 60 FPS acceptance.
try {
  await harness.goToScene('Game');
  await harness.stepFrames(3);
  harness.setSceneVariable('Mode', 0);
  harness.setSceneVariable('Invulnerable', 9999);
  for (const touch of [1, 0]) {
    harness.setSceneVariable('TouchMode', touch);
    await harness.stepFrames(30);
    harness.startProfiling();
    for (const key of ['w', 'd', 's', 'a']) {
      harness.setKeyPressed(key, true);
      await harness.stepFrames(30);
      harness.releaseAllInputs();
    }
    const p = harness.stopProfiling();
    harness.assert(!!p && Number.isFinite(p.avgStepTimeMs),
      `UI mode ${touch}: mean=${p?.avgStepTimeMs} ms`);
  }
} finally { harness.releaseAllInputs(); }
