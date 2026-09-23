const n = name => Number(harness.getSceneVariable(name)?.value);
const obj = name => harness.getObjects(name)[0];
const materials = () => ['Wood', 'Stone', 'Fiber'].map(n).join(',');
const reason = () => String(harness.getSceneVariable('BuildReason')?.value);
async function tap(key) {
  harness.setKeyPressed(key, true); await harness.stepFrames(1);
  harness.setKeyPressed(key, false); await harness.stepFrames(1);
  if (/^(b|Num[1-8]|r|PageUp|PageDown)$/.test(key)) await harness.stepFrames(3);
}
async function dinosaur(x, y, angle) {
  const id = obj('Stegosaur').id;
  harness.setObjectPosition(id, x, y, 0);
  harness.getRuntimeObject(id).setAngle(angle);
  harness.setObjectVariable(id, 'AIClock', 0);
  harness.setObjectVariable(id, 'State', 0);
  await harness.stepFrames(2);
}
try {
  await harness.goToScene('Game'); await harness.stepFrames(3);
  harness.setSceneVariable('Invulnerable', 9999);
  for (const name of ['Wood', 'Stone', 'Fiber']) harness.setSceneVariable(name, 100);
  harness.setSceneVariable('CameraYaw', 0);
  // Recreate the existing foundation next to the reported tile through placement input.
  await dinosaur(1179.4426591115339, 1557.2124306621397, -205.24553228988913);
  harness.setObjectPosition(obj('Player3D').id, 1800, 1650, 0);
  await tap('b'); await tap('Num1'); await tap('Return');
  harness.assert(harness.getObjects('PartFoundation').length === 1,
    `The neighboring foundation can be placed: ${reason()}`);
  harness.setObjectPosition(obj('Player3D').id, 1611.8431285193344, 783.858892678727, 0);
  harness.setSceneVariable('CameraYaw', 147.64227642276367);
  harness.setSceneVariable('BuildAngle', 90);
  await harness.stepFrames(2);
  harness.assert(n('BuildX') === 1500 && n('BuildY') === 1200 && n('BuildValid') === 1,
    `The exact reported tile is clear beside the rotated stegosaur: ${reason()}`);

  // The long body must not become a circular exclusion zone along its narrow side.
  await dinosaur(1800, 1200, 0);
  harness.assert(n('BuildValid') === 1, `Clearance beside the body is buildable: ${reason()}`);
  await dinosaur(1800, 1200, 90);
  harness.assert(n('BuildValid') === 0 && reason().includes('恐龙'),
    'Rotating the long body across the tile correctly blocks construction');
  const before = materials();
  await tap('Return');
  harness.assert(harness.getObjects('PartFoundation').length === 1 && materials() === before,
    'A dinosaur overlap neither creates a foundation nor consumes materials');
  await dinosaur(1500, 1200, 45);
  harness.assert(n('BuildValid') === 0 && reason().includes('恐龙'),
    'A diagonal dinosaur through the foundation remains blocked');
  await dinosaur(1500, 1630, 0);
  harness.assert(n('BuildValid') === 0 && reason().includes('恐龙'),
    'The dinosaur tail still blocks an overlapping foundation edge');

  await dinosaur(1179.4426591115339, 1557.2124306621397, -205.24553228988913);
  await tap('Return');
  const foundations = harness.getObjects('PartFoundation');
  harness.assert(foundations.length === 2 && foundations.some(o => o.x === 1500 && o.y === 1200),
    'The reported adjacent foundation is successfully placed');
  harness.assert(materials() === '88,96,94', `Two foundations cost exactly 12/4/6: ${materials()}`);
  await tap('Return');
  harness.assert(harness.getObjects('PartFoundation').length === 2 && materials() === '88,96,94',
    'Duplicate placement remains rejected without a second charge');
} finally { harness.releaseAllInputs(); }
