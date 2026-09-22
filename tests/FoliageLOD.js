const value = (object, name) => Number(object.variables.find(v => v.name === name)?.value);
try {
  await harness.goToScene('Game');
  await harness.stepFrames(3);
  harness.setSceneVariable('Mode', 2);
  await harness.stepFrames(120);
  const player = harness.getObjects('Player3D')[0];
  const camera = harness.getCameraState('World3D');
  for (const name of ['BerryBush', 'FiberFern']) {
    const original = harness.getObjects(name)[0];
    const representations = () => [
      harness.getObjects(name).find(o => o.id === original.id),
      ...[1, 2].flatMap(level => harness.getObjects(name + 'LOD' + level)
        .filter(o => value(o, 'OwnerId') === original.id)),
    ].filter(Boolean);
    const check = (level, message) => {
      const objects = representations();
      harness.assert(objects.length === 3, name + ': one persistent instance per detail level');
      harness.assert(objects.filter(o => !o.hidden).length === 1,
        name + ': exactly one representation visible: ' + message);
      harness.assert(!objects[level]?.hidden, name + ': ' + message);
    };
    // Move sideways from the camera, away from its player sightline.
    harness.setObjectPosition(original.id, camera.x + 4200, camera.y, 0);
    await harness.stepFrames(12);
    check(2, 'far distance selects the lightest mesh');
    harness.setObjectPosition(original.id, camera.x + 1600, camera.y, 0);
    await harness.stepFrames(12);
    check(1, 'medium distance selects the middle mesh');
    harness.setObjectPosition(original.id, camera.x + 950, camera.y, 0);
    await harness.stepFrames(12);
    check(1, 'hysteresis retains middle detail inside the transition band');
    harness.setObjectPosition(original.id, player.x + 100, player.y, 0);
    await harness.stepFrames(1);
    check(0, 'interaction range immediately restores original detail');
    harness.setObjectPosition(original.id, camera.x + 4200, camera.y, 0);
    await harness.stepFrames(12);
    harness.setObjectVariable(original.id, 'Cooldown', 0.1);
    harness.setSceneVariable('Mode', 0);
    await harness.stepFrames(1);
    harness.assert(representations().every(o => o.hidden), name + ': harvest cooldown hides every detail level');
    await harness.stepFrames(15);
    check(2, 'regrowth restores exactly one distant representation');
    harness.setSceneVariable('Mode', 2);
    harness.removeObject(original.id);
    await harness.stepFrames(1);
    harness.assert(representations().length === 0, name + ': deleting a resource removes its proxies');
  }
  await harness.goToScene('Game');
  await harness.stepFrames(15);
  for (const name of ['BerryBush', 'FiberFern']) {
    for (const level of [1, 2]) harness.assert(
      harness.getObjects(name + 'LOD' + level).length === harness.getObjects(name).length,
      name + ': restarting does not duplicate LOD instances');
  }
} finally { harness.releaseAllInputs(); }
