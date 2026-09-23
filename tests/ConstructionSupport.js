const number = name => Number(harness.getSceneVariable(name)?.value);
const value = (object, name) => Number(harness.getObjectVariable(object.id, name)?.value);
const materials = () => ['Wood', 'Stone', 'Fiber'].map(number).join(',');
async function tap(key) {
  harness.setKeyPressed(key, true);
  await harness.stepFrames(1);
  harness.setKeyPressed(key, false);
  await harness.stepFrames(1);
  if (/^(b|Num[1-8]|r|PageUp|PageDown)$/.test(key)) await harness.stepFrames(6);
  if (key === 'Delete') await harness.stepFrames(3);
}
async function aim(x, y) {
  harness.setObjectPosition(harness.getObjects('Player3D')[0].id, x, y, 0);
  await harness.stepFrames(2);
}
async function place(key, x, y) {
  await aim(x, y);
  await tap(key);
  const foundation = harness.getObjects('PartFoundation')[0];
  harness.assert(number('BuildValid') === 1, `Supported ${key} placement is valid: ${harness.getSceneVariable('BuildReason')?.value}; target=${number('BuildX')},${number('BuildY')}, level=${number('BuildLevel')}, parent=${number('BuildParent')}; foundation=${foundation?.x},${foundation?.y}, kind=${foundation ? value(foundation, 'Kind') : -1}, slot=${foundation ? value(foundation, 'Slot') : -1}, level=${foundation ? value(foundation, 'Level') : -1}`);
  await tap('Return');
  await harness.stepFrames(3);
}
try {
  await harness.goToScene('Game');
  await harness.stepFrames(2);
  for (const name of ['Wood', 'Stone', 'Fiber']) harness.setSceneVariable(name, 100);
  for (const name of ['PartFoundation', 'PartWall', 'PartCeiling']) harness.watch(name);
  await aim(-1800, -150);
  await tap('b');
  await tap('Num5');
  harness.assert(number('BuildValid') === 0, 'A ceiling cannot float above empty ground');
  await tap('Return');
  harness.assert(harness.getObjects('PartCeiling').length === 0 && materials() === '100,100,100',
    'Unsupported ceiling neither spawns nor consumes materials');
  await place('Num1', 0, 750);
  harness.assert(harness.getObjects('PartFoundation').length === 1,
    'Foundation placement completes through the construction signal');
  await tap('r');
  await place('Num3', 150, 750);
  await place('Num5', 0, 750);
  await tap('PageUp');
  await place('Num3', 150, 750);
  harness.assert(harness.getObjects('PartWall').length === 2 && materials() === '81,98,90',
    'Ground wall and upper wall coexist at the same horizontal socket');
  await tap('PageDown');
  await aim(0, 750);
  await tap('Num1');
  await tap('Delete');
  harness.assert(harness.getObjects('PartFoundation').length === 1 && materials() === '81,98,90',
    'Foundation demolition is blocked while dependent parts exist');
  await tap('PageUp');
  await aim(150, 750);
  await tap('Num3');
  await tap('Delete');
  const remainingWalls = harness.getObjects('PartWall');
  harness.assert(remainingWalls.length === 1 && value(remainingWalls[0], 'BaseZ') === 20,
    'Demolition at level 1 removes only the upper wall and preserves the ground wall');
  harness.assert(materials() === '83,98,91', 'Upper wall returns half of its materials, rounded down');
  await tap('PageDown');
  await aim(0, 750);
  await tap('Num5');
  await tap('Delete');
  await aim(150, 750);
  await tap('Num3');
  await tap('Delete');
  await aim(0, 750);
  await tap('Num1');
  await tap('Delete');
  harness.assert(['PartFoundation', 'PartWall', 'PartCeiling'].every(name => harness.getObjects(name).length === 0),
    'Removing children first allows the entire supported structure to be dismantled');
  harness.assert(materials() === '90,99,94', `Each removed part refunds once: ${materials()}`);
} finally {
  harness.releaseAllInputs();
}
