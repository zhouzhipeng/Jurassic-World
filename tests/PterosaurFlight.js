const n = name => Number(harness.getSceneVariable(name)?.value);
const obj = name => harness.getObjects(name)[0];
async function tap(key) {
  harness.setKeyPressed(key, true);
  try { await harness.stepFrames(1); }
  finally { harness.releaseAllInputs(); }
  await harness.stepFrames(1);
}
async function tapTouch(command) {
  const button = harness.getObjects('TouchButton').find(o =>
    Number(harness.getObjectVariable(o.id, 'Active')?.value) === 1 &&
    Number(harness.getObjectVariable(o.id, 'Command')?.value) === command);
  if (!button) { harness.fail(`Touch command ${command} is unavailable`); return; }
  harness.touchStart(71, button.centerX, button.centerY, 'Touch');
  try { await harness.stepFrames(1); }
  finally { harness.touchEnd(71); }
  await harness.stepFrames(3);
}
function touchButton(command) {
  return harness.getObjects('TouchButton').find(o =>
    Number(harness.getObjectVariable(o.id, 'Active')?.value) === 1 &&
    Number(harness.getObjectVariable(o.id, 'Command')?.value) === command);
}
try {
  await harness.goToScene('Game');
  await harness.stepFrames(4);
  harness.setSceneVariable('Mode', 0);
  harness.setSceneVariable('TouchMode', 0);
  harness.setSceneVariable('Invulnerable', 9999);
  const ptero = obj('Pterosaur3D');
  harness.assert(!!ptero && !!obj('PterosaurSaddle3D'), 'The pterosaur and separate saddle assets spawn');
  harness.setObjectPosition(obj('Player3D').id, ptero.x - 300, ptero.y, 0);
  harness.setSceneVariable('PlayerFloor', 0);
  await harness.stepFrames(3);
  const oldHide = n('Hide'), oldFiber = n('Fiber'), oldRope = n('Rope');
  harness.assert(n('PterosaurSaddle') === 0 && obj('PterosaurSaddle3D').hidden,
    'The saddle starts uncrafted and hidden');
  await tap('x');
  harness.assert(n('PterosaurSaddle') === 1 && n('Riding') === 2,
    `Mount input crafts the saddle and boards the pterosaur: saddle=${n('PterosaurSaddle')}, riding=${n('Riding')}`);
  harness.assert(n('Hide') === oldHide - 4 && n('Fiber') === oldFiber - 8 && n('Rope') === oldRope - 3,
    'Saddle crafting consumes exactly four hide, eight fiber and three rope');
  harness.assert(!obj('PterosaurSaddle3D').hidden && !obj('PterosaurRider3D').hidden,
    'The fitted saddle and seated rider are visible');
  const start = obj('Pterosaur3D');
  harness.setKeyPressed('Space', true);
  try {
    await harness.stepFrames(1);
    harness.assert(n('FlightAltitude') - start.z < 20,
      'The first held keyboard frame accelerates without a height jump');
    await harness.stepFrames(44);
  }
  finally { harness.releaseAllInputs(); }
  harness.assert(obj('Pterosaur3D').z > start.z + 200 && n('FlightAltitude') > start.z + 200,
    'Holding Space climbs more than two metres');
  await harness.stepFrames(30);
  const releasedHeight = n('FlightAltitude');
  await harness.stepFrames(15);
  harness.assert(Math.abs(n('FlightAltitude') - releasedHeight) < 3 && Math.abs(n('FlightVerticalSpeed')) < 1,
    'Releasing Space eases the pterosaur to a stop');
  harness.setKeyPressed('w', true);
  try { await harness.stepFrames(24); }
  finally { harness.releaseAllInputs(); }
  const moved = obj('Pterosaur3D');
  harness.assert(Math.hypot(moved.x - start.x, moved.y - start.y) > 40,
    'W steers the mounted pterosaur across the island');
  harness.assert(Math.abs(obj('Player3D').x - moved.x) < 2 && Math.abs(n('PlayerFloor') - moved.z) < 2,
    'The player and camera floor follow the flying mount');
  await tap('x');
  harness.assert(n('Riding') === 2, 'X cannot dismount in the air');
  harness.setKeyPressed('LControl', true);
  try { await harness.stepFrames(90); }
  finally { harness.releaseAllInputs(); }
  harness.assert(n('FlightAltitude') <= n('TerrainFloor') + 35,
    'Ctrl descends until the pterosaur reaches the terrain');
  await tap('x');
  harness.assert(n('Riding') === 0 && !obj('Player3D').hidden && obj('PterosaurRider3D').hidden,
    'X dismounts after landing and restores the visible player');

  // The game's mobile context button mounts the same fitted saddle.
  harness.setSceneVariable('TouchMode', 1);
  harness.setObjectPosition(obj('Player3D').id, obj('Pterosaur3D').x - 230, obj('Pterosaur3D').y, 0);
  await harness.stepFrames(4);
  await tapTouch(306);
  harness.assert(n('Riding') === 2, 'The contextual touch button mounts the pterosaur');
  const touchGround = n('FlightAltitude');
  const ascend = touchButton(90);
  harness.assert(!!ascend, 'The touch ascent control is available while mounted');
  harness.touchStart(72, ascend.centerX, ascend.centerY, 'Touch');
  try {
    await harness.stepFrames(1);
    harness.assert(n('FlightAltitude') - touchGround < 20,
      'Touch ascent starts smoothly without an instant height jump');
    await harness.stepFrames(44);
    harness.assert(n('FlightAltitude') > touchGround + 180,
      'Holding the touch ascent button continuously lifts the pterosaur');
  } finally { harness.touchEnd(72); }
  await harness.stepFrames(30);
  const touchReleasedHeight = n('FlightAltitude');
  await harness.stepFrames(15);
  harness.assert(Math.abs(n('FlightAltitude') - touchReleasedHeight) < 3,
    'Releasing touch ascent stops further climbing');
  const descend = touchButton(91);
  harness.assert(!!descend, 'The touch descent control is available while mounted');
  harness.touchStart(73, descend.centerX, descend.centerY, 'Touch');
  try { await harness.stepFrames(100); }
  finally { harness.touchEnd(73); }
  await harness.stepFrames(3);
  harness.assert(n('FlightAltitude') <= n('TerrainFloor') + 35, 'The touch descent button lands the pterosaur');
  await tapTouch(307);
  harness.assert(n('Riding') === 0, 'The contextual touch button dismounts after landing');
} finally {
  harness.releaseAllInputs();
}
