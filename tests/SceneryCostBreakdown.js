// Diagnostic isolation only: removed objects are not a playable configuration.
try {
  await harness.goToScene('Game');
  await harness.stepFrames(3);
  harness.setSceneVariable('Mode',0);
  harness.setSceneVariable('Invulnerable',9999);
  for (const phase of ['complete','without island','without plants']) {
    if (phase==='without island') harness.removeObject(harness.getObjects('Island3D')[0].id);
    if (phase==='without plants') for (const name of ['BerryBush','FiberFern','WoodSapling']) {
      for (const object of harness.getObjects(name)) harness.removeObject(object.id);
    }
    harness.setObjectPosition(harness.getObjects('Player3D')[0].id,505.4276289009733,223.47497304164955,0);
    harness.setSceneVariable('CameraYaw',82.92682926829268);
    harness.setSceneVariable('CameraPitch',24.290465631929056);
    harness.setSceneVariable('CameraDistance',1250);
    await harness.stepFrames(30);
    harness.startProfiling();
    for (const key of ['w','d','s','a']) {
      harness.setKeyPressed(key,true);
      await harness.stepFrames(30);
      harness.releaseAllInputs();
    }
    const p=harness.stopProfiling();
    harness.assert(!!p && Number.isFinite(p.avgStepTimeMs),`${phase}: mean=${p?.avgStepTimeMs}ms`);
  }
} finally { harness.releaseAllInputs(); }
