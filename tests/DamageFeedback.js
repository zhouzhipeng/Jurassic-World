const n = name => Number(harness.getSceneVariable(name)?.value);
const object = name => harness.getObjects(name)[0];
try {
  await harness.goToScene('Game');
  await harness.stepFrames(4);
  harness.setObjectPosition(object('Player3D').id, 1800, 900, 0);
  harness.setSceneVariable('Invulnerable', 9999);
  await harness.stepFrames(60);
  const player = object('Player3D');
  const raptor = object('Raptor');
  harness.setObjectPosition(raptor.id, player.x, player.y - 200, player.z);
  harness.setObjectVariable(raptor.id, 'Cooldown', 0);
  harness.setObjectVariable(raptor.id, 'AIClock', 0);
  harness.setSceneVariable('Health', 100);
  harness.setSceneVariable('Invulnerable', 0);
  const bitten = await harness.stepUntil(() => n('Health') < 100, { maxFrames: 90 });
  harness.assert(bitten && n('Health') === 88, 'Real raptor bite applies exactly 12 damage');
  harness.assert(!object('DamageFlash').hidden && object('DamageFlash').layer === 'Touch',
    'Real bite displays the touch damage overlay');
  await harness.stepFrames(2);
  harness.assert(!object('TouchToastText').hidden && object('TouchToastText').text.includes('迅猛龙撕咬'),
    'Attack notification remains visible with the actual message');
  harness.assert(object('TouchStatus').text.includes('88'), 'Health HUD shows the damaged health');
  harness.assert(object('Player3D').children?.Body?.[0].animation === 'Hurt', 'Actual survivor plays Hurt');
  const health = n('Health');
  await harness.stepFrames(12);
  harness.assert(n('Health') === health, 'The same bite does not apply damage every frame');
  harness.setSceneVariable('Invulnerable', 9999);
  for (const touch of [0, 1]) {
    harness.setSceneVariable('TouchMode', touch);
    harness.setSceneVariable('HitFlash', .35);
    await harness.stepFrames(2);
    const flash = object('DamageFlash');
    harness.assert(!flash.hidden && flash.layer === (touch ? 'Touch' : 'HUD'),
      'Active overlay follows input mode ' + touch);
  }
  harness.getRuntimeGame().setGameResolutionSize(1600, 650);
  await harness.stepFrames(3);
  const flash = object('DamageFlash'), layer = harness.getRuntimeLayer('Touch');
  harness.assert(Math.abs(flash.width - layer.getCameraWidth()) < 1 &&
    Math.abs(flash.height - layer.getCameraHeight()) < 1, 'Active overlay resizes with the viewport');
  const toast = object('TouchToastText');
  harness.assert(toast.x >= 0 && toast.y >= 0 && toast.x + toast.width <= harness.getGameResolutionWidth() + 1,
    'Attack notification remains within the resized viewport');
  harness.setSceneVariable('Mode', 2);
  await harness.stepFrames(2);
  harness.assert(object('DamageFlash').hidden, 'Pause hides the damage overlay');
  harness.setSceneVariable('Mode', 0);
  await harness.stepFrames(220);
  harness.assert(object('DamageFlash').hidden && object('TouchToastText').hidden,
    'Overlay and notification both expire after recovery');
  harness.assert(object('Player3D').children?.Body?.[0].animation !== 'Hurt', 'Recovery exits Hurt animation');
} finally {
  harness.releaseAllInputs();
  harness.getRuntimeGame().setGameResolutionSize(1600, 900);
}
