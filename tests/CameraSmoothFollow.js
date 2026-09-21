const opacity = object => Number(object?.variables.find(v => v.name === "CameraOpacity")?.value);
const n = name => Number(harness.getSceneVariable(name)?.value);
const player = () => harness.getObjects('Player3D')[0];
const camera = () => harness.getCameraState('World3D');
try {
  await harness.goToScene('Game');
  await harness.stepFrames(3);
  harness.setSceneVariable('Mode', 2);
  harness.setObjectPosition(player().id, 508.8247954787804, 158.44715178780407, 0);
  harness.setSceneVariable('CameraYaw', 27.317073170731657);
  harness.setSceneVariable('CameraPitch', 27.838137472283826);
  harness.setSceneVariable('CameraDistance', 1250);
  let pitch = n('CameraResolvedPitch'), distance = n('CameraResolvedDistance');
  let maxPitchStep = 0, maxZoomOut = 0, minDistance = distance;
  for (let frame = 0; frame < 180; frame++) {
    await harness.stepFrames(1);
    const nextPitch = n('CameraResolvedPitch'), nextDistance = n('CameraResolvedDistance');
    maxPitchStep = Math.max(maxPitchStep, Math.abs(nextPitch - pitch));
    maxZoomOut = Math.max(maxZoomOut, nextDistance - distance);
    minDistance = Math.min(minDistance, nextDistance);
    pitch = nextPitch; distance = nextDistance;
  }
  harness.assert(minDistance > 300, `The exact reported bush never pushes the camera into the character: ${minDistance}`);
  harness.assert(maxPitchStep <= 0.68 && maxZoomOut < 65,
    `No preset-angle or zoom reset jumps: pitch step=${maxPitchStep}, zoom-out step=${maxZoomOut}`);
  const nearBushes = harness.getObjects('BerryBush').filter(o => !o.hidden && opacity(o) > 0 && opacity(o) < 200);
  harness.assert(nearBushes.length > 0, 'Foreground foliage remains visible at half opacity in the reported close-up');
  harness.assert(nearBushes.every(bush => Math.abs(opacity(bush) - 127.5) < 1),
    'Obscuring plants settle at 50 percent opacity');
  harness.assert(nearBushes.every(bush => bush.variables.find(v => v.name === 'CameraFadeReady')?.value === 1),
    'Visible faded bushes have a successfully installed transparent material');
  const harvested = nearBushes[0];
  if (harvested) {
    const object = harness.getRuntimeObject(harvested.id);
    object.getVariables().get('Cooldown').setNumber(30);
    object.hide(true);
    await harness.stepFrames(1);
    harness.assert(harness.getObjects('BerryBush').find(o => o.id === harvested.id)?.hidden,
      'Harvested foliage stays hidden while its camera fade is cleared');
  }
  const c = camera(), p = player();
  const dx = p.x - c.x, dy = p.y - c.y, dz = 120 - c.z;
  const length = Math.hypot(dx, dy, dz);
  const blockers = ['Island3D'].flatMap(
    name => harness.getCurrentRuntimeScene().getObjects(name)).filter(o => o.isVisible());
  harness.assert(gdjs.evtTools.scene3d.raycastObjects(c.x, c.y, c.z,
    dx / length, dy / length, dz / length, blockers, 0, length - 1, true).length === 0,
    'No opaque island geometry blocks the final reported camera view');
  harness.setObjectPosition(player().id, 2000, 1500, 0);
  await harness.stepFrames(60);
  harness.assert(nearBushes.every(bush => opacity(harness.getObjects('BerryBush').find(o => o.id === bush.id)) === 255),
    'Faded bushes regain full opacity after moving away');

  // Crossing foliage repeatedly must not alternate between ground and overhead views.
  harness.setObjectPosition(player().id, 508.8247954787804, 158.44715178780407, 0);
  await harness.stepFrames(90);
  pitch = n('CameraResolvedPitch');
  let worstPitch = 0, worstRecovery = 0;
  distance = n('CameraResolvedDistance');
  for (let frame = 0; frame < 180; frame++) {
    harness.setObjectPosition(player().id, 508.8247954787804 + Math.sin(frame / 22) * 90,
      158.44715178780407 + Math.sin(frame / 35) * 50, 0);
    await harness.stepFrames(1);
    worstPitch = Math.max(worstPitch, Math.abs(n('CameraResolvedPitch') - pitch));
    worstRecovery = Math.max(worstRecovery, n('CameraResolvedDistance') - distance);
    pitch = n('CameraResolvedPitch'); distance = n('CameraResolvedDistance');
  }
  harness.assert(worstPitch <= 0.68 && worstRecovery < 65,
    `Repeated foliage crossings remain gradual: angle=${worstPitch}, recovery=${worstRecovery}`);
  // Mouse orbit changes are damped without changing the user's requested direction.
  const before = camera();
  harness.setSceneVariable('CameraYaw', n('CameraYaw') + 90);
  await harness.stepFrames(1);
  const after = camera();
  const displacement = Math.hypot(after.x - before.x, after.y - before.y, after.z - before.z);
  harness.assert(displacement < 700, `A large orbit input is blended over multiple frames: ${displacement}`);
  // issue-20260921-043627-272: W/S across the spring must never enter the survivor.
  await harness.goToScene('Game');
  await harness.stepFrames(3);
  harness.setSceneVariable('Mode', 0);
  harness.setObjectPosition(player().id, -55, 818, 0);
  harness.setSceneVariable('CameraYaw', 79.02439024390236);
  harness.setSceneVariable('CameraPitch', 28.784183296378405);
  harness.setSceneVariable('CameraDistance', 1250);
  await harness.stepFrames(120);
  let closest = 1250, largestInwardStep = 0, lowestAt = '';
  let lastDistance = n('CameraResolvedDistance');
  for (const [key, frames] of [['w', 56], ['', 31], ['w', 33], ['', 17],
    ['w', 26], ['', 11], ['s', 88], ['', 53], ['s', 39], ['', 120]]) {
    if (key) harness.setKeyPressed(key, true);
    for (let frame = 0; frame < frames; frame++) {
      await harness.stepFrames(1);
      const current = n('CameraResolvedDistance');
      if (current < closest) {
        closest = current;
        lowestAt = `${player().x.toFixed(1)},${player().y.toFixed(1)}`;
      }
      largestInwardStep = Math.max(largestInwardStep, lastDistance - current);
      lastDistance = current;
    }
    harness.releaseAllInputs();
  }
  harness.assert(closest > 300,
    `Recorded spring route keeps the camera outside the character: minimum=${closest}, at=${lowestAt}`);
  harness.assert(largestInwardStep < 90,
    `Low scenery never causes a sudden close-up: largest inward step=${largestInwardStep}`);

  // In open space, starting/stopping/reversing follow must not rotate the horizon.
  harness.setSceneVariable('Mode', 2);
  for (const name of ['Island3D', 'BerryBush', 'FiberFern', 'WoodSapling', 'StoneDeposit',
    'MetalDeposit', 'SpringWater', 'CampHearth', 'CampForge', 'Dinosaur3D',
    'Triceratops', 'Stegosaur', 'Raptor', 'Tyrannosaur']) {
    for (const object of harness.getObjects(name)) harness.removeObject(object.id);
  }
  harness.setObjectPosition(player().id, 2000, 1500, 0);
  await harness.stepFrames(180);
  const settled = camera();
  let horizonDrift = 0;
  for (const speed of [-6, 0, 6, 0]) {
    for (let frame = 0; frame < 60; frame++) {
      const p = player();
      harness.setObjectPosition(p.id, p.x + speed, p.y + speed, 0);
      await harness.stepFrames(1);
      const view = camera();
      horizonDrift = Math.max(horizonDrift, Math.abs(view.rotationX - settled.rotationX),
        Math.abs(view.rotationY - settled.rotationY), Math.abs(view.angle - settled.angle));
    }
  }
  harness.assert(horizonDrift < 0.01,
    `Follow keeps a stable horizon through starts, stops and reversals: drift=${horizonDrift}`);
} finally { harness.releaseAllInputs(); }
