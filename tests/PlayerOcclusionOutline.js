const player = () => harness.getObjects('Player3D')[0];
const amount = () => Number(harness.getObjectVariable(player().id, 'OcclusionAmount')?.value);
const body = () => player().children?.Body?.[0];
try {
  await harness.goToScene('Game');
  await harness.stepFrames(3);
  harness.setSceneVariable('Mode', 2);
  // Isolate line-of-sight cases from roaming wildlife and the island camera solver.
  for (const name of ['Island3D', 'BerryBush', 'FiberFern', 'WoodSapling', 'StoneDeposit',
    'MetalDeposit', 'SpringWater', 'CampHearth', 'CampForge', 'Dinosaur3D',
    'Triceratops', 'Stegosaur', 'Raptor', 'Tyrannosaur']) {
    for (const object of harness.getObjects(name)) harness.removeObject(object.id);
  }
  harness.setObjectPosition(player().id, 2000, 1500, 0);
  harness.setSceneVariable('CameraYaw', 0);
  harness.setSceneVariable('CameraPitch', 25);
  harness.setSceneVariable('CameraDistance', 1250);
  await harness.stepFrames(90);
  harness.assert(amount() === 0, 'Clear view keeps the original character appearance');
  harness.assert(!player().children?.OcclusionOutline?.length,
    'The silhouette uses the real body rather than a second animated model');
  const plant = harness.spawn('WoodSapling', 2000, 1700, -60, 'World3D');
  await harness.stepFrames(30);
  harness.assert(amount() > 0.95,
    `Foreground tree reveals the outline even when foliage fades: ${amount()}`);
  harness.assert(!!body() && !body().hidden,
    'Occlusion preserves the animated body that supplies the silhouette mask');
  harness.setObjectVariable(plant.id, 'Cooldown', 30);
  harness.getRuntimeObject(plant.id).hide(true);
  await harness.stepFrames(30);
  harness.assert(amount() === 0, 'Hidden or harvested blockers do not retain an outline');
  harness.setObjectVariable(plant.id, 'Cooldown', 0);
  harness.getRuntimeObject(plant.id).hide(false);
  harness.setObjectPosition(plant.id, 2200, 1700, -60);
  await harness.stepFrames(30);
  harness.assert(amount() === 0, 'A tree beside the sightline does not trigger highlighting');
  harness.removeObject(plant.id);
  const wall = harness.spawn('PartWall', 2000, 1575, 0, 'World3D');
  await harness.stepFrames(8);
  harness.assert(amount() > 0, `A nearby solid wall also triggers the outline: ${amount()}`);
  harness.removeObject(wall.id);
  await harness.stepFrames(90);
  harness.assert(amount() === 0, 'Removing a solid obstruction clears the outline');
  harness.setSceneVariable('Mode', 0);
  harness.setSceneVariable('Invulnerable', 9999);
  harness.setKeyPressed('Space', true);
  await harness.stepFrames(5);
  harness.releaseAllInputs();
  harness.assert(body()?.animation === 'JumpStart',
    'The silhouette source follows the real jump animation');
  await harness.stepFrames(65);
  harness.assert(body()?.animation === 'Idle', 'Landing recovers the original body animation');
  harness.watch('Player3D');
} finally {
  harness.releaseAllInputs();
}
