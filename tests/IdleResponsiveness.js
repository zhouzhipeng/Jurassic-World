// issue-20260921-135045-743: exact idle platform view from the report.
const n = name => Number(harness.getSceneVariable(name)?.value);
const player = () => harness.getObjects('Player3D')[0];
async function tap(command) {
  const button = harness.getObjects('TouchButton').find(o =>
    Number(harness.getObjectVariable(o.id, 'Active')?.value) === 1 &&
    Number(harness.getObjectVariable(o.id, 'Command')?.value) === command);
  if (!button) throw new Error(`Missing touch command ${command}`);
  harness.touchStart(71, button.centerX, button.centerY, 'Touch');
  await harness.stepFrames(1);
  harness.touchEnd(71);
  await harness.stepFrames(2);
}
try {
  await harness.goToScene('Game');
  await harness.stepFrames(3);
  harness.setObjectPosition(player().id, 1054.63, 388.13, 90);
  for (const [name, value] of Object.entries({ PlayerFloor: 90,
    CameraYaw: 176.910569105691, CameraPitch: 29.5018477457502,
    CameraDistance: 500 })) harness.setSceneVariable(name, value);
  await harness.stepFrames(120);
  for (let window = 0; window < 6; window++) {
    harness.startProfiling();
    await harness.stepFrames(900);
    const profile = harness.stopProfiling();
    harness.assert(profile.avgStepTimeMs < 33.3,
      `Idle ${(window + 1) * 15}s mean/max ${profile.avgStepTimeMs}/${profile.maxStepTimeMs} ms`);
  }
  const before = player();
  harness.setKeyPressed('Space', true);
  await harness.stepFrames(8);
  harness.releaseAllInputs();
  harness.assert(n('PlayerFloor') > before.z + 20, 'Keyboard jump responds after 90s idle');
  await harness.stepFrames(80);
  await tap(1);
  harness.assert(n('Mode') === 2, 'Touch menu opens after prolonged idle');
  await tap(8);
  harness.assert(n('Mode') === 0, 'Touch resume returns to gameplay');
  const start = player();
  harness.setKeyPressed('s', true);
  await harness.stepFrames(30);
  harness.releaseAllInputs();
  harness.assert(Math.hypot(player().x - start.x, player().y - start.y) > 20,
    'Movement remains responsive after idle and menu resume');
} finally { harness.releaseAllInputs(); }
