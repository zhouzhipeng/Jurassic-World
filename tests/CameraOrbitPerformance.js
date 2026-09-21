// Two full rotations: record both first-use and warmed render costs.
try {
  await harness.goToScene('Game');
  await harness.stepFrames(3);
  harness.setSceneVariable('Mode', 2);
  harness.setObjectPosition(harness.getObjects('Player3D')[0].id,
    171.6472345523082, 1045.290177449477, 0);
  harness.setSceneVariable('CameraDistance', 1250);
  harness.setSceneVariable('CameraPitch', 12.473022912047304);
  await harness.stepFrames(120);
  const start = harness.getObjects('Player3D')[0];
  for (let lap = 0; lap < 2; lap++) {
    harness.startProfiling();
    for (let frame = 0; frame < 180; frame++) {
      harness.setSceneVariable('CameraYaw', (lap * 180 + frame) * 2);
      await harness.stepFrames(1);
    }
    const profile = harness.stopProfiling();
    harness.assert(!!profile && Number.isFinite(profile.avgStepTimeMs),
      `Orbit ${lap + 1}: measured mean=${profile?.avgStepTimeMs}, max=${profile?.maxStepTimeMs} ms`);
    const camera = harness.getCameraState('World3D');
    harness.assert(!!camera && Number.isFinite(camera.x + camera.y + camera.z), 'Orbit camera remains finite');
  }
  const end = harness.getObjects('Player3D')[0];
  harness.assert(Math.hypot(end.x - start.x, end.y - start.y) < 0.01,
    'Performance exercise rotates the camera while the player stays still');
} finally { harness.releaseAllInputs(); }
