// Arrange inventory and a clear site; all buildings are placed through real input.
const number = name => Number(harness.getSceneVariable(name)?.value);
const player = () => harness.getObjects('Player3D')[0];
const materials = () => ['Wood', 'Stone', 'Fiber'].map(number).join(',');
async function tap(key) {
  harness.setKeyPressed(key, true);
  await harness.stepFrames(1);
  harness.setKeyPressed(key, false);
  await harness.stepFrames(1);
  if (/^(b|Num[1-8]|r|PageUp|PageDown)$/.test(key)) await harness.stepFrames(6);
  if (key === 'Return') await harness.stepFrames(3);
}
try {
  await harness.goToScene('Game');
  await harness.stepFrames(2);
  harness.watch('PartFoundation');
  for (const name of ['Wood', 'Stone', 'Fiber']) harness.setSceneVariable(name, 100);
  harness.setObjectPosition(player().id, 20, 740, 0);
  await tap('b');
  await tap('Num1');
  harness.assert(number('BuildValid') === 1, 'Clear ground accepts a foundation');
  await tap('Return');
  const first = harness.getObjects('PartFoundation');
  harness.assert(first.length === 1 && first[0].x === 600 && first[0].y === 900,
    'Off-grid aim snaps the foundation to (600, 900)');
  harness.assert(materials() === '94,98,97', `One foundation costs 6/2/3, observed ${materials()}`);
  await harness.stepFrames(15);
  await tap('Return');
  harness.assert(harness.getObjects('PartFoundation').length === 1 && materials() === '94,98,97',
    'Idle frames and duplicate placement neither create another part nor charge materials');
  harness.setObjectPosition(player().id, 320, 740, 0);
  await harness.stepFrames(5);
  harness.assert(number('BuildValid') === 1, 'Adjacent foundation socket is valid');
  await tap('Return');
  harness.assert(harness.getObjects('PartFoundation').length === 2 && materials() === '88,96,94',
    'Adjacent foundation is created and charged exactly once');
  // A separate empty site isolates material rejection from overlap rejection.
  harness.setObjectPosition(player().id, 20, 1040, 0);
  harness.setSceneVariable('Wood', 0);
  await harness.stepFrames(5);
  const before = materials();
  harness.assert(number('BuildValid') === 0, 'Insufficient wood invalidates the clear socket');
  await tap('Return');
  harness.assert(harness.getObjects('PartFoundation').length === 2 && materials() === before,
    'Rejected placement leaves inventory and building count unchanged');
  harness.assert(String(harness.getSceneVariable('BuildReason')?.value).includes('木 6'),
    'The rejection explains the exact six-wood shortage');
  const hint = harness.getObjects('TouchHint')[0].text;
  harness.assert(hint.includes('持有/需要') && hint.includes('木 0/6'),
    'The build HUD distinguishes held materials from the foundation cost');
  harness.setSceneVariable('Wood', 6);
  harness.setSceneVariable('Stone', 1);
  harness.setSceneVariable('Fiber', 1);
  await harness.stepFrames(5);
  const shortage = String(harness.getSceneVariable('BuildReason')?.value);
  harness.assert(shortage.includes('石 1') && shortage.includes('纤维 2'),
    'Simultaneous stone and fiber shortages are both shown');
  harness.setSceneVariable('Stone', 2);
  harness.setSceneVariable('Fiber', 3);
  await harness.stepFrames(5);
  harness.assert(number('BuildValid') === 1, 'Supplying the exact missing materials enables placement');
  await tap('Return');
  harness.assert(harness.getObjects('PartFoundation').length === 3 && materials() === '0,0,0',
    'The previously rejected tile places successfully and consumes exactly its cost');
} finally {
  harness.releaseAllInputs();
}
