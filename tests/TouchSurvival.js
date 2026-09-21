// One-tap contextual actions reuse the real resource, food, water and riding systems.
const n = name => Number(harness.getSceneVariable(name)?.value);
const val = (o,key) => Number(harness.getObjectVariable(o.id,key)?.value);
const ov = (name,key) => Number(harness.getObjectVariable(name,key)?.value);
async function tap(command) {
  const b = harness.getObjects('TouchButton').find(o => val(o,'Active')===1 && val(o,'Command')===command);
  if (!b) throw new Error(`No touch action ${command}, context=${n('TouchContext')}, mode=${n('Mode')}`);
  harness.touchStart(61,b.centerX,b.centerY,'Touch'); await harness.stepFrames(1);
  harness.touchEnd(61); await harness.stepFrames(3);
}
async function move(x,y) { harness.setObjectPosition(harness.getObjects('Player3D')[0].id,x,y,0); await harness.stepFrames(4); }
try {
  await harness.goToScene('Game'); await harness.stepFrames(3);
  harness.setSceneVariable('Invulnerable',9999);
  await move(430,100);
  const berries=n('Berries'); await tap(301); await harness.stepFrames(55);
  harness.assert(n('Berries')===berries+3 && n('TouchAutoHarvest')===0, 'One tap harvests exactly one bush and stops after completion');
  const tree=harness.getObjects('WoodSapling')[0]; await move(tree.x,tree.y);
  const wood=n('Wood'); await tap(301); await harness.stepFrames(95);
  harness.assert(n('Wood')===wood+4 && n('SelectedHotbar')===1, 'Tree harvesting automatically selects the axe and completes its three hits');
  await move(-800,250); const raw=n('Meat'), fuelWood=n('Wood');
  await tap(303); await harness.stepFrames(490);
  harness.assert(n('Wood')===fuelWood-1 && n('Meat')===raw-1 && n('CookedMeat')===1, 'One fire interaction adds fuel once and cooks one portion');
  harness.setSceneVariable('Hunger',40); await tap(2); await tap(411); await tap(111);
  harness.assert(n('CookedMeat')===0 && n('Hunger')>69, 'Food can be eaten from the touch backpack without a hotkey');
  await move(-1120,300); const hide=n('Hide'); await tap(304); await tap(120);
  harness.assert(n('Canteen')===1 && n('Hide')===hide-2, 'The contextual workshop crafts a canteen using the native recipe');
  await move(-220,850); harness.setSceneVariable('Water',30); await tap(302);
  harness.assert(n('Water')>99 && n('CanteenCharges')===3, 'The water action drinks and fills the canteen together');
  await move(0,400); harness.setSceneVariable('Water',30); await tap(5);
  harness.assert(n('Water')>69 && n('CanteenCharges')===2, 'Quick supplies choose the canteen when water is low');
  harness.setSceneVariable('Trust',100); const dino=harness.getObjects('Dinosaur3D')[0];
  await move(dino.x,dino.y+150); await tap(306);
  harness.assert(n('Riding')===1, 'The same contextual button mounts a tamed dinosaur');
  await tap(307); harness.assert(n('Riding')===0, 'A second contextual tap safely dismounts');
  const bush=harness.getObjects('BerryBush').find(o=>val(o,'Cooldown')<=0); await move(bush.x,bush.y);
  const count=n('Berries'); await tap(301); await harness.stepFrames(8);
  harness.touchStart(63,n('TouchJoyX')+n('TouchRadius'),n('TouchJoyY'),'Touch'); await harness.stepFrames(8);
  harness.touchEnd(63); await harness.stepFrames(55);
  harness.assert(n('TouchAutoHarvest')===0 && n('Berries')===count, 'Moving cancels an unfinished one-tap harvest');
} finally { harness.releaseAllInputs(); }
