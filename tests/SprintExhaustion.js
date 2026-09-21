const n = name => Number(harness.getSceneVariable(name)?.value);
const player = () => harness.getObjects('Player3D')[0];
const p = name => Number(harness.getObjectVariable(player().id, name)?.value);

async function arrange(stamina) {
  harness.releaseAllInputs();
  await harness.goToScene('Game');
  await harness.stepFrames(3);
  harness.setSceneVariable('Invulnerable', 9999);
  harness.setSceneVariable('CameraYaw', 0);
  harness.setSceneVariable('Stamina', stamina);
  // An open stretch avoids collision and combat obscuring locomotion.
  harness.setObjectPosition(player().id, 0, 800, 0);
}

async function checkRecovery(label) {
  let exhausted = false;
  let flickered = false;
  let walked = 0;
  for (let frame = 0; frame < 90; frame++) {
    await harness.stepFrames(1);
    if (p('Sprinting') === 0) exhausted = true;
    if (exhausted) {
      flickered ||= p('Sprinting') !== 0 || p('AnimationState') !== 1;
      if (p('Travel') > 0.1) walked++;
    }
  }
  harness.assert(exhausted && walked > 60 && !flickered,
    `${label}: depletion produces sustained walking without one-frame run restarts`);
  harness.assert(n('Stamina') > 2, `${label}: stamina recovers above the old one-point toggle threshold`);
  // Exercise recovery near the threshold without traversing the island for 7 seconds.
  harness.setSceneVariable('Stamina', 14.9);
  await harness.stepFrames(1);
  harness.assert(p('Sprinting') === 0, `${label}: remains walking below the recovery threshold`);
  harness.assert(await harness.stepUntil(() => p('Sprinting') === 1, { maxFrames: 20 }),
    `${label}: held input resumes sprinting after recovery`);
  await harness.stepFrames(12);
  harness.assert(p('AnimationState') === 2 && p('Travel') > 7 && p('Travel') < 9,
    `${label}: recovered run animation matches normal sprint speed`);
}

try {
  await arrange(100);
  harness.setKeyPressed('d', true);
  harness.setKeyPressed('LShift', true);
  await harness.stepFrames(20);
  harness.assert(p('AnimationState') === 2 && p('Sprinting') === 1,
    'Healthy Shift movement plays the run animation');
  harness.setKeyPressed('LShift', false);
  await harness.stepFrames(2);
  harness.assert(p('AnimationState') === 1, 'Releasing Shift returns to walking');
  harness.setKeyPressed('d', false);
  await harness.stepFrames(2);
  harness.assert(p('AnimationState') === 0, 'Releasing movement returns to idle');

  await arrange(1.1);
  harness.setKeyPressed('d', true);
  harness.setKeyPressed('LShift', true);
  await checkRecovery('Keyboard');

  await arrange(1.1);
  const x = n('TouchJoyX'), y = n('TouchJoyY'), radius = n('TouchRadius');
  harness.touchStart(61, x, y, 'Touch');
  await harness.stepFrames(1);
  harness.touchMove(61, x + radius, y, 'Touch');
  await checkRecovery('Touch');
  harness.setKeyPressed('LShift', true);
  await harness.stepFrames(2);
  harness.assert(n('MoveSpeed') === 500 && p('Travel') < 9,
    'Touch sprint plus Shift applies the sprint multiplier only once');
} finally {
  harness.releaseAllInputs();
}
