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
    harness.assert(full.length>0 && tiles.length>0 && Math.abs(Math.min(...full.map(h=>h.distance))-Math.min(...tiles.map(h=>h.distance)))<.01,`Spatial query tiles match island at ${x},${y}; full=${full.slice(0,4).map(h=>h.distance)} tiles=${tiles.slice(0,8).map(h=>h.distance)}`);
  }
  for (const name of ['Stegosaur','Raptor','Tyrannosaur','WoodSapling','StoneDeposit','MetalDeposit','SpringWater']) {
    const far=harness.getObjects(name).find(o=>Math.hypot(o.x-player().x,o.y-player().y)>4500);
    harness.assert(!!far,`${name}: outer exploration instance exists`);
    harness.assert(far.hidden,`${name}: distant instance is not drawn`);
    const identity=far.id;
    harness.setObjectPosition(player().id,far.x+350,far.y,0);
    await harness.stepFrames(3);
    const near=harness.getObjects(name).find(o=>o.id===identity);
    harness.assert(!!near && !near.hidden,`${name}: same instance returns when approached`);
    if (['Stegosaur','Raptor','Tyrannosaur'].includes(name)) harness.assert(number(near,'HP')===number(far,'HP'),`${name}: culling preserves health`);
    harness.setObjectPosition(player().id,650,200,0);
    await harness.stepFrames(3);
    harness.assert(harness.getObjects(name).find(o=>o.id===identity)?.hidden,`${name}: leaving hides it again`);
  }
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
