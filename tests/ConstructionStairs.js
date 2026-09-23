const number = name => Number(harness.getSceneVariable(name)?.value);
const player = () => harness.getObjects('Player3D')[0];
async function tap(key) {
  harness.setKeyPressed(key, true);
  await harness.stepFrames(1);
  harness.setKeyPressed(key, false);
  await harness.stepFrames(1);
  if (/^(b|Num[1-8]|r|PageUp|PageDown)$/.test(key)) await harness.stepFrames(6);
}
async function place(key, x, y) {
  harness.setObjectPosition(player().id, x, y, 0);
  await harness.stepFrames(2);
  await tap(key);
  harness.assert(number('BuildValid') === 1, `Stair fixture ${key} is placeable: ${harness.getSceneVariable('BuildReason')?.value}`);
  await tap('Return');
}
async function walk(key, frames) {
  harness.setKeyPressed(key, true);
  await harness.stepFrames(frames);
  harness.setKeyPressed(key, false);
  await harness.stepFrames(1);
}
try {
  await harness.goToScene('Game');
  await harness.stepFrames(2);
  for (const name of ['Wood', 'Stone', 'Fiber']) harness.setSceneVariable(name, 100);
  // Arrange an already-cleared work site, not a harvesting outcome.
  for (const bush of harness.getObjects('BerryBush')) {
    if (Math.abs(bush.x) < 180 && Math.abs(bush.y - 600) < 180) harness.setObjectVariable(bush.id, 'Cooldown', 60);
  }
  harness.watch('Player3D');
  harness.watch('PartStairs');
  await tap('b');
  await place('Num1', 0, 750);
  await place('Num1', 0, 1050);
  await place('Num2', 150, 900);
  await place('Num5', 0, 750);
  await place('Num7', 0, 1050);
  harness.assert(harness.getObjects('PartStairs').length === 1, 'Stairs attach to the lower foundation');
  await tap('Num5');
  const wood = number('Wood');
  await tap('Return');
  harness.assert(harness.getObjects('PartCeiling').length === 1 && number('Wood') === wood,
    'A ceiling cannot cover the staircase headroom');
  await tap('b');
  harness.setObjectPosition(player().id, 0, 820, 0);
  await harness.stepFrames(2);
  await walk('w', 80);
  harness.assert(player().y < 450 && player().z === 320, `Walking up stairs reaches the upper floor: y=${player().y}, z=${player().z}`);
  await harness.stepFrames(30);
  harness.assert(player().z === 320 && number('PlayerFloor') === 320, 'Player remains supported while standing on the upper floor');
  await walk('s', 80);
  await harness.stepFrames(15);
  harness.assert(player().y > 780 && player().z === 0, `Walking down returns to ground: y=${player().y}, z=${player().z}`);
} finally {
  harness.releaseAllInputs();
}
