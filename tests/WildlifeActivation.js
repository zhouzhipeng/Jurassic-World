const value = (id, key) => Number(harness.getObjectVariable(id, key)?.value);
try {
  await harness.goToScene('Game');
  await harness.stepFrames(4);
  harness.setSceneVariable('Mode', 0);
  harness.setSceneVariable('Invulnerable', 9999);
  const player = harness.getObjects('Player3D')[0];
  const heyin = harness.getObjects('Heyin')[0];
  const actor = harness.getObjects('Raptor')[0];
  harness.setObjectPosition(player.id, 0, 400, 0);
  harness.setObjectPosition(heyin.id, 350, 900, 0);
  harness.setObjectPosition(actor.id, 4500, 4500, 0);
  harness.setObjectVariable(actor.id, 'HomeX', 4500);
  harness.setObjectVariable(actor.id, 'HomeY', 4500);
  await harness.stepFrames(2);
  const clock = value(actor.id, 'Clock'), hp = value(actor.id, 'HP');
  await harness.stepFrames(30);
  harness.assert(value(actor.id, 'Clock') === clock && value(actor.id, 'HP') === hp,
    'Distant living wildlife retains identity and health without running patrol AI');
  harness.setObjectPosition(player.id, 3700, 4500, 0);
  await harness.stepFrames(3);
  harness.assert(value(actor.id, 'Clock') > clock, 'Approaching immediately resumes wildlife AI');
  harness.setObjectPosition(player.id, 0, 400, 0);
  harness.setObjectPosition(heyin.id, 3400, 4500, 0);
  const nearCompanion = value(actor.id, 'Clock');
  await harness.stepFrames(3);
  harness.assert(value(actor.id, 'Clock') > nearCompanion,
    'Wildlife remains active around the companion even when the player is far away');
  harness.setObjectPosition(heyin.id, 350, 900, 0);
  harness.setObjectVariable(actor.id, 'HP', 0);
  await harness.stepFrames(2);
  harness.assert(value(actor.id, 'State') === 4, 'Distant lethal damage runs the normal death state');
  harness.setObjectVariable(actor.id, 'Respawn', 0.1);
  await harness.stepFrames(10);
  harness.assert(value(actor.id, 'HP') > 0 && value(actor.id, 'State') !== 4,
    'Distant dead wildlife continues its respawn timer and revives');
} finally { harness.releaseAllInputs(); }
