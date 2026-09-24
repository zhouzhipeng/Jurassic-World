const n = name => Number(harness.getSceneVariable(name)?.value);
const obj = name => harness.getObjects(name)[0];
async function tap(key) {
  harness.setKeyPressed(key, true);
  try { await harness.stepFrames(1); }
  finally { harness.releaseAllInputs(); }
  await harness.stepFrames(1);
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
  try { await harness.stepFrames(45); }
  finally { harness.releaseAllInputs(); }
  harness.assert(obj('Pterosaur3D').z > start.z + 200 && n('FlightAltitude') > start.z + 200,
    'Holding Space climbs more than two metres');
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
} finally {
  harness.releaseAllInputs();
}
