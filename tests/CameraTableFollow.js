const n = name => Number(harness.getSceneVariable(name)?.value);
const player = () => harness.getObjects('Player3D')[0];
try {
  await harness.goToScene('Game');
  await harness.stepFrames(3);
  harness.setSceneVariable('Mode', 2);
  harness.setObjectPosition(player().id, -1175.2840105504042, -66.17404914226792, 0);
  harness.setSceneVariable('CameraYaw', 27.317073170731835);
  harness.setSceneVariable('CameraPitch', 28.78418329637843);
  harness.setSceneVariable('CameraDistance', 1950);
  await harness.stepFrames(120);
  const p = player(), yaw = n('CameraYaw') * Math.PI / 180;
  const pitch = n('CameraPitch') * Math.PI / 180;
  const solids = ['Island3D', 'CampForge', 'CampHearth', 'StoneDeposit'].flatMap(
    name => harness.getCurrentRuntimeScene().getObjects(name));
  const hits = [];
  for (const [side, height] of [[0,0],[-65,0],[65,0],[0,80],[-65,80],[65,80]]) {
    for (const hit of gdjs.evtTools.scene3d.raycastObjects(
      p.x + Math.cos(yaw) * side, p.y - Math.sin(yaw) * side, 120 + height,
      Math.sin(yaw) * Math.cos(pitch), Math.cos(yaw) * Math.cos(pitch), Math.sin(pitch),
      solids, 0, 1950, true).slice(0,2)) {
      hits.push({side, height, object:hit.object.getName(), distance:hit.distance, z:hit.pointZ});
    }
  }
  harness.assert(n('CameraResolvedDistance') >= 600,
    `Table view must not enter the survivor: distance=${n('CameraResolvedDistance')}; probes=${JSON.stringify(hits)}`);
} finally { harness.releaseAllInputs(); }
