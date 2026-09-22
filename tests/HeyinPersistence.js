const n=k=>Number(['HeyinStay','HeyinEnergy','HeyinResting'].includes(k)?harness.getObjectVariable('Heyin',k.slice(5))?.value:harness.getSceneVariable(k)?.value);
const obj=k=>harness.getObjects(k)[0];
async function tap(k){harness.setKeyPressed(k,true);await harness.stepFrames(1);harness.setKeyPressed(k,false);await harness.stepFrames(2);}
async function clickObject(o){harness.setMousePosition(o.centerX,o.centerY,o.layer);harness.setMouseButtonPressed(true,'left');await harness.stepFrames(1);harness.setMouseButtonPressed(false,'left');await harness.stepFrames(3);}
try {
 await harness.goToScene('Game');await harness.stepFrames(3);
 harness.setObjectPosition(obj('Player3D').id,450,900,0);harness.setSceneVariable('Fiber',10);harness.setSceneVariable('Berries',10);await harness.stepFrames(3);
 const button=harness.getObjects('TouchButton').find(o=>Number(harness.getObjectVariable(o.id,'Command')?.value)===311);
 if(!button)throw new Error('No touch rescue button near Heyin');
 harness.touchStart(41,button.centerX,button.centerY,button.layer);await harness.stepFrames(2);harness.touchEnd(41);await harness.stepFrames(3);
 harness.assert(n('HeyinStage')===2&&n('Fiber')===6,'The real touch rescue button uses the same material and story rules');
 await tap('g');harness.assert(n('HeyinStay')===1,'The rescued companion can be left waiting');
 harness.setSceneVariable('TouchMode',0);await harness.stepFrames(3);harness.setSceneVariable('SaveStorage','JurassicWorldTests_HeyinPersistence');
 harness.setObjectVariable('Heyin','HP',43);harness.setObjectVariable('Heyin','Grace',27);harness.setObjectVariable('Heyin','Promise',1);harness.setObjectVariable('Heyin','Trust',15);
 await tap('Escape');const saved=obj('Heyin');const energy=n('HeyinEnergy');await clickObject(obj('Save'));
 harness.assert(n('SaveFlag')===1,'The normal menu saves to an isolated companion test slot');
 await harness.goToScene('Game');harness.setSceneVariable('TouchMode',0);await harness.stepFrames(3);harness.setSceneVariable('SaveStorage','JurassicWorldTests_HeyinPersistence');
 await tap('Escape');await clickObject(obj('Load'));
 harness.assert(n('HeyinStage')===2&&n('HeyinStay')===1&&n('HeyinEnergy')===energy,'A fresh scene restores rescue progress, waiting command and fatigue');
 harness.assert(Number(harness.getObjectVariable('Heyin','HP')?.value)===43&&Number(harness.getObjectVariable('Heyin','Grace')?.value)===27&&Number(harness.getObjectVariable('Heyin','Trust')?.value)===15&&Number(harness.getObjectVariable('Heyin','Promise')?.value)===1,'Save restores health, remaining rescue grace, trust and commitment');
 harness.assert(obj('Heyin').x===saved.x&&obj('Heyin').y===saved.y&&obj('Heyin').angle===saved.angle,'Load restores the companion’s exact saved world position and heading');
 await tap('Escape');await tap('g');await harness.stepFrames(2);
 harness.assert(n('HeyinStay')===0&&n('Fiber')===6,'Loaded companion resumes following without repeating rescue');
}finally{harness.releaseAllInputs();}
