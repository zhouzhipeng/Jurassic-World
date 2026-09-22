const obj=n=>harness.getObjects(n)[0];
async function tap(k){harness.setKeyPressed(k,true);await harness.stepFrames(1);harness.setKeyPressed(k,false);await harness.stepFrames(2);}
try {
 await harness.goToScene('Game');await harness.stepFrames(3);
 harness.watch('FireGlow');harness.watch('FireEmber');
 harness.setObjectPosition(obj('Player3D').id,-650,300,0);await harness.stepFrames(3);
 harness.assert(harness.getObjects('FireEmber').length===0,'An unlit hearth emits no embers');
 await tap('v');await harness.stepFrames(12);
 const first=harness.getObjects('FireEmber').slice(-1)[0];const flame=obj('FireGlow');
 harness.assert(!!first&&!flame.hidden,'Real fuel input lights the flame and starts particles');
 await harness.stepFrames(12);
 const risen=harness.getObjects('FireEmber').find(p=>p.id===first.id);
 harness.assert(!!risen&&risen.z>first.z+8&&risen.width<first.width,'A living ember rises and shrinks instead of remaining a static decoration');
 harness.assert(Math.abs(obj('FireGlow').depth-flame.depth)>1,'Flame height changes between frames');
 await tap('Escape');const frozen=obj('FireEmber');const depth=obj('FireGlow').depth;await harness.stepFrames(60);
 harness.assert(obj('FireEmber').z===frozen.z&&obj('FireGlow').depth===depth,'Pause freezes fire motion and particle lifetime');
 await tap('Escape');harness.setObjectVariable(obj('CampHearth').id,'Fuel',0.04);await harness.stepFrames(120);
 harness.assert(obj('FireGlow').hidden&&harness.getObjects('FireEmber').length===0,'Fuel exhaustion hides the flame and all remaining embers expire');
 await tap('v');await harness.stepFrames(12);
 harness.assert(harness.getObjects('FireEmber').length>0,'Adding fuel restarts particles without recreating the scene');
 for(let i=0;i<7;i++){
  harness.spawn('BuiltCampfire',-600+i*90,500,90,'World3D');
  const fire=harness.getObjects('BuiltCampfire').slice(-1)[0];
  harness.setObjectVariable(fire.id,'Slot',900+i);harness.setObjectVariable(fire.id,'Fuel',20);
 }
 await harness.stepFrames(140);
 harness.assert(harness.getObjects('FireGlow').length===8,'Each constructed fire receives its own linked flame');
 const particles=harness.getObjects('FireEmber');
 harness.assert(particles.length>50&&particles.length<=96,'Multiple fires respect the global 96-particle limit');
 harness.assert(particles.some(p=>p.z>150),'Raised constructed fires emit at their own world elevation');
 for(const name of ['CampHearth','BuiltCampfire'])for(const fire of harness.getObjects(name))harness.removeObject(fire.id);
 await harness.stepFrames(120);
 harness.assert(harness.getObjects('FireGlow').length===0&&harness.getObjects('FireEmber').length===0,'Removing fire owners leaves no orphan flames or particles');
} finally {harness.releaseAllInputs();}
