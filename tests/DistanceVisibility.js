const number=(o,key)=>Number(o.variables.find(v=>v.name===key)?.value);
try {
  await harness.goToScene('Game');
  await harness.stepFrames(4);
  harness.setSceneVariable('Mode',0);
  harness.setSceneVariable('Invulnerable',9999);
  const player=()=>harness.getObjects('Player3D')[0];
  const scene=harness.getCurrentRuntimeScene();
  const probes=scene.getObjectNamesInGroup('TerrainProbes').flatMap(name=>scene.getObjects(name));
  for (const [x,y] of [[650,200],[1700,-4100],[-3800,-3900],[4250,1800],[-2400,3900]]) {
    const full=gdjs.evtTools.scene3d.raycastObjects(x,y,8000,0,0,-1,scene.getObjects('Island3D'),0,9000,true);
    const tiles=gdjs.evtTools.scene3d.raycastObjects(x,y,8000,0,0,-1,probes,0,9000,true);
    harness.assert(tiles.length>0 && tiles.every(t=>full.some(f=>Math.abs(f.distance-t.distance)<.01)),`Spatial scenery hits belong to the visible island at ${x},${y}`);
  }
  harness.setObjectPosition(player().id,0,-1500,0);
  harness.setSceneVariable('CameraYaw',180);
  harness.setSceneVariable('CameraPitch',12);
  await harness.stepFrames(5);
  const ray=harness.getSceneVariable('CameraFollow')?.children?.find(v=>v.name==='GroundRay');
  const g=Object.fromEntries((ray?.children||[]).map(v=>[v.name,Number(v.value)]));
  harness.assert(g.Distance>0,'Uphill camera exercises grid intersection');
  const meshHits=gdjs.evtTools.scene3d.raycastObjects(g.X,g.Y,g.Z,g.DX,g.DY,g.DZ,scene.getObjects('Island3D'),0,g.Distance+1,true);
  harness.assert(meshHits.some(h=>Math.abs(h.distance-g.Distance)<.05),'Direct height-grid intersection matches the rendered mountain triangles');
  for (const name of ['Stegosaur','Raptor','Tyrannosaur','WoodSapling','StoneDeposit','MetalDeposit','SpringWater']) {
    const away=name==='SpringWater' ? [-5500,5000] : [650,200];
    harness.setObjectPosition(player().id,away[0],away[1],0);
    await harness.stepFrames(3);
    const far=harness.getObjects(name).find(o=>Math.hypot(o.x-player().x,o.y-player().y)>4500);
    harness.assert(!!far,`${name}: outer exploration instance exists`);
    harness.assert(far.hidden,`${name}: distant instance is not drawn`);
    const identity=far.id;
    harness.setObjectPosition(player().id,far.x+350,far.y,0);
    await harness.stepFrames(3);
    const near=harness.getObjects(name).find(o=>o.id===identity);
    harness.assert(!!near && !near.hidden,`${name}: same instance returns when approached`);
    if (['Stegosaur','Raptor','Tyrannosaur'].includes(name)) harness.assert(number(near,'HP')===number(far,'HP'),`${name}: culling preserves health`);
    harness.setObjectPosition(player().id,away[0],away[1],0);
    await harness.stepFrames(3);
    harness.assert(harness.getObjects(name).find(o=>o.id===identity)?.hidden,`${name}: leaving hides it again`);
  }
  harness.setObjectPosition(player().id,650,200,0);
  await harness.stepFrames(3);
  for (const name of ['BerryBush','FiberFern']) {
    const far=harness.getObjects(name).find(o=>Math.hypot(o.x-player().x,o.y-player().y)>6500);
    await harness.stepFrames(12);
    const visible=()=>[...harness.getObjects(name).filter(o=>o.id===far.id),...[1,2].flatMap(l=>harness.getObjects(name+'LOD'+l).filter(o=>number(o,'OwnerId')===far.id))].filter(o=>!o.hidden);
    harness.assert(visible().length===0,`${name}: distant detail levels are all culled`);
    harness.setObjectPosition(player().id,far.x+200,far.y,0);
    await harness.stepFrames(3);
    harness.assert(visible().length===1,`${name}: approaching restores one detail level`);
    harness.setObjectPosition(player().id,650,200,0);
    await harness.stepFrames(12);
  }
} finally { harness.releaseAllInputs(); }
