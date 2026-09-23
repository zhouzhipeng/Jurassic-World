const number = name => Number(harness.getSceneVariable(name)?.value);
const objectNumber = (object, name) => Number(harness.getObjectVariable(object.id, name)?.value);
async function tap(key) {
  harness.setKeyPressed(key, true);
  await harness.stepFrames(1);
  harness.setKeyPressed(key, false);
  await harness.stepFrames(1);
  if (/^(b|Num[1-8]|r|PageUp|PageDown)$/.test(key)) await harness.stepFrames(6);
}
async function click(name) {
  const object = harness.getObjects(name)[0];
  harness.setMousePosition(object.x + object.width / 2, object.y + object.height / 2, object.layer);
  harness.setMouseButtonPressed(true, 'left');
  await harness.stepFrames(1);
  harness.setMouseButtonPressed(false, 'left');
  await harness.stepFrames(2);
}
try {
  await harness.goToScene('Game');
  harness.setSceneVariable('TouchMode', 0);
  await harness.stepFrames(5);
  harness.watch('ConstructionController');
  harness.assert(harness.getObjects('ConstructionController').length === 1,
    'The construction extension has one active controller');
  const records = [
    { Kind: 10, X: 200, Y: 800, Z: 20, Angle: 90, Level: 1, Parent: -1, Open: 0 },
    { Kind: 12, X: 350, Y: 800, Z: 320, Angle: 0, Level: 2, Parent: 0, Open: 0 },
  ];
  harness.setSceneVariable('BuildJSON', JSON.stringify(records));
  harness.setSceneVariable('BuildRestore', 1);
  await harness.stepFrames(5);
  const foundation = harness.getObjects('PartFoundation');
  const wall = harness.getObjects('PartWall');
  harness.assert(foundation.length === 1 && wall.length === 1,
    `The extension recreated both saved building types: foundation=${foundation.length}, wall=${wall.length}, controllerCount=${objectNumber(harness.getObjects('ConstructionController')[0], 'RestoreCount')}`);
  harness.assert(number('BuildCount') === 2 && number('BuildRestore') === 0,
    'The completion signal returned the building count');
  harness.assert(foundation[0].z === 20 && wall[0].z === 320,
    'Each restored prefab applied its saved 3D elevation');
  harness.assert(objectNumber(wall[0], 'Parent') === 0 && objectNumber(wall[0], 'Slot') === 1,
    'Restored parent and slot state preserve building relationships');
  harness.setSceneVariable('SaveStorage', 'JurassicWorldGameplayTests_ConstructionSignals');
  harness.setSceneVariable('SaveRequested', 1);
  await harness.stepFrames(4);
  harness.setSceneVariable('BuildJSON', '[]');
  harness.setSceneVariable('BuildRestore', 1);
  await harness.stepFrames(5);
  harness.assert(harness.getObjects('PartFoundation').length === 0 && harness.getObjects('PartWall').length === 0,
    'An empty restore clears the active buildings');
  await tap('Escape');
  await click('Load');
  await tap('Escape');
  await harness.stepFrames(9);
  harness.assert(harness.getObjects('PartFoundation').length === 1 && harness.getObjects('PartWall').length === 1,
    'The extension saved and reloaded the building records through signals');
} finally {
  harness.releaseAllInputs();
}
