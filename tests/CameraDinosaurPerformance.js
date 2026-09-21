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
  harness.startProfiling();
  for (let frame = 0; frame < 180; frame++) {
    harness.setSceneVariable('CameraYaw', 547.642276422764 + frame * 2);
    await harness.stepFrames(1);
  }
  const warm = harness.stopProfiling();
  harness.assert(warm.avgStepTimeMs < 33.3 && warm.maxStepTimeMs < 100,
    `Warmed dinosaur orbit mean/max: ${warm.avgStepTimeMs}/${warm.maxStepTimeMs} ms`);

  // Isolate each species and observe real mesh visibility, independent of the
  // camera's approximation. Turns, elevation, hiding and movement invalidate it.
  const species = ['Dinosaur3D', 'Triceratops', 'Stegosaur', 'Raptor', 'Tyrannosaur'];
  for (const name of ['Island3D', 'BerryBush', 'FiberFern', 'WoodSapling', 'StoneDeposit',
    'MetalDeposit', 'SpringWater', 'CampHearth', 'CampForge', ...species]) {
    for (const object of harness.getObjects(name)) harness.getRuntimeObject(object.id).hide(true);
  }
  harness.setObjectPosition(p.id, 0, 0, 0);
  harness.setSceneVariable('CameraYaw', 0);
  harness.setSceneVariable('CameraPitch', 12);
  const headIsVisible = actor => {
    const view = harness.getCameraState('World3D');
    const length = Math.hypot(view.x, view.y, view.z - 190);
    return gdjs.evtTools.scene3d.raycastObjects(view.x, view.y, view.z,
      -view.x / length, -view.y / length, (190 - view.z) / length,
      [actor], 0, length - 1, true).length === 0;
  };
  for (const name of species) {
    const actor = harness.getRuntimeObject(name);
    actor.hide(false);
    harness.setObjectPosition(actor.getUniqueId(), 0, 650, 0);
    actor.setAngle(0);
    await harness.stepFrames(240);
    harness.assert(headIsVisible(actor), `${name}: camera clears actual model`);
    harness.assert(n('CameraResolvedPitch') > 12.1 || n('CameraResolvedDistance') < 1200,
      `${name}: foreground body still triggers camera avoidance`);
    actor.setAngle(90);
    harness.setObjectPosition(actor.getUniqueId(), 0, 650, 150);
    await harness.stepFrames(240);
    harness.assert(headIsVisible(actor), `${name}: turned and elevated model remains clear`);
    harness.setObjectPosition(actor.getUniqueId(), 1800, 650, 150);
    await harness.stepFrames(240);
    harness.assert(n('CameraResolvedDistance') > 1240 && n('CameraResolvedPitch') < 13,
      `${name}: moving out of the corridor restores requested framing`);
    actor.hide(true);
    harness.setObjectPosition(actor.getUniqueId(), 0, 650, 0);
    await harness.stepFrames(1);
    harness.assert(n('CameraSafeDistance') === 1250, `${name}: hidden body does not block`);
  }
  // The player's own mount must not become a camera blocker.
  harness.setObjectPosition(dino.getUniqueId(), 0, 0, 0);
  dino.hide(false);
  harness.setSceneVariable('Riding', 1);
  await harness.stepFrames(240);
  harness.assert(n('CameraResolvedDistance') > 1240 && n('CameraResolvedPitch') < 13,
    'Mounted camera excludes its own dinosaur');
} finally { harness.releaseAllInputs(); }
