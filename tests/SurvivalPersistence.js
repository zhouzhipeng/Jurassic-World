const n=name=>Number(harness.getSceneVariable(name)?.value);
async function tap(key){harness.setKeyPressed(key,true);await harness.stepFrames(1);harness.setKeyPressed(key,false);await harness.stepFrames(1);}
async function click(name){const o=harness.getObjects(name)[0];harness.setMousePosition(o.centerX,o.centerY,o.layer);harness.setMouseButtonPressed(true,'left');await harness.stepFrames(1);harness.setMouseButtonPressed(false,'left');await harness.stepFrames(2);}
async function move(x,y){harness.setObjectPosition(harness.getObjects('Player3D')[0].id,x,y,0);await harness.stepFrames(3);}
function fires(){return ['BuiltCampfire','CampHearth'].flatMap(name=>harness.getObjects(name).map(o=>({name,x:o.x,y:o.y,values:['Slot','Fuel','Cooking','CookTime'].map(k=>harness.getObjectVariable(o.id,k)?.value)})));}
function companion(){const o=harness.getObjects('Triceratops')[0];return {x:o.x,y:o.y,values:['Bond','FeedWait','Command','HP'].map(k=>harness.getObjectVariable(o.id,k)?.value)};}
const storage='JurassicWorldTests_SurvivalPersistence';
try {
  await harness.goToScene('Game');await harness.stepFrames(3);
  harness.setSceneVariable('SaveStorage',storage);
  for(const k of ['Wood','Stone','Fiber'])harness.setSceneVariable(k,100);
  await move(0,750);await tap('b');await tap('Num8');
  harness.assert(n('BuildValid')===1,'The persistence fixture can place a real campfire');await tap('Return');await tap('b');
  const built=harness.getObjects('BuiltCampfire')[0];if(!built)throw new Error('Campfire placement failed');
  await move(built.x+160,built.y);await tap('v');await tap('v');await tap('c');
  await move(-650,300);await tap('v');await tap('c');
  const trike=harness.getObjects('Triceratops')[0];
  harness.setObjectVariable(trike.id,'Bond',60);harness.setObjectVariable(trike.id,'FeedWait',2);
  harness.setObjectVariable(trike.id,'Command',1);harness.setObjectPosition(trike.id,-1650,1440,0);
  const seam=harness.getObjects('MetalDeposit')[0];harness.setObjectVariable(seam.id,'Cooldown',137);
  for(const [k,v] of Object.entries({BodyTemp:35.4,Wetness:61,Canteen:1,CanteenCharges:2,MetalOre:5,MetalIngot:2,ForgeBuilt:1,ForgeBusy:1,ForgeTime:6,CookedMeat:3,MealsCooked:8,QuestStage:8}))harness.setSceneVariable(k,v);
  await tap('Escape');
  const names=['BodyTemp','Wetness','Canteen','CanteenCharges','MetalOre','MetalIngot','ForgeBuilt','ForgeBusy','ForgeTime','CookedMeat','MealsCooked','QuestStage','Health'];
  const values=names.map(n),savedFires=JSON.stringify(fires()),savedTrike=JSON.stringify(companion());
  const savedCooldown=Number(harness.getObjectVariable(seam.id,'Cooldown')?.value),position=harness.getObjects('Player3D')[0];
  await click('Save');harness.assert(n('SaveFlag')===1,'The pause menu stores survival data in an isolated slot');
  await harness.goToScene('Game');await harness.stepFrames(3);harness.setSceneVariable('SaveStorage',storage);
  harness.assert(n('Canteen')===0 && n('MetalOre')===0 && n('ForgeBuilt')===0,'A fresh scene starts with fresh survival defaults');
  await tap('Escape');await click('Load');
  harness.assert(names.every((name,i)=>n(name)===values[i]),'Loading restores exact supplies, environment, forge queue and chapter progress');
  harness.assert(JSON.stringify(fires())===savedFires,'Both placed and permanent fires restore their own fuel and cooking jobs');
  harness.assert(JSON.stringify(companion())===savedTrike,'A partly tamed companion retains its own trust, feeding wait, command and position');
  const restored=harness.getObjects('MetalDeposit').find(o=>Number(harness.getObjectVariable(o.id,'SiteId')?.value)===0);
  harness.assert(Number(harness.getObjectVariable(restored.id,'Cooldown')?.value)===savedCooldown,'The depleted ore seam retains its cooldown by site identity');
  const loaded=harness.getObjects('Player3D')[0];
  harness.assert(loaded.x===position.x && loaded.y===position.y,'Loading returns the player to the saved location');
  await harness.stepFrames(40);
  harness.assert(JSON.stringify(fires())===savedFires && n('ForgeTime')===values[names.indexOf('ForgeTime')],
    'Restored production remains frozen while the menu stays open');
  await tap('Escape');await harness.stepFrames(620);
  harness.assert(n('CookedMeat')===values[names.indexOf('CookedMeat')]+2 && n('MetalIngot')===values[names.indexOf('MetalIngot')]+1,
    'Resuming finishes both retained meals and the ingot exactly once');
}finally{harness.releaseAllInputs();}
