const number = name => Number(harness.getSceneVariable(name)?.value);
const player = () => harness.getObjects('Player3D')[0];
const doorOpen = () => Number(harness.getObjectVariable('PartDoor', 'Open')?.value);
async function tap(key) {
  harness.setKeyPressed(key, true);
  await harness.stepFrames(1);
  harness.setKeyPressed(key, false);
  await harness.stepFrames(1);
  if (/^(b|Num[1-8]|r|PageUp|PageDown)$/.test(key)) await harness.stepFrames(6);
  if (key === 'Return' || key === 'e') await harness.stepFrames(3);
}
async function walk(key, frames) {
  harness.setKeyPressed(key, true);
  await harness.stepFrames(frames);
  harness.setKeyPressed(key, false);
  await harness.stepFrames(1);
}
async function aim(x, y) {
  harness.setObjectPosition(player().id, x, y, 0);
  await harness.stepFrames(2);
}
try {
  await harness.goToScene('Game');
  await harness.stepFrames(2);
  for (const name of ['Wood', 'Stone', 'Fiber']) harness.setSceneVariable(name, 100);
  harness.watch('Player3D');
  harness.watch('PartDoor');
  await aim(0, 750);
  await tap('b');
  await tap('Num1');
  await tap('Return');
  await aim(0, 900);
  await tap('Num6');
  await tap('Return');
  harness.assert(harness.getObjects('PartDoor').length === 0, 'Door requires a matching door frame');
  await tap('Num4');
  await tap('Return');
  await tap('Num6');
  await tap('Return');
  harness.assert(harness.getObjects('PartDoor').length === 1 && doorOpen() === 0, 'Door snaps into its frame and starts closed');
  await tap('b');
  const closedDoor = harness.getObjects('PartDoor')[0];
  harness.setSceneVariable('CameraYaw', 0);
  await aim(closedDoor.x, closedDoor.y + 120);
  await walk('w', 80);
  harness.assert(player().y > closedDoor.y + 30 && player().y < closedDoor.y + 120,
    `Closed door blocks forward movement: player=${player().x},${player().y}, door=${closedDoor.x},${closedDoor.y}`);
  await tap('e');
  harness.assert(doorOpen() === 1, 'E opens the nearby door');
  // An open leaf has moved, but its original socket must remain occupied.
  harness.setSceneVariable('CameraYaw', -90);
  await aim(0, 900);
  await tap('b');
  await tap('Num6');
  const wood = number('Wood');
  await tap('Return');
  harness.assert(harness.getObjects('PartDoor').length === 1 && number('Wood') === wood,
    'Opening a door does not free its socket for a duplicate');
  await tap('b');
  harness.setSceneVariable('CameraYaw', 0);
  await aim(closedDoor.x, closedDoor.y + 120);
  await walk('w', 120);
  harness.assert(player().y < closedDoor.y - 30, `Player walks through open doorway onto the floor: y=${player().y}, doorY=${closedDoor.y}`);
  await walk('s', 120);
  await tap('e');
  harness.assert(doorOpen() === 0, 'E closes the same door again');
  await aim(closedDoor.x, closedDoor.y + 120);
  await walk('w', 80);
  harness.assert(player().y > closedDoor.y + 30, 'Closing the door restores its blocking collision');
} finally {
  harness.releaseAllInputs();
}
