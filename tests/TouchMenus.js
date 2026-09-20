// Build, craft, claim, navigate, save/load and respawn using only real touch input.
const n=name=>Number(harness.getSceneVariable(name)?.value);
const val=(o,k)=>Number(harness.getObjectVariable(o.id,k)?.value);
async function tap(command) {
  const b=harness.getObjects('TouchButton').find(o=>val(o,'Active')===1&&val(o,'Command')===command);
  if(!b) throw new Error(`Missing command ${command}; mode=${n('Mode')}, panel=${n('TouchPanel')}`);
  harness.touchStart(71,b.centerX,b.centerY,'Touch'); await harness.stepFrames(1);
  harness.touchEnd(71); await harness.stepFrames(3);
}
try {
  await harness.goToScene('Game'); await harness.stepFrames(3);
  harness.setSceneVariable('SaveStorage','JurassicWorldTests_TouchMenus');
  harness.setSceneVariable('Invulnerable',9999);
  for(const k of ['Wood','Stone','Fiber']) harness.setSceneVariable(k,100);
  harness.setObjectPosition(harness.getObjects('Player3D')[0].id,-1780,-135,0); await harness.stepFrames(3);
  await tap(3); await tap(210);
  harness.assert(n('BuildMode')===1&&n('BuildKind')===10&&n('BuildValid')===1,'A touch building card enters placement at a valid ground socket');
  await tap(20); harness.assert(n('BuildAngle')===90,'The touch rotate button rotates a preview by 90 degrees');
  await tap(21);
  harness.assert(harness.getObjects('PartFoundation').length===1&&n('Wood')===94,'Touch placement creates one foundation and charges its real cost');
  await tap(21); harness.assert(harness.getObjects('PartFoundation').length===1&&n('Wood')===94,'Invalid repeat placement cannot duplicate a building or charge materials');
  await tap(11); harness.assert(n('BuildLevel')===1,'Upper-floor construction is accessible without Page Up');
  await tap(12); await tap(10);
  harness.setSceneVariable('QuestStage',2); await harness.stepFrames(2);
  await tap(2); const spears=n('Spear'); await tap(113);
  harness.assert(n('Spear')===spears+1&&n('CraftedSpears')===1,'A recipe card crafts a spear and advances the real quest counter');
  await tap(8); await tap(4); await tap(130);
  harness.assert(n('QuestStage')===3,'The quest card claims a completed goal using touch');
  await tap(8); await tap(1); await tap(103); await tap(151);
  harness.assert(n('NavMode')===1&&n('Mode')===0,'Destination cards set water navigation and return to exploration');
  await tap(1); await tap(101); const savedWood=n('Wood');
  await tap(2); await tap(114); await tap(8); await tap(1); await tap(102); await harness.stepFrames(4);
  harness.assert(n('Wood')===savedWood&&harness.getObjects('PartFoundation').length===1,'Touch save/load restores supplies and the placed building');
  // Arrange lethal exposure; the native death event, then touch respawn, must process it.
  harness.setSceneVariable('Health',0); harness.setSceneVariable('Invulnerable',0); await harness.stepFrames(3);
  harness.assert(n('Dead')===1,'The death state offers a touch respawn flow');
  await tap(199);
  harness.assert(n('Dead')===0&&n('Mode')===0&&n('Health')===100,'The respawn card returns the player to camp without Enter');
} finally { harness.releaseAllInputs(); }
