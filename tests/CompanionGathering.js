const n = name => Number(harness.getSceneVariable(name)?.value);
const bond = () => Number(harness.getObjectVariable('Triceratops', 'Bond')?.value);
async function tap(key) {
  harness.setKeyPressed(key,true); await harness.stepFrames(1);
  harness.setKeyPressed(key,false); await harness.stepFrames(1);
}
async function approach() {
  const trike=harness.getObjects('Triceratops')[0];
  harness.setObjectPosition(harness.getObjects('Player3D')[0].id,trike.x+310,trike.y,0);
  await harness.stepFrames(2);
}
try {
  await harness.goToScene('Game'); await harness.stepFrames(3);
  harness.setSceneVariable('SaveStorage','JurassicWorldTests_Companion');
  harness.setSceneVariable('Berries',30);
  await approach(); await tap('t');
  harness.assert(bond()===20 && n('Berries')===27, 'First tame feeding spends three berries for twenty trust');
  await tap('t');
  harness.assert(bond()===20 && n('Berries')===27, 'The four-second feeding interval prevents repeated charges');
  for(let i=0;i<4;i++) {
    await harness.stepFrames(245); await approach(); await tap('t');
  }
  harness.assert(bond()===100 && n('Berries')===15 && n('CompanionTamed')===1,
    'Five real feedings tame the herbivore and unlock companion utility');
  await tap('h');
  const stay=harness.getObjects('Triceratops')[0]; await harness.stepFrames(150);
  const stayed=harness.getObjects('Triceratops')[0];
  harness.assert(Math.hypot(stayed.x-stay.x,stayed.y-stay.y)<1, 'The stay whistle holds the tamed animal in place');
  await tap('h');
  const player=harness.getObjects('Player3D')[0];
  harness.setObjectPosition(player.id,stayed.x+1100,stayed.y,0);
  await harness.stepFrames(150);
  const followed=harness.getObjects('Triceratops')[0];
  harness.assert(followed.x>stayed.x+400, 'The follow whistle brings the companion toward a distant player');
  await tap('h');
  const bush=harness.getObjects('BerryBush').find(x=>x.y>0 && Math.abs(x.x)<1000);
  if(!bush) throw new Error('The fixture needs an existing southern berry bush');
  harness.setObjectPosition(followed.id,bush.x-550,bush.y,0);
  harness.setObjectPosition(player.id,bush.x,bush.y,0);
  await harness.stepFrames(3);
  harness.assert(n('CompanionBonus')===1, 'A nearby tamed, stationary companion enables the gathering bonus');
  const berries=n('Berries'), gathered=n('GatherBerries');
  harness.setKeyPressed('e',true); await harness.stepFrames(55);
  harness.setKeyPressed('e',false); await harness.stepFrames(2);
  harness.assert(n('Berries')===berries+6 && n('GatherBerries')===gathered+6,
    'A real berry harvest doubles both backpack yield and quest credit');
} finally { harness.releaseAllInputs(); }
