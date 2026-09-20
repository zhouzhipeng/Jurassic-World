// With adaptWidth active the host determines aspect ratio; vary logical density.
// Portrait and landscape aspect ratios are additionally checked by resizing the preview window.
const n=name=>Number(harness.getSceneVariable(name)?.value);
const val=(o,k)=>Number(harness.getObjectVariable(o.id,k)?.value);
async function tap(command) {
  const b=harness.getObjects('TouchButton').find(o=>val(o,'Active')===1&&val(o,'Command')===command);
  if(!b) throw new Error(`Missing responsive button ${command}`);
  harness.touchStart(81,b.centerX,b.centerY,'Touch');await harness.stepFrames(1);
  harness.touchEnd(81);await harness.stepFrames(3);
}
function contained(objects,w,h){return objects.every(b=>b.x>=0&&b.y>=0&&b.x+b.width<=w+1&&b.y+b.height<=h+1);}
try {
  await harness.goToScene('Game');await harness.stepFrames(3);
  harness.setSceneVariable('Invulnerable',9999);
  for(const requestedHeight of [900,650,1200]){
    harness.getRuntimeGame().setGameResolutionSize(1600,requestedHeight);await harness.stepFrames(4);
    const w=harness.getGameResolutionWidth(),h=harness.getGameResolutionHeight();
    const visible=()=>harness.getObjects('TouchButton').filter(o=>val(o,'Active')===1);
    harness.assert(n('TouchWidth')===w&&n('TouchHeight')===h&&contained(visible(),w,h),`All play controls fit ${w} x ${h}`);
    const stick=harness.getObjects('TouchStick')[0];
    harness.assert(contained([stick],w,h)&&visible().every(o=>o.width>=44&&o.height>=44),`Joystick and touch targets remain usable at ${w} x ${h}`);
    await tap(3);
    const cards=visible().filter(o=>val(o,'Slot')>=100);
    harness.assert(cards.length===8&&contained(visible(),w,h),`All eight building cards and the close button fit ${w} x ${h}`);
    harness.assert(cards.every((a,i)=>cards.slice(i+1).every(b=>a.x+a.width<=b.x||b.x+b.width<=a.x||a.y+a.height<=b.y||b.y+b.height<=a.y)),`Cards do not overlap at ${w} x ${h}`);
    await tap(210);
    const building=visible();
    harness.assert(n('BuildMode')===1&&contained(building,w,h)&&building.every((a,i)=>building.slice(i+1).every(b=>a.x+a.width<=b.x||b.x+b.width<=a.x||a.y+a.height<=b.y||b.y+b.height<=a.y)),`Building controls fit without overlap at ${w} x ${h}`);
    await tap(10);
  }
} finally { harness.releaseAllInputs(); harness.getRuntimeGame().setGameResolutionSize(1600,900); }
