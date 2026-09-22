const n=k=>Number(['HeyinStay','HeyinEnergy','HeyinResting'].includes(k)?harness.getObjectVariable('Heyin',k.slice(5))?.value:harness.getSceneVariable(k)?.value);
const obj=k=>harness.getObjects(k)[0];
async function tap(k){harness.setKeyPressed(k,true);await harness.stepFrames(1);harness.setKeyPressed(k,false);await harness.stepFrames(2);}
async function move(x,y){harness.setObjectPosition(obj('Player3D').id,x,y,0);await harness.stepFrames(3);}
try {
 await harness.goToScene('Game');harness.setSceneVariable('TouchMode',0);await harness.stepFrames(3);
 harness.watch('Heyin');harness.watch('HeyinStory');
 harness.assert(Math.abs(obj('Heyin').depth-192)<1,'Companion uses the adult 192-unit height, close to the 202-unit survivor');
 await move(450,900);harness.setSceneVariable('Fiber',0);harness.setSceneVariable('Berries',0);
 await tap('g');harness.assert(n('HeyinStage')===1,'Approach discovers the injured woman; missing supplies cannot complete rescue');
 harness.setSceneVariable('Fiber',10);harness.setSceneVariable('Berries',10);
 const r=obj('Raptor');harness.setObjectPosition(r.id,450,1000,0);await harness.stepFrames(2);await tap('g');
 harness.assert(n('HeyinStage')===1 && n('Fiber')===10 && n('Berries')===10,'A nearby living predator blocks rescue without charging materials');
 harness.setObjectPosition(r.id,-700,-2150,0);await harness.stepFrames(2);await tap('g');
 harness.assert(n('HeyinStage')===2 && n('Fiber')===6 && n('Berries')===7,'Safe rescue consumes exactly four fiber and three berries');
 await tap('g');const stay=obj('Heyin');await move(900,900);await harness.stepFrames(60);
 harness.assert(n('HeyinStay')===1 && obj('Heyin').x===stay.x && obj('Heyin').y===stay.y,'G switches to waiting without repeating the rescue cost');
 await move(stay.x+100,stay.y);await tap('g');await move(900,900);await harness.stepFrames(45);
 harness.assert(obj('Heyin').x>stay.x+90 && obj('Heyin').x<stay.x+140 && obj('Heyin').children.Body[0].animation==='Walk','Follow resumes with the actual GLB walk animation');
 const walking=obj('Heyin');const bearing=Math.atan2(obj('Player3D').y-walking.y,obj('Player3D').x-walking.x)*180/Math.PI;
 harness.assert(Math.abs(((walking.angle-bearing+90+540)%360)-180)<2,'The model uses the forward heading confirmed by the game side-view preview');
 await tap('Escape');const paused=obj('Heyin');const energy=n('HeyinEnergy');await harness.stepFrames(90);
 harness.assert(obj('Heyin').x===paused.x && n('HeyinEnergy')===energy,'Pause freezes companion movement and fatigue');await tap('Escape');
 // Reachable ground-plane waypoints: only move the player; the NPC must walk.
 for(const [x,y] of [[200,950],[-300,850],[-650,550],[-650,350]]){await move(x,y);await harness.stepFrames(270);}
 harness.assert(n('HeyinStage')===3,'The NPC physically reaches the camp before the escort chapter completes');
 harness.setObjectVariable('Heyin','Energy',4);await harness.stepFrames(3);
 harness.assert(n('HeyinResting')===1 && obj('Heyin').children.Body[0].animation==='Rest','Low energy triggers the authored rest pose');
 await harness.stepFrames(760);harness.assert(n('HeyinResting')===0,'Rest automatically recovers with a separate resume threshold');
 // Pass north of the four jump platforms; a follower should not cross them.
 for(const [x,y] of [[0,0],[650,-50],[1350,-50],[1580,680]]){await move(x,y);await harness.stepFrames(350);}
 await tap('g');harness.assert(n('HeyinStage')===4,'Arriving together and interacting identifies the maternal knot');
 const f=n('Fiber'),b=n('Berries');await tap('g');harness.assert(n('HeyinStage')===4&&n('Fiber')===f&&n('Berries')===b,'Repeated conversation cannot duplicate rescue costs or clue progress');
 // Arrange a blocked approach after verifying the entire quest by input.
 harness.setObjectVariable('Heyin','Stay',0);harness.setObjectPosition(obj('Heyin').id,-450,-700,0);await move(-900,-700);await harness.stepFrames(80);
 harness.assert(obj('Heyin').x>=-556,'The follower stops outside the static house rather than walking through its wall');
} finally {harness.releaseAllInputs();}
