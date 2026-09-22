const n = name => Number(harness.getSceneVariable(name)?.value);
const player = () => harness.getObjects('Player3D')[0];
async function press(key, frames) {
  harness.setKeyPressed(key, true);
  await harness.stepFrames(frames);
  harness.releaseAllInputs();
  await harness.stepFrames(1);
}
try {
  await harness.goToScene('Game');
  await harness.stepFrames(3);
  harness.setSceneVariable('Mode', 0);
  harness.setSceneVariable('Invulnerable', 9999);
  harness.setSceneVariable('CameraYaw', 0);
  // Arrange outside the entrance; all entry and exit displacement uses real input.
  harness.setObjectPosition(player().id, -900, -300, 0);
  harness.watch('Player3D');
  await press('w', 65);
  harness.assert(player().y < -650 && player().z === 30.5,
    `Walk through doorway onto timber floor: y=${player().y}, z=${player().z}`);
  await press('w', 70);
  harness.assert(player().y > -916 && player().y < -900, 'Rear wall stops walking from inside');
  await press('a', 70);
  harness.assert(player().x > -1156 && player().x < -1140, 'Left wall stays solid from inside');
  await press('d', 90);
  harness.assert(player().x < -644 && player().x > -660, 'Right wall stays solid from inside');
  await press('s', 100);
  harness.assert(player().y < -484 && player().y > -500, 'Front wall beside the doorway stays solid');
  // Return to the doorway from inside, then walk out.
  await press('a', 43);
  await press('s', 50);
  await harness.stepFrames(25);
  harness.assert(player().y > -335 && player().z === 0, 'Exit returns naturally to ground height');
  // Check outside approaches to all wall faces.
  for (const [x,y,key,axis,bound,sign] of [
    [-1350,-700,'d','x',-1244,-1], [-450,-700,'a','x',-556,1],
    [-900,-1100,'s','y',-1004,-1], [-1100,-300,'w','y',-396,1],
    [-700,-300,'w','y',-396,1]
  ]) {
    harness.setObjectPosition(player().id,x,y,0);
    harness.setSceneVariable('PlayerFloor',0);
    await press(key,40);
    harness.assert((player()[axis]-bound)*sign >= 0, `Outside wall blocks ${key} from ${x},${y}`);
  }
  harness.setObjectPosition(player().id,-900,-300,0);
  harness.setSceneVariable('PlayerFloor',0);
  await harness.stepFrames(3);
  harness.touchStart(81,n('TouchJoyX'),n('TouchJoyY'),'Touch');
  await harness.stepFrames(1);
  harness.touchMove(81,n('TouchJoyX'),n('TouchJoyY')-n('TouchRadius')*.65,'Touch');
  await harness.stepFrames(100);
  harness.releaseAllInputs();
  await harness.stepFrames(3);
  harness.assert(player().y < -500 && player().y > -916 && player().z === 30.5,
    `Touch joystick enters the same house: y=${player().y}, z=${player().z}`);
  await press('Space',1);
  await harness.stepFrames(65);
  harness.assert(player().z === 30.5 && n('JumpVelocity') === 0, 'Jump lands back on the house floor');
} finally { harness.releaseAllInputs(); }
