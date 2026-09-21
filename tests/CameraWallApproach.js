const n = name => Number(harness.getSceneVariable(name)?.value);
const player = () => harness.getObjects('Player3D')[0];
try {
  await harness.goToScene('Game');
  await harness.stepFrames(3);
  harness.setSceneVariable('Mode', 0);
  harness.setObjectPosition(player().id, -614.4224308277594, -200, 0);
  harness.setSceneVariable('CameraYaw', 60.48780487804886);
  harness.setSceneVariable('CameraPitch', 27.36511456023651);
  harness.setSceneVariable('CameraDistance', 1750);
  await harness.stepFrames(120);
  let closest = 1750, largestStep = 0, previous = n('CameraResolvedDistance');
  let worst = '';
  for (const [keys, frames] of [[['w','d'],26],[['d'],22],[['w','d'],23],[[],60],
    [['w'],60],[[],45],[['s'],30],[[],60]]) {
    for (const key of keys) harness.setKeyPressed(key, true);
    for (let frame = 0; frame < frames; frame++) {
      await harness.stepFrames(1);
      const distance = n('CameraResolvedDistance');
      if (distance < closest) {
        closest = distance;
        worst = `position=${player().x},${player().y}; safe=${n('CameraSafeDistance')}; pitch=${n('CameraResolvedPitch')}`;
      }
      largestStep = Math.max(largestStep, Math.abs(distance - previous));
      previous = distance;
    }
    harness.releaseAllInputs();
  }
  harness.assert(closest > 1650,
    `An unobstructed camera stays wide while approaching/pressing the wall: distance=${closest}; ${worst}`);
  harness.assert(largestStep < 40, `No zoom pumping at wall contact: largest step=${largestStep}`);
} finally { harness.releaseAllInputs(); }
