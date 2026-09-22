// Diagnostic only: alternate modes/distances are not acceptance evidence.
const cases = [
  { label: 'reported view', mode: 0, distance: 1250, flash: 0 },
  { label: 'reported hurt', mode: 0, distance: 1250, flash: 2 },
  { label: 'paused gameplay', mode: 2, distance: 1250, flash: 0 },
  { label: 'short camera queries', mode: 0, distance: 300, flash: 2 },
];
try {
  await harness.goToScene('Game');
  await harness.stepFrames(4);
  harness.setSceneVariable('Invulnerable', 9999);
  harness.setObjectPosition(harness.getObjects('Player3D')[0].id, 4687.91, 545.62, 1440.46);
  harness.setSceneVariable('CameraYaw', 80.97561);
  harness.setSceneVariable('CameraPitch', 12.23651);
  await harness.stepFrames(90);
  for (const c of cases) {
    harness.setSceneVariable('Mode', c.mode);
    harness.setSceneVariable('CameraDistance', c.distance);
    harness.setSceneVariable('HitFlash', c.flash);
    await harness.stepFrames(10);
    harness.startProfiling();
    await harness.stepFrames(60);
    const p = harness.stopProfiling();
    harness.assert(!!p && Number.isFinite(p.avgStepTimeMs), c.label + ': ' + JSON.stringify(p?.sections.slice(0,3)));
  }
} finally { harness.releaseAllInputs(); }
