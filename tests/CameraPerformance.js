// issue-20260921-071339-601: measure moving views, where identical-ray caches miss.
// Host timings are diagnostics; the 33 ms budget is calibrated on this dev host.
const scenarios = [
  { label: 'Reported camp view', x: 505.4276289009733, y: 223.47497304164955,
    yaw: 82.92682926829268, pitch: 24.290465631929056 },
  { label: 'Fence and eaves', x: -446.7471751788618, y: -961.2302091713711,
    yaw: 42.92682926829274, pitch: 12 },
];
try {
  for (const scenario of scenarios) {
    await harness.goToScene('Game');
    await harness.stepFrames(3);
    harness.setSceneVariable('Mode', 0);
    const player = harness.getObjects('Player3D')[0];
    harness.setObjectPosition(player.id, scenario.x, scenario.y, 0);
    harness.setSceneVariable('CameraYaw', scenario.yaw);
    harness.setSceneVariable('CameraPitch', scenario.pitch);
    harness.setSceneVariable('CameraDistance', 1250);
    await harness.stepFrames(120);
    let traveled = 0;
    harness.startProfiling();
    for (const key of ['w', 'd', 's', 'a', 'w', 's']) {
      const before = harness.getObjects('Player3D')[0];
      harness.setKeyPressed(key, true);
      await harness.stepFrames(40);
      harness.releaseAllInputs();
      const after = harness.getObjects('Player3D')[0];
      traveled += Math.hypot(after.x - before.x, after.y - before.y);
    }
    const profile = harness.stopProfiling();
    harness.assert(traveled > 100, `${scenario.label}: exercised real movement (${traveled})`);
    harness.assert(!!profile && Number.isFinite(profile.avgStepTimeMs) && profile.avgStepTimeMs < 33,
      `${scenario.label}: average moving frame below 33 ms on the reference host; observed ${profile?.avgStepTimeMs}`);
    const camera = harness.getCameraState('World3D');
    harness.assert(!!camera && Number.isFinite(camera.x + camera.y + camera.z),
      `${scenario.label}: camera remains finite while moving`);
    const fps = harness.getObjects('FPSCounter')[0];
    const width = harness.getGameResolutionWidth();
    harness.assert(!!fps && !fps.hidden && fps.layer === 'Performance' && fps.y === 8 &&
      Math.abs(fps.x - (width - fps.width) / 2) < 1,
      `${scenario.label}: FPS stays visible at the top center`);
  }
} finally { harness.releaseAllInputs(); }
