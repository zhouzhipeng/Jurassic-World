const n = name => Number(harness.getSceneVariable(name)?.value);
const player = () => harness.getObjects('Player3D')[0];
async function press(key, frames) {
  harness.setKeyPressed(key, true);
  await harness.stepFrames(frames);
  harness.setKeyPressed(key, false);
  await harness.stepFrames(1);
}
try {
  await harness.goToScene('Game');
  await harness.stepFrames(3);
  harness.setSceneVariable('Invulnerable', 9999);
  harness.setSceneVariable('CameraYaw', 0);
  harness.setObjectPosition(player().id, 1050, 220, 0);
  await harness.stepFrames(2);
  harness.watch('Player3D');
  harness.watch('JumpPlatform');
  harness.assert(harness.getObjects('JumpPlatform').length === 4, 'Four permanent test platforms are present');
  await press('s', 20);
  harness.assert(player().y < 280 && player().z === 0, 'A raised platform blocks walking through its side');
  harness.setKeyPressed('Space', true);
  await harness.stepFrames(12);
  harness.assert(player().z > 90 && n('CombatCD') === 0, 'Space rises above the first platform without attacking');
  harness.setKeyPressed('s', true);
  await harness.stepFrames(24);
  harness.setKeyPressed('s', false);
  await harness.stepFrames(35);
  harness.assert(player().z === 90 && n('JumpVelocity') === 0, `Land on first platform and holding Space does not auto-jump: ${player().z}`);
  harness.setKeyPressed('Space', false);
  await harness.stepFrames(1);
  // Traverse each next step using movement and jump, beginning at the previous ledge.
  for (let i = 1; i < 4; i++) {
    harness.setObjectPosition(player().id, 1050, 300 + (i-1)*340 + 220, player().z);
    await harness.stepFrames(2);
    harness.setKeyPressed('Space', true);
    harness.setKeyPressed('s', true);
    await harness.stepFrames(33);
    harness.releaseAllInputs();
    await harness.stepFrames(28);
    harness.assert(player().z === (i+1)*90, `Jump reaches step ${i+1}: z=${player().z}, y=${player().y}`);
  }
  await press('d', 40);
  await harness.stepFrames(65);
  harness.assert(player().z === 0, 'Walking off the highest platform falls to ground');
  await press('Space', 8);
  const airborne = player().z;
  harness.setSceneVariable('Mode', 2);
  await harness.stepFrames(20);
  harness.assert(player().z === airborne, 'Menus pause jump physics');
  harness.setSceneVariable('Mode', 0);
  await harness.stepFrames(65);
  const button = harness.getObjects('TouchButton').find(o => Number(harness.getObjectVariable(o.id,'Command')?.value) === 90 && Number(harness.getObjectVariable(o.id,'Active')?.value) === 1);
  harness.assert(!!button, 'An independent touch jump button is visible');
  const x = player().x;
  harness.touchStart(81, n('TouchJoyX'), n('TouchJoyY'), 'Touch');
  harness.touchMove(81, n('TouchJoyX') + n('TouchRadius')*.65, n('TouchJoyY'), 'Touch');
  harness.touchStart(82, button.centerX, button.centerY, 'Touch');
  await harness.stepFrames(1);
  harness.touchEnd(82);
  await harness.stepFrames(12);
  harness.assert(player().z > 90 && player().x > x+15, 'A second finger jumps while the joystick keeps moving');
  harness.releaseAllInputs();
  await harness.stepFrames(65);
  await press('k', 1);
  harness.assert(n('CombatCD') > 0 && player().z === 0, 'K retains keyboard combat separately from jumping');
} finally {
  harness.releaseAllInputs();
}
