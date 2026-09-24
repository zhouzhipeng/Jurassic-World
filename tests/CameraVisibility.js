const n = name => Number(harness.getSceneVariable(name)?.value);
const player = () => harness.getObjects('Player3D')[0];
const camera = () => harness.getCameraState('World3D');
const targetZ = () => 120 + n('PlayerFloor') + n('Riding') * 220;
function clearSight(blockers, label) {
  const p = player(), c = camera();
  harness.assert(!!c && Number.isFinite(c.x + c.y + c.z), `${label}: finite camera`);
  if (!c) return;
  // Observe actual camera-to-head/torso/feet visibility, independently of solver variables.
  for (const height of [-70, 0, 70]) {
    const dx = p.x - c.x, dy = p.y - c.y, dz = targetZ() + height - c.z;
    const length = Math.hypot(dx, dy, dz);
    const hits = gdjs.evtTools.scene3d.raycastObjects(c.x, c.y, c.z,
      dx / length, dy / length, dz / length, blockers, 0, length - 1, true);
    harness.assert(hits.length === 0, `${label}: body height ${height} is unobstructed`);
  }
}
try {
  await harness.goToScene('Game');
  await harness.stepFrames(3);
  // Freeze gameplay to isolate camera response, which must also run in menus/photo mode.
  harness.setSceneVariable('Mode', 2);
  harness.setSceneVariable('CameraYaw', 0);
  harness.setSceneVariable('CameraPitch', 25);
  harness.setSceneVariable('CameraDistance', 1250);
  harness.setObjectPosition(player().id, 2000, 1500, 0);
  const island = harness.getRuntimeObject('Island3D');
  island.hide(true);
  // Nearby resource bushes must not compete with the deliberately arranged wall.
  for (const name of ['BerryBush', 'FiberFern', 'WoodSapling', 'StoneDeposit',
    'MetalDeposit', 'SpringWater', 'Dinosaur3D', 'Triceratops', 'Stegosaur', 'Raptor', 'Tyrannosaur']) {
    for (const object of harness.getObjects(name)) harness.removeObject(object.id);
  }
  await harness.stepFrames(90);
  const wall = harness.spawn('PartWall', 2000, 1950, 100, 'World3D');
  // The construction prefab owns its height and reapplies BaseZ every frame.
  harness.setObjectVariable(wall.id, 'BaseZ', 100);
  harness.watch('PartWall');
  harness.watch('Player3D');
  await harness.stepFrames(1);
  const wallRuntime = harness.getRuntimeObject(wall.id);
  const wallRenderer = wallRuntime?.get3DRendererObject();
  const probe = gdjs.evtTools.scene3d.raycastObjects(2000, 1500, 220, 0, 1, 0.3, [wallRuntime], 0, 1250, true);
  harness.assert(n('CameraResolvedDistance') < 500 && n('CameraDistance') === 1250,
    `A newly placed wall retracts the camera in one frame without changing requested zoom: distance=${n('CameraResolvedDistance')}, z=${wallRuntime?.getZ()}, children=${wallRenderer?.children.length}, group=${wallRenderer?.position.x},${wallRenderer?.position.y},${wallRenderer?.position.z}, child=${wallRenderer?.children[0]?.position.x},${wallRenderer?.children[0]?.position.y},${wallRenderer?.children[0]?.position.z}, probe=${probe.length}`);
  clearSight([harness.getRuntimeObject(wall.id)], 'Wall');
  const compressed = n('CameraResolvedDistance');
  harness.getRuntimeObject(wall.id).hide(true);
  await harness.stepFrames(20);
  harness.assert(n('CameraResolvedDistance') > compressed && n('CameraResolvedDistance') < 1250,
    'Hidden geometry stops blocking and zoom recovers smoothly');
  await harness.stepFrames(180);
  harness.assert(Math.abs(n('CameraResolvedDistance') - 1250) < 1,
    'The selected zoom is restored when the obstruction clears');
  harness.getRuntimeObject(wall.id).hide(false);
  harness.setObjectPosition(wall.id, 2000, 1620, 0);
  const previousPitch = n('CameraResolvedPitch');
  await harness.stepFrames(1);
  harness.assert(Math.abs(n('CameraResolvedPitch') - previousPitch) < 1,
    'A close wall does not snap the camera to a preset angle');
  await harness.stepFrames(240);
  harness.assert(n('CameraResolvedPitch') > 25 && n('CameraResolvedDistance') > 260,
    'A close wall gradually selects a clear higher angle');
  clearSight([harness.getRuntimeObject(wall.id)], 'Close wall');
  harness.removeObject(wall.id);
  harness.setSceneVariable('PlayerFloor', 600);
  harness.setSceneVariable('Riding', 1);
  await harness.stepFrames(1);
  const p = player(), c = camera(), d = n('CameraResolvedDistance');
  harness.assert(Math.abs(c.z - (targetZ() + Math.sin(n('CameraResolvedPitch') * Math.PI / 180) * d)) < 0.01,
    'Camera uses the current elevated mounted target height');
  harness.assert(Math.abs(c.x - p.x) < 0.01, 'Camera remains centered on the mounted target');

  // Exercise real combined island geometry, including the trees from the reported view.
  await harness.goToScene('Game');
  await harness.stepFrames(3);
  harness.setSceneVariable('Mode', 2);
  harness.setObjectPosition(player().id, 704.9452698315055, 1569.948293057374, 0);
  harness.setSceneVariable('CameraYaw', -43.86724579574575);
  harness.setSceneVariable('CameraPitch', 31.72602739726028);
  harness.setSceneVariable('CameraDistance', 750);
  await harness.stepFrames(1);
  clearSight(harness.getCurrentRuntimeScene().getObjects('Island3D'), 'Reported tree obstruction');
  // Clear body sight is the contract; low ground probes no longer force needless zoom.
  harness.assert(n('CameraResolvedDistance') <= 750 && n('CameraResolvedDistance') >= 220,
    `The reported view retains safe player framing at or within the requested zoom: ${n('CameraResolvedDistance')}`);
  harness.setSceneVariable('CameraPitch', 25);
  harness.setSceneVariable('CameraDistance', 2000);
  const scene = harness.getCurrentRuntimeScene();
  const terrain = scene.getObjects('Island3D');
  let obstructedOrbits = 0;
  for (const position of [[1600, 800], [1800, 1650], [0, 0]]) {
    harness.setObjectPosition(player().id, position[0], position[1], 0);
    for (let yaw = 0; yaw < 360; yaw += 45) {
      harness.setSceneVariable('CameraYaw', yaw);
      await harness.stepFrames(60);
      if (n('CameraSafeDistance') < 1900) obstructedOrbits++;
      clearSight(terrain, `Island ${position.join(',')} yaw ${yaw}`);
      harness.assert(n('CameraResolvedDistance') <= n('CameraSafeDistance') + 0.01,
        'Orbit changes never ease through an obstruction');
    }
  }
  harness.assert(obstructedOrbits > 0, 'The island sweep exercised actual scenery obstructions');
} finally { harness.releaseAllInputs(); }
