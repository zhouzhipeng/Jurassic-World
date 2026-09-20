// Simultaneous fingers drive the existing movement, camera and combat paths.
const n = name => Number(harness.getSceneVariable(name)?.value);
const player = () => harness.getObjects('Player3D')[0];
const val = (o, key) => Number(harness.getObjectVariable(o.id, key)?.value);
const button = command => harness.getObjects('TouchButton').find(o => val(o, 'Active') === 1 && val(o, 'Command') === command);
async function tap(command, id = 90) {
  const b = button(command);
  if (!b) throw new Error(`Missing touch command ${command}; mode=${n('Mode')}`);
  harness.touchStart(id, b.centerX, b.centerY, 'Touch'); await harness.stepFrames(1);
  harness.touchEnd(id); await harness.stepFrames(3);
}
try {
  await harness.goToScene('Game'); await harness.stepFrames(3);
  harness.setSceneVariable('Invulnerable', 9999);
  harness.setObjectPosition(player().id, 0, 400, 0); await harness.stepFrames(3);
  harness.assert(n('TouchMode') === 1 && !harness.getRuntimeLayer('HUD').isVisible(), 'The game starts with the phone HUD and hides the old desktop panels');
  const before = player(), yaw = n('CameraYaw');
  const jx = n('TouchJoyX'), jy = n('TouchJoyY'), r = n('TouchRadius');
  const lx = n('TouchWidth') * .60, ly = n('TouchHeight') * .56;
  const attack = button(7);
  harness.touchStart(31, jx, jy, 'Touch');
  harness.touchStart(32, lx, ly, 'Touch');
  harness.touchStart(33, attack.centerX, attack.centerY, 'Touch');
  await harness.stepFrames(1);
  harness.touchMove(31, jx + r, jy, 'Touch');
  harness.touchMove(32, lx + 100, ly + 20, 'Touch');
  await harness.stepFrames(18);
  harness.assert(Math.hypot(player().x-before.x, player().y-before.y) > 80, 'The joystick moves the player while other fingers remain down');
  harness.assert(Math.abs(n('CameraYaw') - yaw) > 10 && n('TouchMoveId') !== n('TouchLookId'), 'A second finger turns the camera without taking over movement');
  harness.assert(n('CombatCD') > 0 && n('TouchAttack') === 1, 'A third finger attacks through the native combat cooldown');
  harness.touchEnd(31); harness.touchEnd(33); await harness.stepFrames(2);
  const stopped = player();
  harness.touchMove(32, lx + 150, ly + 20, 'Touch'); await harness.stepFrames(8);
  harness.assert(Math.hypot(player().x-stopped.x,player().y-stopped.y)<.1 && n('TouchAttack')===0, 'Releasing movement and attack stops both while the look finger remains active');
  harness.touchEnd(32); await harness.stepFrames(2);
  harness.touchStart(41, jx+r, jy, 'Touch'); await harness.stepFrames(2);
  await tap(1, 42);
  const paused = player(), time = n('WorldMinutes'); await harness.stepFrames(30);
  harness.assert(n('Mode')===2 && n('TouchMoveId')===-999 && n('WorldMinutes')===time && Math.hypot(player().x-paused.x,player().y-paused.y)<.1, 'Opening the menu cancels held gestures and pauses the world');
  await tap(8,43); await harness.stepFrames(10);
  harness.assert(n('Mode')===0 && n('TouchMoveX')===0 && n('TouchMoveId')===-999, 'Closing the menu requires a fresh movement touch');
  harness.touchEnd(41); await harness.stepFrames(2);
  const menu = button(1);
  harness.touchStart(51, menu.centerX, menu.centerY, 'Touch'); await harness.stepFrames(1);
  harness.touchMove(51, menu.x-100, menu.y+150, 'Touch'); await harness.stepFrames(1);
  harness.touchEnd(51); await harness.stepFrames(2);
  harness.assert(n('Mode')===0, 'Dragging off a button cancels the tap instead of opening a menu');
} finally { harness.releaseAllInputs(); }
