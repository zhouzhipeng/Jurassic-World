// Full scene, normal gameplay and HUD. This is a strict host frame-cost gate,
// not a claim about wall-clock presentation or different hardware.
const observations = [];
try {
  await harness.goToScene('Game');
  await harness.stepFrames(4);
  harness.setSceneVariable('Mode', 0);
  harness.setSceneVariable('Invulnerable', 9999);
  for (const scenario of [
    { label: 'camp movement', x: 505.43, y: 223.47, yaw: 82.93, pitch: 24.29, orbit: false },
    { label: 'camp orbit', x: 505.43, y: 223.47, yaw: 82.93, pitch: 24.29, orbit: true },
    { label: 'fence movement', x: -446.75, y: -961.23, yaw: 42.93, pitch: 12, orbit: false },
    { label: 'mountain orbit', x: 1700, y: -4100, yaw: 180, pitch: 24, orbit: true },
  ]) {
    harness.setObjectPosition(harness.getObjects('Player3D')[0].id, scenario.x, scenario.y, 0);
    harness.setSceneVariable('CameraYaw', scenario.yaw);
    harness.setSceneVariable('CameraPitch', scenario.pitch);
    await harness.stepFrames(90);
    harness.startProfiling();
    for (let frame = 0; frame < 180; frame++) {
      if (scenario.orbit) harness.setSceneVariable('CameraYaw', scenario.yaw + frame * 2);
      else if (frame % 30 === 0) {
        harness.releaseAllInputs();
        harness.setKeyPressed(['w', 'd', 's', 'a', 'w', 's'][frame / 30], true);
      }
      await harness.stepFrames(1);
    }
    harness.releaseAllInputs();
    const p = harness.stopProfiling();
    harness.assert(!!p && Number.isFinite(p.avgStepTimeMs), scenario.label + ': measured frame cost');
    const times = p.frameTimesMs.slice().sort((a, b) => a - b);
    const p95 = times[Math.floor((times.length - 1) * .95)];
    observations.push({ label: scenario.label, mean: p.avgStepTimeMs, p95, max: p.maxStepTimeMs });
  }
  harness.assert(observations.every(o => o.mean <= 1000 / 60 && o.p95 <= 1000 / 60 && o.max <= 1000 / 30),
    '60 FPS host budget (mean/p95 <= 16.67 ms, max <= 33.33 ms): ' + JSON.stringify(observations));
} finally { harness.releaseAllInputs(); }
