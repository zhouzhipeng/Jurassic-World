const player = () => harness.getObjects('Player3D')[0];
const n = name => Number(harness.getSceneVariable(name)?.value);
try {
  await harness.goToScene('Game');
  await harness.stepFrames(3);
  harness.setSceneVariable('Mode',0);
  harness.setSceneVariable('Invulnerable',9999);
  harness.setObjectPosition(player().id,-1000.2820158411475,-769.4598185499594,30.5);
  harness.setSceneVariable('PlayerFloor',30.5);
  harness.setSceneVariable('CameraYaw',20.162601626016382);
  harness.setSceneVariable('CameraPitch',23.825572801182563);
  harness.setSceneVariable('CameraDistance',1250);
  await harness.stepFrames(120);
  for (const scenario of ['idle','movement','first orbit','warm orbit']) {
    harness.startProfiling();
    for (let frame=0;frame<180;frame++) {
      if (scenario==='movement') {
        if (frame%30===0) {
          harness.releaseAllInputs();
          harness.setKeyPressed(['s','d','w','a','s','w'][Math.floor(frame/30)],true);
        }
      }
      if (scenario.endsWith('orbit')) harness.setSceneVariable('CameraYaw',20.162601626016382+frame*2);
      await harness.stepFrames(1);
    }
    harness.releaseAllInputs();
    const p=harness.stopProfiling();
    const times=p.frameTimesMs.slice().sort((a,b)=>a-b);
    const p95=times[Math.floor((times.length-1)*.95)];
    // First exposure includes shader/render setup; recurring cost has the
    // tighter budget. Keep both measurements instead of hiding cold frames.
    const cold = scenario==='first orbit';
    harness.assert(p.avgStepTimeMs<(cold ? 33.3 : 25) && p95<(cold ? 66.7 : 40),
      `Indoor ${scenario}: mean/p95/max=${p.avgStepTimeMs}/${p95}/${p.maxStepTimeMs} ms`);
    harness.assert(Number.isFinite(n('CameraResolvedDistance')) && n('CameraResolvedDistance')>=300,
      `Indoor ${scenario}: camera keeps finite framing`);
    harness.assert(player().z===30.5, `Indoor ${scenario}: player remains on the floor`);
  }
} finally { harness.releaseAllInputs(); }
