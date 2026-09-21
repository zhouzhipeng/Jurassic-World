const n = name => Number(harness.getSceneVariable(name)?.value);
const player = () => harness.getObjects('Player3D')[0];
try {
  await harness.goToScene('Game');
  await harness.stepFrames(3);
  harness.setSceneVariable('Mode', 0);
  harness.setObjectPosition(player().id, -446.7471751788618, -961.2302091713711, 0);
  harness.setSceneVariable('CameraYaw', 42.92682926829274);
  harness.setSceneVariable('CameraPitch', 12);
  harness.setSceneVariable('CameraDistance', 1250);
  await harness.stepFrames(120);
  let closest = 1250, largestStep = 0, previous = n('CameraResolvedDistance'), worst = '';
  for (const [keys, frames] of [[['w'],75],[[],90],[['s'],75],[[],90],
    [['a','w'],8],[['w'],55],[[],90],[['a','s'],31],[['s'],8],[[],45],
    [['s','d'],49],[['d'],13],[[],90]]) {
    for (const key of keys) harness.setKeyPressed(key,true);
    for (let frame=0; frame<frames; frame++) {
      await harness.stepFrames(1);
      const distance=n('CameraResolvedDistance');
      if(distance<closest) {
        closest=distance;
        const follow=harness.getCurrentRuntimeScene().getVariables().get('CameraFollow');
        const x=follow.getChild('X').getAsNumber(), y=follow.getChild('Y').getAsNumber();
        const yaw=follow.getChild('Yaw').getAsNumber()*Math.PI/180, pitch=n('CameraResolvedPitch')*Math.PI/180;
        const probes=[];
        for(const [side,height] of [[0,0],[-65,0],[65,0],[0,80],[-65,80],[65,80]]) {
          const hits=gdjs.evtTools.scene3d.raycastObjects(x+Math.cos(yaw)*side,y-Math.sin(yaw)*side,120+height,
            Math.sin(yaw)*Math.cos(pitch),Math.cos(yaw)*Math.cos(pitch),Math.sin(pitch),
            harness.getCurrentRuntimeScene().getObjects('Island3D'),0,400,true);
          for(const hit of hits.slice(0,1)) probes.push({side,height,d:hit.distance,x:hit.pointX,y:hit.pointY,z:hit.pointZ});
        }
        worst=JSON.stringify({x:player().x,y:player().y,pitch:n('CameraResolvedPitch'),safe:n('CameraSafeDistance'),probes});
      }
      largestStep=Math.max(largestStep,Math.abs(distance-previous)); previous=distance;
    }
    harness.releaseAllInputs();
  }
  harness.assert(closest>=290,`Fence crossings preserve useful third-person framing: min=${closest}; largestStep=${largestStep}; ${worst}`);
  harness.assert(largestStep<90,`Fence crossings do not cause abrupt zoom: ${largestStep}`);
} finally { harness.releaseAllInputs(); }
