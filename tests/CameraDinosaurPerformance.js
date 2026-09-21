// issue-20260921-080220-709: exact reported player and camera setup.
const n = name => Number(harness.getSceneVariable(name)?.value);
try {
  await harness.goToScene('Game');
  await harness.stepFrames(3);
  harness.setSceneVariable('Mode', 2);
  harness.setObjectPosition(harness.getObjects('Player3D')[0].id, 650, 200, 0);
  harness.setSceneVariable('CameraYaw', 187.642276422764);
  harness.setSceneVariable('CameraPitch', 14.6016260162602);
  harness.setSceneVariable('CameraDistance', 1250);
  await harness.stepFrames(120);
  harness.startProfiling();
  await harness.stepFrames(120);
  const blocked = harness.stopProfiling();
  harness.assert(blocked.avgStepTimeMs < 33.3,
    `Reported dinosaur view mean/max: ${blocked.avgStepTimeMs}/${blocked.maxStepTimeMs} ms`);
  const p = harness.getObjects('Player3D')[0], c = harness.getCameraState('World3D');
  const dino = harness.getRuntimeObject('Dinosaur3D');
  const dx = p.x - c.x, dy = p.y - c.y, dz = 190 - c.z;
  const length = Math.hypot(dx, dy, dz);
  const hits = gdjs.evtTools.scene3d.raycastObjects(c.x, c.y, c.z,
    dx / length, dy / length, dz / length, [dino], 0, length - 1, true);
  harness.assert(hits.length === 0, 'Actual animated dinosaur mesh leaves the player head visible');
  harness.startProfiling();
  for (let frame = 0; frame < 180; frame++) {
    harness.setSceneVariable('CameraYaw', 187.642276422764 + frame * 2);
    await harness.stepFrames(1);
  }
  const orbit = harness.stopProfiling();
  const times = orbit.frameTimesMs.slice().sort((a, b) => a - b);
  const p95 = times[Math.floor((times.length - 1) * 0.95)];
  harness.assert(orbit.avgStepTimeMs < 33.3 && p95 < 50,
    `Dinosaur orbit mean/p95/max: ${orbit.avgStepTimeMs}/${p95}/${orbit.maxStepTimeMs} ms`);
  harness.assert(Number.isFinite(n('CameraResolvedDistance')) && n('CameraResolvedDistance') >= 300,
    'Orbit retains finite usable player framing');
} finally { harness.releaseAllInputs(); }
