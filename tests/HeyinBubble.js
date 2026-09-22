const obj=n=>harness.getObjects(n)[0];
const b=k=>Number(harness.getObjectVariable('HeyinBubble',k)?.value);
const game=harness.getRuntimeGame();const original=[game.getGameResolutionWidth(),game.getGameResolutionHeight()];
try {
 await harness.goToScene('Game');await harness.stepFrames(3);harness.watch('HeyinBubble');harness.watch('HeyinBubbleText');
 harness.assert(obj('HeyinBubbleText').hidden,'No floating dialogue when the player is far away');
 harness.setObjectPosition(obj('Player3D').id,470,900,0);harness.setSceneVariable('CameraYaw',145);harness.setSceneVariable('CameraDistance',650);harness.setSceneVariable('CameraPitch',20);await harness.stepFrames(45);
 harness.assert(!obj('HeyinBubbleText').hidden&&!obj('HeyinBubble').hidden,'Approach shows both dialogue and bubble background');
 harness.assert(obj('HeyinBubbleText').text.includes('家人走散'),'Bubble displays the current story dialogue');
 harness.assert(Number.isFinite(b('HeadX'))&&Number.isFinite(b('HeadY'))&&b('Forward')>0,'Head projection is finite and in front of the world camera');
 harness.assert(obj('HeyinBubbleText').y+obj('HeyinBubbleText').height<b('HeadY'),'Bubble stays above the projected head');
 const x=b('HeadX');harness.setSceneVariable('CameraYaw',215);await harness.stepFrames(45);
 harness.assert(!obj('HeyinBubbleText').hidden&&Math.abs(b('HeadX')-x)>20,'Bubble follows the head when orbiting the camera');
 harness.setSceneVariable('CameraDistance',1250);await harness.stepFrames(45);
 harness.assert(!obj('HeyinBubbleText').hidden&&Number.isFinite(obj('HeyinBubbleText').x),'Zooming out preserves the head anchor');
 harness.setSceneVariable('HeyinMessageTime',0);await harness.stepFrames(3);
 harness.assert(!obj('HeyinBubbleText').hidden&&obj('HeyinBubbleText').text.includes('帮帮我'),'Ongoing Talk has a readable fallback after the timed message ends');
 harness.setSceneVariable('Mode',2);await harness.stepFrames(3);harness.assert(obj('HeyinBubbleText').hidden&&obj('HeyinBubble').hidden,'Menu hides text and background together');
 harness.setSceneVariable('Mode',0);await harness.stepFrames(3);
 harness.setSceneVariable('HeyinMessage','禾音：终于可以歇一歇了。母亲叫岚枝，父亲叫砚山，弟弟叫小岑。我们一起去东边清泉找找他们留下的结绳吧。');harness.setSceneVariable('HeyinMessageTime',12);await harness.stepFrames(3);
 harness.assert(b('H')>80&&obj('HeyinBubbleText').y+obj('HeyinBubbleText').height<=b('Y')+b('H')-10,'Long dialogue grows the rounded panel without overflowing its padding');
 game.setGameResolutionSize(568,320);harness.setSceneVariable('CameraDistance',650);harness.setSceneVariable('CameraYaw',145);await harness.stepFrames(45);
 harness.assert(!obj('HeyinBubbleText').hidden&&b('X')>=12&&b('X')+b('W')<=game.getGameResolutionWidth()-12,'Narrow landscape keeps the full bubble inside screen edges');
 harness.setObjectPosition(obj('Heyin').id,4000,4000,0);await harness.stepFrames(3);harness.assert(obj('HeyinBubbleText').hidden&&obj('HeyinBubble').hidden,'Leaving dialogue range hides both bubble objects');
}finally{game.setGameResolutionSize(original[0],original[1]);harness.releaseAllInputs();}
