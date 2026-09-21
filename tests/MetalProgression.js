// A bounded playthrough of mining -> claims -> smelting -> upgraded combat.
const n=name=>Number(harness.getSceneVariable(name)?.value);
async function tap(key) {
  harness.setKeyPressed(key,true); await harness.stepFrames(1);
  harness.setKeyPressed(key,false); await harness.stepFrames(1);
}
async function move(x,y) {
  harness.setObjectPosition(harness.getObjects('Player3D')[0].id,x,y,0);
  await harness.stepFrames(3);
}
async function click(name) {
  const b=harness.getObjects(name)[0];
  harness.setMousePosition(b.centerX,b.centerY,b.layer);
  harness.setMouseButtonPressed(true,'left'); await harness.stepFrames(1);
  harness.setMouseButtonPressed(false,'left'); await harness.stepFrames(2);
}
async function claim() {
  await tap('j'); await click('ClaimQuest'); await tap('j');
}
async function mine(seam) {
  await move(seam.x,seam.y);
  harness.setKeyPressed('e',true); await harness.stepFrames(113);
  harness.setKeyPressed('e',false); await harness.stepFrames(2);
}
try {
  await harness.goToScene('Game'); harness.setSceneVariable('TouchMode', 0); await harness.stepFrames(3);
  harness.setSceneVariable('SaveStorage','JurassicWorldTests_MetalProgression');
  harness.setSceneVariable('Invulnerable',9999);
  // Start at the mining chapter, with ordinary construction supplies prepared.
  harness.setSceneVariable('QuestStage',7);
  harness.setSceneVariable('Wood',60); harness.setSceneVariable('Stone',30);
  const seams=harness.getObjects('MetalDeposit');
  for(const seam of seams.slice(0,3)) await mine(seam);
  harness.assert(n('MetalOre')===6 && n('GatherMetal')===6 && n('QuestReady')===1,
    'Three native hold-E extractions supply six ore and complete the expedition objective');
  harness.assert(Number(harness.getObjectVariable(seams[0].id,'Cooldown')?.value)>170,
    'Mined seams remain depleted instead of immediately rewarding another harvest');
  await claim(); harness.assert(n('QuestStage')===8,'Claiming the expedition unlocks the forge objective');
  await move(-1020,440);
  const wood=n('Wood'),stone=n('Stone'); await tap('z');
  harness.assert(n('ForgeBuilt')===1 && n('Wood')===wood-8 && n('Stone')===stone-12,
    'The first forge interaction repairs it for the displayed material cost');
  for(let i=0;i<3;i++) {
    await tap('z'); const raw=n('MetalOre'),fuel=n('Wood'); await tap('z');
    harness.assert(n('MetalOre')===raw && n('Wood')===fuel,'An occupied forge cannot double-charge ore or wood');
    await harness.stepFrames(605);
  }
  harness.assert(n('MetalIngot')===3 && n('SmeltedMetal')===3 && n('MetalOre')===0 && n('QuestReady')===1,
    'Three timed smelts turn six ore into three ingots and complete the forge goal');
  await claim(); harness.assert(n('QuestStage')===9,'Forge completion unlocks the metal tools objective');
  await tap('u');
  harness.assert(n('MetalTools')===1 && n('MetalIngot')===0 && n('Spear')>=1,
    'Crafting the upgrade spends three ingots and equips stronger tools');
  const remaining=n('Wood'); await tap('u');
  harness.assert(n('Wood')===remaining,'The permanent upgrade cannot be purchased twice');
  await claim(); harness.assert(n('QuestStage')===10,'Metal tools unlock the hunting objective');
  const before=n('MetalOre'); await mine(seams[3]);
  harness.assert(n('MetalOre')===before+4,'Metal tools double ore yield from a new seam');
  const raptor=harness.getObjects('Raptor')[0];
  harness.setObjectPosition(raptor.id,0,1300,0);
  harness.setObjectVariable(raptor.id,'HP',120);
  await move(0,1540);
  await tap('k');
  harness.assert(Number(harness.getObjectVariable(raptor.id,'HP')?.value)===65,
    'A real upgraded spear hit deals 55 damage');
  for(let i=0;i<2;i++){await harness.stepFrames(42);await tap('k');}
  await harness.stepFrames(2); // Allow the HUD to observe the completed combat update.
  harness.assert(n('Kills')===1 && n('QuestReady')===1,'A completed hunt advances the new objective counter');
  await claim();
  harness.assert(n('QuestStage')===11 && n('QuestReady')===0,
    'The final main objective opens a fresh, uncompleted expedition contract');
} finally { harness.releaseAllInputs(); }
