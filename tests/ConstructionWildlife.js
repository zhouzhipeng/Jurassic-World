const n = name => Number(harness.getSceneVariable(name)?.value);
const obj = name => harness.getObjects(name)[0];
const materials = () => ['Wood', 'Stone', 'Fiber'].map(n).join(',');
const reason = () => String(harness.getSceneVariable('BuildReason')?.value);
async function tap(key) {
  harness.setKeyPressed(key, true); await harness.stepFrames(1);
  harness.setKeyPressed(key, false); await harness.stepFrames(1);
  if (/^(b|Num[1-8]|r|PageUp|PageDown)$/.test(key)) await harness.stepFrames(6);
  if (key === 'Return') await harness.stepFrames(3);
}
async function dinosaur(x, y, angle) {
  const id = obj('Stegosaur').id;
  harness.setObjectPosition(id, x, y, 0);
  harness.getRuntimeObject(id).setAngle(angle);
  harness.setObjectVariable(id, 'AIClock', 0);
  harness.setObjectVariable(id, 'State', 0);
  await harness.stepFrames(5);
}
try {
  await harness.goToScene('Game'); await harness.stepFrames(3);
  harness.setSceneVariable('Invulnerable', 9999);
  for (const name of ['Wood', 'Stone', 'Fiber']) harness.setSceneVariable(name, 100);
  harness.setSceneVariable('CameraYaw', 0);
  // Recreate the existing foundation next to the reported tile through placement input.
  await dinosaur(1179.4426591115339, 1557.2124306621397, -205.24553228988913);
  harness.setObjectPosition(obj('Player3D').id, 600, 1050, 0);
  await tap('b'); await tap('Num1'); await tap('Return');
  harness.assert(harness.getObjects('PartFoundation').length === 1,
    `The neighboring foundation can be placed: ${reason()}`);
  harness.setObjectPosition(obj('Player3D').id, 600, 1350, 0);
  await tap('r');
  await harness.stepFrames(5);
  harness.assert(n('BuildX') === 600 && n('BuildY') === 900 && n('BuildValid') === 1,
    `The exact reported tile is clear beside the rotated stegosaur: ${reason()}`);

  // The long body must not become a circular exclusion zone along its narrow side.
  await dinosaur(900, 900, 0);
  harness.assert(n('BuildValid') === 1, `Clearance beside the body is buildable: ${reason()}`);
  await dinosaur(900, 900, 90);
  harness.assert(n('BuildValid') === 0 && reason().includes('恐龙'),
    'Rotating the long body across the tile correctly blocks construction');
  const before = materials();
  await tap('Return');
  harness.assert(harness.getObjects('PartFoundation').length === 1 && materials() === before,
    'A dinosaur overlap neither creates a foundation nor consumes materials');
  await dinosaur(600, 900, 45);
  harness.assert(n('BuildValid') === 0 && reason().includes('恐龙'),
    'A diagonal dinosaur through the foundation remains blocked');
  await dinosaur(600, 1330, 0);
  harness.assert(n('BuildValid') === 0 && reason().includes('恐龙'),
    'The dinosaur tail still blocks an overlapping foundation edge');

  await dinosaur(1179.4426591115339, 1557.2124306621397, -205.24553228988913);
  await tap('Return');
  const foundations = harness.getObjects('PartFoundation');
  harness.assert(foundations.length === 2 && foundations.some(o => o.x === 600 && o.y === 900),
    'The reported adjacent foundation is successfully placed');
  harness.assert(materials() === '88,96,94', `Two foundations cost exactly 12/4/6: ${materials()}`);
  await tap('Return');
  harness.assert(harness.getObjects('PartFoundation').length === 2 && materials() === '88,96,94',
    'Duplicate placement remains rejected without a second charge');
} finally { harness.releaseAllInputs(); }
