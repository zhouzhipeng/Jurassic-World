const n = name => Number(harness.getSceneVariable(name)?.value);
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
  const startingMeat = n('Meat');
  await tap('g');
  harness.assert(n('FishingState') === 0 && n('Meat') === startingMeat, 'G cannot fish on land');

  // Start on the existing boat to isolate fishing from the boarding journey.
  harness.setSceneVariable('Sailing', 1);
  await harness.stepFrames(2);
  await tap('g');
  harness.assert(n('FishingState') === 1, 'G casts a line from a stationary boat');
  await tap('g');
  harness.assert(n('FishingState') === 3 && n('Meat') === startingMeat, 'Reeling before a bite loses the attempt');
  await harness.stepFrames(95);
  await tap('g');
  harness.assert(n('FishingState') === 1, 'Fishing can resume after the short recovery');
  await harness.stepFrames(182);
  harness.assert(n('FishingState') === 2, 'A bite opens after waiting with the boat still');
  await tap('g');
  harness.assert(n('FishingState') === 3 && n('Meat') === startingMeat + 1, 'A timely reel adds exactly one raw food to the existing inventory');

  await harness.stepFrames(125);
  await tap('g');
  harness.assert(n('FishingState') === 1, 'A new cast begins after catching a fish');
  harness.setKeyPressed('w', true);
  try { await harness.stepFrames(3); }
  finally { harness.releaseAllInputs(); }
  harness.assert(n('FishingState') === 3, 'Rowing cancels the fishing attempt');
  await harness.stepFrames(95);
  await tap('g');
  harness.assert(n('FishingState') === 1, 'The player can cast again after stopping');
  harness.setSceneVariable('Sailing', 0);
  await harness.stepFrames(2);
  harness.assert(n('FishingState') === 0 && n('Meat') === startingMeat + 1, 'Leaving the boat clears the line without another catch');
} finally {
  harness.releaseAllInputs();
}
