const obj=n=>harness.getObjects(n)[0];
const v=(n,k)=>Number(harness.getObjectVariable(n,k)?.value);
const s=k=>Number(harness.getSceneVariable(k)?.value);
async function tap(k){harness.setKeyPressed(k,true);await harness.stepFrames(1);harness.setKeyPressed(k,false);await harness.stepFrames(2);}
async function touch(n){const o=obj(n);harness.touchStart(78,o.x+20,o.y+10,o.layer);await harness.stepFrames(1);harness.touchEnd(78);await harness.stepFrames(2);}
try {
 await harness.goToScene('Game');await harness.stepFrames(3);harness.watch('Heyin');
 harness.assert(v('Heyin','HP')===70&&v('Heyin','Energy')===100&&!obj('HeyinVitals').hidden,'Independent wounded health and stamina panel exists from the start');
 harness.setObjectVariable('Heyin','Grace',0);await harness.stepFrames(60);
 harness.assert(v('Heyin','HP')<70&&v('Heyin','HP')>68,'An untreated wound loses health over time');
 harness.setSceneVariable('Mode',2);const hp=v('Heyin','HP');await harness.stepFrames(30);harness.assert(v('Heyin','HP')===hp,'Menus pause wound deterioration');
 harness.setSceneVariable('Mode',0);harness.setObjectPosition(obj('Player3D').id,470,900,0);await harness.stepFrames(3);
 await touch('HeyinTalkButton');harness.assert(s('Mode')===9&&!obj('HeyinOption1').hidden,'Touch opens the choice conversation');
 harness.setSceneVariable('Fiber',0);harness.setSceneVariable('Berries',0);await tap('Num1');harness.assert(s('HeyinStage')===1&&s('Fiber')===0,'Insufficient rescue supplies cannot rescue or go negative');
 await tap('y');harness.setSceneVariable('Fiber',10);harness.setSceneVariable('Berries',10);await tap('Num1');
 harness.assert(s('HeyinStage')===2&&s('Fiber')===6&&s('Berries')===7,'Choice rescue spends the same supplies as G');
 const rescued=v('Heyin','HP');await harness.stepFrames(60);harness.assert(v('Heyin','HP')===rescued,'Rescue stops the wound permanently');
 await tap('y');harness.setObjectVariable('Heyin','HP',40);harness.setObjectVariable('Heyin','Energy',20);await tap('Num1');
 harness.assert(v('Heyin','HP')===65&&s('Fiber')===4,'Bandaging consumes two fibers and restores 25 HP');
 await touch('HeyinOption2');harness.assert(v('Heyin','Energy')===50&&v('Heyin','HP')===70&&s('Berries')===5,'Touch food choice restores independent stamina and health: '+v('Heyin','Energy')+','+v('Heyin','HP')+','+s('Berries'));
 await tap('Num3');await tap('Num3');harness.assert(v('Heyin','Promise')===1&&v('Heyin','Trust')===15,'Family dialogue commitment changes companion relationship');
 await tap('Num3');await tap('Num3');harness.assert(v('Heyin','Trust')===15,'Repeating the promise cannot farm trust');
 await tap('Num4');harness.assert(v('Heyin','Stay')===1,'Choice can ask the companion to wait');
 await tap('Num5');harness.assert(s('Mode')===0&&obj('HeyinOption1').hidden,'Closing choices resumes exploration');
 for(const n of ['Raptor','Tyrannosaur'])for(const o of harness.getObjects(n))harness.removeObject(o.id);
 harness.setObjectPosition(obj('Player3D').id,1300,900,0);harness.setObjectPosition(obj('Heyin').id,350,900,0);harness.setObjectVariable('Heyin','HP',100);
 const r=harness.spawn('Raptor',350,690,0,'World3D');await harness.stepFrames(3);harness.setObjectVariable(r.id,'Cooldown',0);harness.setObjectVariable(r.id,'AIClock',0);
 const playerHP=s('Health');await harness.stepFrames(60);
 harness.assert(v(r.id,'TargetHeyin')===1&&v('Heyin','HP')===88,'Raptor selects and bites the nearby companion exactly once');
 harness.assert(s('Health')===playerHP,'A bite targeting Heyin does not damage the distant player');
 harness.removeObject(r.id);harness.setObjectVariable('Heyin','Invulnerable',0);const t=harness.spawn('Tyrannosaur',350,540,0,'World3D');await harness.stepFrames(3);harness.setObjectVariable(t.id,'Cooldown',0);await harness.stepFrames(80);
 harness.assert(v(t.id,'TargetHeyin')===1&&v('Heyin','HP')===64,'Tyrannosaur also attacks the companion with its own damage');
 harness.setObjectVariable('Heyin','HP',1);harness.setObjectVariable('Heyin','Invulnerable',0);harness.setObjectVariable(t.id,'Cooldown',0);harness.setObjectVariable(t.id,'State',2);await harness.stepFrames(85);harness.assert(s('Mode')===10&&obj('HeyinMenuText').text.includes('保护同伴失败'),'Companion death displays failure rather than player respawn');
 await harness.stepFrames(310);harness.assert(s('Mode')===0&&s('HeyinStage')===0&&v('Heyin','HP')===70,'Five-second failure countdown restarts the entire scene and story');
harness.setObjectVariable('Heyin','HP',0.01);harness.setObjectVariable('Heyin','Grace',0);await harness.stepFrames(5);harness.assert(s('Mode')===10,'Untreated wound can actually cause companion death');
} finally {harness.releaseAllInputs();}
