const storage = 'JurassicWorldGameplayTests_Persistence';
const number = name => Number(harness.getSceneVariable(name)?.value);
const parts = ['PartFoundation', 'PartPillar', 'PartDoorframe', 'PartDoor', 'PartCeiling'];
function decode(variable) {
  if (!variable) throw new Error('Required variable is missing');
  if (variable.type === 'array') return (variable.children || []).map(decode);
  if (variable.type === 'structure') return Object.fromEntries((variable.children || []).map(child => [child.name, decode(child)]));
  return variable.value;
}
function records() { return JSON.stringify(decode(harness.getSceneVariable('BuildingRecords'))); }
function buildings() {
  return JSON.stringify(parts.flatMap(name => harness.getObjects(name).map(object => ({
    name, x: object.x, y: object.y, z: object.z, angle: object.angle,
    state: ['Kind', 'Slot', 'BaseZ', 'Level', 'Parent', 'Open', 'BaseAngle'].map(key => harness.getObjectVariable(object.id, key)?.value),
  }))));
}
async function tap(key) {
  harness.setKeyPressed(key, true);
  await harness.stepFrames(1);
  harness.setKeyPressed(key, false);
  await harness.stepFrames(1);
}
async function click(name) {
  const object = harness.getObjects(name)[0];
  if (!object) throw new Error(`Missing menu button ${name}`);
  harness.setMousePosition(object.x + object.width / 2, object.y + object.height / 2, object.layer);
  harness.setMouseButtonPressed(true, 'left');
  await harness.stepFrames(1);
  harness.setMouseButtonPressed(false, 'left');
  await harness.stepFrames(2);
}
async function place(key, x, y) {
  harness.setObjectPosition(harness.getObjects('Player3D')[0].id, x, y, 0);
  await harness.stepFrames(2);
  await tap(key);
  harness.assert(number('BuildValid') === 1, `Save fixture ${key} is placeable`);
  await tap('Return');
}
try {
  await harness.goToScene('Game');
  await harness.stepFrames(2);
  harness.setSceneVariable('SaveStorage', storage);
  for (const name of ['Wood', 'Stone', 'Fiber']) harness.setSceneVariable(name, 100);
  await tap('b');
  await place('Num1', 0, 750);
  await place('Num4', 0, 900);
  await place('Num6', 0, 900);
  await place('Num2', 150, 900);
  await place('Num5', 0, 750);
  await tap('b');
  harness.setObjectPosition(harness.getObjects('Player3D')[0].id, 0, 570, 0);
  await harness.stepFrames(2);
  await tap('e');
  harness.assert(Number(harness.getObjectVariable('PartDoor', 'Open')?.value) === 1, 'Save fixture contains an open door');
  const savedRecords = records();
  const savedBuildings = buildings();
  const savedMaterials = ['Wood', 'Stone', 'Fiber'].map(number).join(',');
  await tap('Escape');
  harness.assert(number('Mode') === 2, 'Escape opens the pause menu');
  await click('Save');
  harness.assert(number('SaveFlag') === 1, 'Save button confirms a completed save');
  // Recreate the scene, then load only the dedicated slot written in this run.
  await harness.goToScene('Game');
  await harness.stepFrames(2);
  harness.setSceneVariable('SaveStorage', storage);
  harness.assert(parts.every(name => harness.getObjects(name).length === 0), 'Fresh scene contains no prior test buildings');
  await tap('Escape');
  await click('Load');
  await tap('Escape');
  await harness.stepFrames(3);
  for (const name of parts) harness.watch(name);
  harness.assert(records() === savedRecords, 'Loading restores all building records, sockets, levels and support parents');
  harness.assert(buildings() === savedBuildings, 'Restored meshes preserve positions, heights, support state and the swung-open door');
  harness.assert(['Wood', 'Stone', 'Fiber'].map(number).join(',') === savedMaterials, 'Loading restores exact inventory without charging construction again');
} finally {
  harness.releaseAllInputs();
}
