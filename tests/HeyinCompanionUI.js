const obj=n=>harness.getObjects(n)[0];
const scene=k=>Number(harness.getSceneVariable(k)?.value);
const game=harness.getRuntimeGame();const original=[game.getGameResolutionWidth(),game.getGameResolutionHeight()];
async function tap(k){harness.setKeyPressed(k,true);await harness.stepFrames(1);harness.setKeyPressed(k,false);await harness.stepFrames(2);}
try {
 await harness.goToScene('Game');await harness.stepFrames(3);
 harness.setObjectPosition(obj('Player3D').id,470,900,0);harness.setSceneVariable('CameraYaw',145);harness.setSceneVariable('CameraDistance',650);await harness.stepFrames(30);
 for(const size of [[1600,900],[568,320]]){
  game.setGameResolutionSize(size[0],size[1]);await harness.stepFrames(5);
  harness.assert(!obj('HeyinVitalsText').hidden&&obj('HeyinVitalsText').x>=0&&obj('HeyinVitalsText').x+206<size[0],`Companion bars and values stay on screen at ${size}`);
  harness.assert(obj('HeyinStory').x+obj('HeyinStory').width<obj('HeyinVitalsText').x||obj('HeyinStory').y>obj('HeyinVitalsText').y+100,`Quest and companion status do not overlap at ${size}`);
  const b=obj('HeyinTalkButton');harness.touchStart(81,b.x+30,b.y+10,b.layer);await harness.stepFrames(1);harness.touchEnd(81);await harness.stepFrames(3);
  harness.assert(scene('Mode')===9&&obj('HeyinMenuText').y+obj('HeyinMenuText').height<obj('HeyinOption1').y,`Touch opens a readable conversation at ${size}`);
  await tap('Num3');
  harness.assert(obj('HeyinOption3').x+obj('HeyinOption3').width<size[0]-10&&obj('HeyinOption5').y+obj('HeyinOption5').height<size[1]-5,`Family choices fit the viewport at ${size}`);
  await tap('Escape');harness.assert(scene('Mode')===0&&obj('HeyinOption3').hidden,`Escape closes only the conversation at ${size}`);
 }
} finally {game.setGameResolutionSize(original[0],original[1]);harness.releaseAllInputs();}
