const n = name => Number(harness.getSceneVariable(name)?.value);
const player = () => harness.getObjects('Player3D')[0];
try {
  await harness.goToScene('Game');
  await harness.stepFrames(3);
  harness.setSceneVariable('Mode', 2);
  harness.setObjectPosition(player().id, -1175.2840105504042, -66.17404914226792, 0);
  harness.setSceneVariable('CameraYaw', 27.317073170731835);
  harness.setSceneVariable('CameraPitch', 28.78418329637843);
  harness.setSceneVariable('CameraDistance', 1950);
  await harness.stepFrames(120);
  const p = player(), yaw = n('CameraYaw') * Math.PI / 180;
  const pitch = n('CameraPitch') * Math.PI / 180;
  const solids = ['Island3D', 'CampForge', 'CampHearth', 'StoneDeposit'].flatMap(
    name => harness.getCurrentRuntimeScene().getObjects(name));
  const hits = [];
  for (const [side, height] of [[0,0],[-65,0],[65,0],[0,80],[-65,80],[65,80]]) {
    for (const hit of gdjs.evtTools.scene3d.raycastObjects(
      p.x + Math.cos(yaw) * side, p.y - Math.sin(yaw) * side, 120 + height,
      Math.sin(yaw) * Math.cos(pitch), Math.cos(yaw) * Math.cos(pitch), Math.sin(pitch),
      solids, 0, 1950, true).slice(0,2)) {
      hits.push({side, height, object:hit.object.getName(), distance:hit.distance, z:hit.pointZ});
    }
  }
  harness.assert(n('CameraResolvedDistance') >= 600,
    `Table view must not enter the survivor: distance=${n('CameraResolvedDistance')}; probes=${JSON.stringify(hits)}`);
  // Replay approaches and reversals around this table with the real movement input.
  harness.setSceneVariable('Mode', 0);
  let closest = n('CameraResolvedDistance'), largestStep = 0;
  let previous = closest;
  for (const [key, frames] of [['s', 35], ['', 20], ['w', 26], ['', 39],
    ['s', 31], ['', 30], ['w', 28], ['', 90]]) {
    if (key) harness.setKeyPressed(key, true);
    for (let frame = 0; frame < frames; frame++) {
      await harness.stepFrames(1);
      const distance = n('CameraResolvedDistance');
      closest = Math.min(closest, distance);
      largestStep = Math.max(largestStep, Math.abs(distance - previous));
      previous = distance;
    }
    harness.releaseAllInputs();
  }
  harness.assert(closest >= 600, `Table approaches keep a usable follow distance: ${closest}`);
  harness.assert(largestStep < 90, `No abrupt zoom on table approaches/reversals: ${largestStep}`);
  const c = harness.getCameraState('World3D'), finalPlayer = player();
  const dx = finalPlayer.x - c.x, dy = finalPlayer.y - c.y, dz = 200 - c.z;
  const length = Math.hypot(dx, dy, dz);
  harness.assert(gdjs.evtTools.scene3d.raycastObjects(c.x, c.y, c.z,
    dx / length, dy / length, dz / length, solids, 0, length - 1, true).length === 0,
    'The survivor head is visible from the resulting table view');
} finally { harness.releaseAllInputs(); }
