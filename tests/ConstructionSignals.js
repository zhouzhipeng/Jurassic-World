const number = name => Number(harness.getSceneVariable(name)?.value);
const objectNumber = (object, name) => Number(harness.getObjectVariable(object.id, name)?.value);
try {
  await harness.goToScene('Game');
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
    `The extension recreated both saved building types: foundation=${foundation.length}, wall=${wall.length}, controllerCount=${objectNumber(harness.getObjects('ConstructionController')[0], 'RestoreCount')}, payloadLength=${objectNumber(harness.getObjects('ConstructionController')[0], 'LastPayloadLength')}, parsedCount=${objectNumber(harness.getObjects('ConstructionController')[0], 'LastParsedCount')}, BuildCount=${number('BuildCount')}`);
  harness.assert(number('BuildCount') === 2 && number('BuildRestore') === 0,
    'The completion signal returned the building count');
  harness.assert(foundation[0].z === 20 && wall[0].z === 320,
    'Each restored prefab applied its saved 3D elevation');
  harness.assert(objectNumber(wall[0], 'Parent') === 0 && objectNumber(wall[0], 'Slot') === 1,
    'Restored parent and slot state preserve building relationships');
} finally {
  harness.releaseAllInputs();
}
