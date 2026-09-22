// Keep the complete world and HUD. Synthetic HitFlash isolates the overlay;
// the final scenario independently exercises actual predator damage.
const s = name => Number(harness.getSceneVariable(name)?.value);
const observations = [];
async function measure(label, frames) {
  harness.startProfiling();
  await harness.stepFrames(frames);
  const p = harness.stopProfiling();
  harness.assert(!!p && Number.isFinite(p.avgStepTimeMs), label + ': valid profile');
  const times = p.frameTimesMs.slice().sort((a, b) => a - b);
  observations.push({ label, mean: p.avgStepTimeMs,
    p95: times[Math.floor((times.length - 1) * .95)], max: p.maxStepTimeMs });
}
try {
  await harness.goToScene('Game');
  await harness.stepFrames(4);
  harness.setSceneVariable('Mode', 0);
  harness.setSceneVariable('Invulnerable', 9999);
  harness.setObjectPosition(harness.getObjects('Player3D')[0].id, 1700, -4100, 0);
  harness.setSceneVariable('CameraYaw', 180);
  harness.setSceneVariable('CameraPitch', 24);
  await harness.stepFrames(90);
  for (const touch of [1, 0]) {
    harness.setSceneVariable('TouchMode', touch);
    await harness.stepFrames(3);
    await measure('idle touch=' + touch, 120);
    harness.setSceneVariable('HitFlash', 3);
    await measure('damage touch=' + touch, 120);
    const flash = harness.getObjects('DamageFlash')[0];
    const layer = touch ? 'Touch' : 'HUD';
    harness.assert(!flash.hidden && flash.layer === layer && flash.opacity > 0,
      'Damage pulse visible on ' + layer);
    harness.assert(Math.abs(flash.width - harness.getRuntimeLayer(layer).getCameraWidth()) < 1 &&
      Math.abs(flash.height - harness.getRuntimeLayer(layer).getCameraHeight()) < 1,
      'Damage pulse covers ' + layer);
    await harness.stepFrames(210);
    harness.assert(harness.getObjects('DamageFlash')[0].hidden, 'Pulse expires touch=' + touch);
  }
  harness.setSceneVariable('TouchMode', 1);
  harness.setObjectPosition(harness.getObjects('Player3D')[0].id, 1800, 900, 0);
  await harness.stepFrames(60);
  const player = harness.getObjects('Player3D')[0];
  const enemy = harness.getObjects('Raptor')[0];
  harness.setObjectPosition(enemy.id, player.x, player.y - 200, player.z);
  harness.setObjectVariable(enemy.id, 'Cooldown', 0);
  harness.setObjectVariable(enemy.id, 'AIClock', 0);
  harness.setSceneVariable('Health', 100);
  harness.setSceneVariable('Invulnerable', 0);
  await measure('real repeated raptor bites', 300);
  harness.assert(s('Health') <= 76 && s('Health') > 0, 'Repeated real bites reduce health: ' + s('Health'));
  harness.assert(harness.getPlayedSounds().some(sound => sound.sound === 'hurt.wav'), 'Real bite plays hurt audio');
  harness.setSceneVariable('Invulnerable', 9999);
  await measure('damage recovery', 180);
  harness.assert(harness.getObjects('DamageFlash')[0].hidden, 'Overlay clears after attacks stop');
  // Reproduce the report's mountain position and camera without deleting scenery.
  harness.setObjectPosition(harness.getObjects('Player3D')[0].id, 4687.91, 545.62, 1440.46);
  harness.setSceneVariable('CameraYaw', 80.97561);
  harness.setSceneVariable('CameraPitch', 12.23651);
  await harness.stepFrames(90);
  harness.setSceneVariable('HitFlash', 3);
  harness.setSceneVariable('NoticeMessage', '受击性能回归：迅猛龙撕咬，请拉开距离。');
  await measure('reported mountain attack feedback', 120);
  harness.assert(observations.every(o => o.max <= 1000 / 60),
    'Every sampled frame <= 16.67 ms: ' + JSON.stringify(observations));
} finally { harness.releaseAllInputs(); }
