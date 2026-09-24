await harness.goToScene('Game');
await harness.stepFrames(4);

const boat = harness.getObjects('Rowboat')[0];
harness.assert(!!boat, 'The coastal scene has a rowboat');
const runtimeBoat = harness.getRuntimeObject(boat.id);
harness.assert(!!runtimeBoat, 'The rowboat can be positioned for the shore approach');

// Begin just offshore, facing west. The A key rows west with zero camera yaw.
harness.setObjectPosition(boat.id, 6500, -1000);
runtimeBoat.setAngle(90);
harness.setSceneVariable('Mode', 0);
harness.setSceneVariable('CameraYaw', 0);
harness.setSceneVariable('Sailing', 1);
await harness.stepFrames(2);

harness.setKeyPressed('a', true);
try {
  await harness.stepFrames(80);
} finally {
  harness.releaseAllInputs();
}

const stopped = harness.getObjects('Rowboat')[0];
harness.assert(!!stopped && stopped.x < 6480,
  `The boat rows toward the shore: x=${stopped?.x}`);
harness.assert(!!stopped && stopped.x > 6370,
  `The boat remains afloat before the beach: x=${stopped?.x}`);
const rider = harness.getObjects('Player3D')[0];
harness.assert(!!rider && Math.abs(rider.x - stopped.x) < 1 && Math.abs(rider.y - stopped.y) < 1,
  'The rider stays aligned with the stopped boat');
