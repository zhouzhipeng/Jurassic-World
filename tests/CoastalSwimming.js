const n = name => Number(harness.getSceneVariable(name)?.value);
const player = () => harness.getObjects('Player3D')[0];
try {
  await harness.goToScene('Game');
  await harness.stepFrames(3);
  harness.setSceneVariable('CameraYaw', 0);
  harness.setSceneVariable('Invulnerable', 9999);
  harness.setObjectPosition(player().id, 5650, 2500, 0);
  await harness.stepFrames(3);
  harness.assert(n('SwimMode') === 0 && n('CoastEdge') > 600 && Math.abs(n('TerrainFloor')) < 2,
    `Dry sand is walkable: mode=${n('SwimMode')}, edge=${n('CoastEdge')}, floor=${n('TerrainFloor')}`);
  harness.setObjectPosition(player().id, 6300, 2500, 0);
  await harness.stepFrames(3);
  harness.assert(n('SwimMode') === 0 && n('TerrainFloor') > -130,
    `Shallow shoreline remains walkable: mode=${n('SwimMode')}, floor=${n('TerrainFloor')}`);
  harness.setObjectPosition(player().id, 6500, 2500, 0);
  await harness.stepFrames(3);
  harness.assert(n('SwimMode') === 1 && n('TerrainFloor') < -160,
    `Swimming starts before deep-water walking: mode=${n('SwimMode')}, floor=${n('TerrainFloor')}`);
  harness.setObjectPosition(player().id, 6200, 2500, 0);
  await harness.stepFrames(3);
  harness.setKeyPressed('d', true);
  await harness.stepFrames(205);
  harness.releaseAllInputs();
  const atSea = player();
  harness.assert(atSea.x > 6800 && n('CoastEdge') < 0 && n('SwimMode') === 1,
    `Player crosses the beach into swim: x=${atSea.x}, edge=${n('CoastEdge')}, mode=${n('SwimMode')}`);
  harness.assert(n('Breath') > 95 && n('JumpVelocity') === 0,
    'Surface swimming replenishes air and does not apply jump gravity');
  // Arrange deeper water within the reachable nearshore zone.
  harness.setObjectPosition(atSea.id, 7850, 2500, -245);
  await harness.stepFrames(3);
  const surface = n('PlayerFloor');
  harness.setKeyPressed('c', true);
  await harness.stepFrames(1);
  harness.releaseAllInputs();
  await harness.stepFrames(44);
  harness.assert(n('SwimMode') === 2 && n('PlayerFloor') < surface - 40 && n('DiveDepth') > 0,
    `C dives under the surface: z=${n('PlayerFloor')}, depth=${n('DiveDepth')}`);
  harness.assert(n('Breath') < 100 && n('PlayerFloor') >= n('TerrainFloor') + 19,
    `Diving consumes breath and stays above the seabed: breath=${n('Breath')}, floor=${n('TerrainFloor')}`);
  harness.setKeyPressed('Space', true);
  await harness.stepFrames(1);
  harness.releaseAllInputs();
  await harness.stepFrames(60);
  harness.assert(n('SwimMode') === 1 && n('PlayerFloor') >= surface - 2,
    `Space returns to the surface: mode=${n('SwimMode')}, z=${n('PlayerFloor')}`);
  harness.setObjectPosition(player().id, 6200, 2500, 0);
  await harness.stepFrames(3);
  harness.assert(n('SwimMode') === 0 && n('PlayerFloor') >= n('TerrainFloor') - 1,
    'Returning to shallow shore restores land movement and ground support');
} finally {
  harness.releaseAllInputs();
}
