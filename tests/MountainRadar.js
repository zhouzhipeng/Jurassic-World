const obj = name => harness.getObjects(name)[0];
const n = name => Number(harness.getSceneVariable(name)?.value);
const game = harness.getRuntimeGame();
const original = [game.getGameResolutionWidth(),game.getGameResolutionHeight()];
async function press(key,frames) {
  harness.setKeyPressed(key,true);
  try { await harness.stepFrames(frames); }
  finally { harness.releaseAllInputs(); }
  await harness.stepFrames(1);
}
try {
  await harness.goToScene('Game');
  await harness.stepFrames(4);
  harness.setSceneVariable('Mode',0);
  harness.setSceneVariable('Invulnerable',9999);
  const species = ['Dinosaur3D','Triceratops','Stegosaur','Raptor','Tyrannosaur'];
  harness.assert(species.reduce((sum,name)=>sum+harness.getObjects(name).length,0)===25,'Expanded island contains 25 dinosaurs');
  harness.assert(harness.getObjects('MetalDeposit').length===12 && harness.getObjects('SpringWater').length===6,'Outer regions contain 12 ore seams and 6 springs');
  harness.assert(new Set(harness.getObjects('MetalDeposit').map(o=>harness.getObjectVariable(o.id,'SiteId')?.value)).size===12,'Ore seams retain independent save identities');
  const scene = harness.getCurrentRuntimeScene();
  // Compare gameplay elevation to the exported triangle surface, not a copy of
  // the mathematical height formula. Avoid camp props and tree trunks.
  for (const [x,y] of [[0,-1600],[1700,-4100],[-3800,-3900],[4250,1800],[-2400,3900]]) {
    harness.setObjectPosition(obj('Player3D').id,x,y,0);
    harness.setSceneVariable('PlayerFloor',0);
    harness.setSceneVariable('JumpVelocity',0);
    await harness.stepFrames(3);
    const p=obj('Player3D');
    const hits=gdjs.evtTools.scene3d.raycastObjects(p.x,p.y,8000,0,0,-1,scene.getObjects('Island3D'),0,9000,true);
    const closest=hits.reduce((best,h)=>Math.min(best,Math.abs(h.pointZ-p.z)),Infinity);
    harness.assert(p.z>50 && closest<12,`Ground follows actual mountain mesh at ${x},${y}: z=${p.z}, error=${closest}`);
  }
  harness.setObjectPosition(obj('Player3D').id,0,-1500,0);
  harness.setSceneVariable('PlayerFloor',0);
  harness.setSceneVariable('CameraYaw',0);
  await harness.stepFrames(3);
  const start=obj('Player3D'); const radarStart=obj('RadarPlayer');
  await press('w',35);
  const walked=obj('Player3D');
  harness.assert(walked.y<start.y-100 && walked.z>start.z+20,'Real movement climbs the mountain slope');
  harness.assert(obj('RadarPlayer').y<radarStart.y,'Northward movement moves the radar marker upward');
  const ground=walked.z;
  await press('Space',12);
  harness.assert(obj('Player3D').z>ground+70,'Space jumps above elevated terrain');
  await harness.stepFrames(65);
  harness.assert(Math.abs(obj('Player3D').z-n('TerrainFloor'))<1 && n('JumpVelocity')===0,'Jump lands back on the mountain surface');
  harness.setObjectPosition(obj('Player3D').id,2850,4600,0);
  harness.setSceneVariable('PlayerFloor',0);
  await harness.stepFrames(3);
  await press('d',40);
  harness.assert(obj('Player3D').x>3030 && obj('Player3D').y>4400,'Player can explore beyond both former map boundaries');
  harness.setObjectPosition(obj('Dinosaur3D').id,1700,-4100,0);
  harness.setSceneVariable('Riding',1);
  await harness.stepFrames(3);
  harness.assert(obj('Dinosaur3D').z>1800 && Math.abs(n('PlayerFloor')-obj('Dinosaur3D').z)<1,'Mounted camera anchor follows high mountain terrain');
  harness.setSceneVariable('Riding',0);
  harness.setObjectPosition(obj('Player3D').id,-650,350,0);
  harness.setSceneVariable('PlayerFloor',0);
  for(const [width,height] of [[1600,900],[568,320],[720,900]]) {
    game.setGameResolutionSize(width,height);
    await harness.stepFrames(4);
    const map=obj('RadarMap');
    const actualWidth=game.getGameResolutionWidth(), actualHeight=game.getGameResolutionHeight();
    harness.assert(!map.hidden && map.x>=0 && map.x+map.width<=actualWidth && map.y+map.height<=actualHeight,`Radar fits top-right: requested ${width}x${height}, actual ${actualWidth}x${actualHeight}, map ${map.x},${map.y},${map.width},${map.height}`);
    const buttons=harness.getObjects('TouchButton').filter(b=>Number(harness.getObjectVariable(b.id,'Active')?.value)===1);
    harness.assert(buttons.every(b=>b.x+b.width<=map.x || b.y>=map.y+map.height || b.y+b.height<=map.y),`Radar does not overlap active touch buttons at ${width}x${height}`);
  }
  harness.setSceneVariable('Mode',2); await harness.stepFrames(2);
  harness.assert(obj('RadarMap').hidden,'Radar hides while a menu is open');
  harness.setSceneVariable('Mode',0); await harness.stepFrames(2);
  harness.assert(!obj('RadarMap').hidden,'Radar returns on resuming exploration');
  harness.watch('Player3D'); harness.watch('RadarPlayer');
} finally {
  game.setGameResolutionSize(original[0],original[1]);
  harness.releaseAllInputs();
}
