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
  harness.watch('PartWall');
  harness.watch('Player3D');
  await harness.stepFrames(1);
  const wallHits = gdjs.evtTools.scene3d.raycastObjects(2000, 1500, 120, 0,
    Math.cos(25 * Math.PI / 180), Math.sin(25 * Math.PI / 180),
    [harness.getRuntimeObject(wall.id)], 0, 1280, true);
  const nearbyNames = ['Island3D', 'BerryBush', 'FiberFern', 'WoodSapling', 'StoneDeposit', 'MetalDeposit', 'SpringWater', 'CampHearth', 'CampForge', 'PartWall', 'Dinosaur3D', 'Triceratops', 'Stegosaur', 'Raptor', 'Tyrannosaur'];
  const candidates = nearbyNames.flatMap(name => harness.getCurrentRuntimeScene().getObjects(name)).filter(o => o.isVisible());
  const diagnosticHits = [-80, 0, 80].flatMap(z => [-65, 0, 65].flatMap(x =>
    gdjs.evtTools.scene3d.raycastObjects(player().x + x, player().y, targetZ() + z,
      0, Math.cos(25 * Math.PI / 180), Math.sin(25 * Math.PI / 180), candidates, 0, 1280, true)
      .slice(0, 1).map(h => [h.object.getName(), h.distance, h.pointX, h.pointY, h.pointZ])));
  harness.assert(n('CameraResolvedDistance') < 500 && n('CameraDistance') === 1250,
    `A newly placed wall retracts the camera in one frame without changing requested zoom: distance=${n('CameraResolvedDistance')}, hits=${JSON.stringify(diagnosticHits)}, center=${wallHits.length}`);
  clearSight([harness.getRuntimeObject(wall.id)], 'Wall');
  const compressed = n('CameraResolvedDistance');
  harness.getRuntimeObject(wall.id).hide(true);
  await harness.stepFrames(1);
  harness.assert(n('CameraResolvedDistance') > compressed && n('CameraResolvedDistance') < 1250,
    'Hidden geometry stops blocking and zoom recovers smoothly');
  await harness.stepFrames(90);
  harness.assert(Math.abs(n('CameraResolvedDistance') - 1250) < 1,
    'The selected zoom is restored when the obstruction clears');
  harness.getRuntimeObject(wall.id).hide(false);
  harness.setObjectPosition(wall.id, 2000, 1620, 0);
  await harness.stepFrames(1);
  harness.assert(n('CameraResolvedPitch') > 25 && n('CameraResolvedDistance') > 260,
    'A close wall selects a clear higher angle without pushing the camera into the player');
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
  harness.setSceneVariable('CameraPitch', 25);
  harness.setSceneVariable('CameraDistance', 2000);
  const scene = harness.getCurrentRuntimeScene();
  const terrain = scene.getObjects('Island3D');
  let obstructedOrbits = 0;
  for (const position of [[1600, 800], [1800, 1650], [0, 0]]) {
    harness.setObjectPosition(player().id, position[0], position[1], 0);
    for (let yaw = 0; yaw < 360; yaw += 45) {
      harness.setSceneVariable('CameraYaw', yaw);
      await harness.stepFrames(1);
      if (n('CameraSafeDistance') < 1900) obstructedOrbits++;
      clearSight(terrain, `Island ${position.join(',')} yaw ${yaw}`);
      harness.assert(n('CameraResolvedDistance') <= n('CameraSafeDistance') + 0.01,
        'Orbit changes never ease through an obstruction');
    }
  }
  harness.assert(obstructedOrbits > 0, 'The island sweep exercised actual scenery obstructions');
} finally { harness.releaseAllInputs(); }
