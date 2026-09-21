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
  const nearBushes = harness.getObjects('BerryBush').filter(o => o.hidden);
  harness.assert(nearBushes.length > 0, 'Only foreground foliage is suppressed in the reported close-up');
  const c = camera(), p = player();
  const dx = p.x - c.x, dy = p.y - c.y, dz = 120 - c.z;
  const length = Math.hypot(dx, dy, dz);
  const blockers = ['Island3D', 'BerryBush', 'WoodSapling', 'FiberFern'].flatMap(
    name => harness.getCurrentRuntimeScene().getObjects(name)).filter(o => o.isVisible());
  harness.assert(gdjs.evtTools.scene3d.raycastObjects(c.x, c.y, c.z,
    dx / length, dy / length, dz / length, blockers, 0, length - 1, true).length === 0,
    'The player is visible from the final reported camera view');
  harness.setObjectPosition(player().id, 2000, 1500, 0);
  await harness.stepFrames(60);
  harness.assert(nearBushes.every(bush => !harness.getObjects('BerryBush').find(o => o.id === bush.id)?.hidden),
    'Camera-hidden bushes return after moving away');

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
} finally { harness.releaseAllInputs(); }
