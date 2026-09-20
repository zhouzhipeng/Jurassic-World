const value = name => Number(harness.getSceneVariable(name)?.value);
const text = name => String(harness.getSceneVariable(name)?.value);
const rgb = color => [(color >> 16) & 255, (color >> 8) & 255, color & 255];
async function tap(key) {
  harness.setKeyPressed(key, true);
  await harness.stepFrames(1);
  harness.setKeyPressed(key, false);
  await harness.stepFrames(1);
}
try {
  await harness.goToScene('Game'); harness.setSceneVariable('TouchMode', 0);
  await harness.stepFrames(2);
  harness.setSceneVariable('Invulnerable', 9999);
  harness.assert(value('WorldDay') === 1 && text('TimeDisplay') === '08:00'
    && value('DayLengthSeconds') === 720 && value('Daylight') === 1,
    'A new expedition begins on Day 1 at 08:00 with a 12 minute day');
  harness.assert(harness.getObjects('TimeStatus')[0]?.text?.includes('第 1 天 · 08:00') === true
    && harness.getRuntimeLayer('World3D')?.hasEffect('Moon') === true,
    'The live clock is visible and the native moon light exists');

  let before = value('WorldMinutes');
  await harness.stepFrames(60, { dtMs: 1000 / 60 });
  const at60fps = value('WorldMinutes') - before;
  before = value('WorldMinutes');
  await harness.stepFrames(30, { dtMs: 1000 / 30 });
  harness.assert(Math.abs(at60fps - 2) < 0.001
    && Math.abs(value('WorldMinutes') - before - at60fps) < 0.001,
    'One real second advances two game minutes at both 30 and 60 FPS');

  const daylightSky = harness.getCurrentRuntimeScene().getBackgroundColor();
  await tap('F7');
  harness.assert(value('WorldMinutes') >= 844 && value('WorldMinutes') < 845
    && text('TimePhase') === '白天', 'F7 advances exactly six hours on release');
  await tap('F7');
  harness.assert(text('TimePhase') === '夜晚' && value('Daylight') === 0
    && harness.getCurrentRuntimeScene().getBackgroundColor() !== daylightSky,
    'Advancing into the evening changes the live scene to night');
  await tap('F7');
  harness.assert(value('WorldDay') === 2 && value('WorldMinutes') >= 124
    && value('WorldMinutes') < 125, 'Skipping across midnight increments the calendar once');
  await tap('F7');
  harness.assert(text('TimePhase') === '白天' && value('Daylight') === 1,
    'The next morning restores daylight');

  const skies = [];
  for (const [minutes, phase] of [[240, '夜晚'], [360, '黎明'], [720, '白天'], [1080, '黄昏'], [1260, '夜晚']]) {
    harness.setSceneVariable('WorldMinutes', minutes);
    await harness.stepFrames(1);
    skies.push(rgb(harness.getCurrentRuntimeScene().getBackgroundColor()));
    harness.assert(text('TimePhase') === phase
      && harness.getObjects('TimeStatus')[0]?.text?.includes(phase) === true,
      `The clock and HUD identify ${phase} at ${minutes / 60}:00`);
  }
  harness.assert(skies[0].every((channel, i) => channel < skies[2][i] * 0.25)
    && skies[1][0] > skies[1][1] && skies[3][0] > skies[3][1],
    'Night has a dark blue sky while dawn and dusk have warm sky colors');
  harness.setSceneVariable('WorldMinutes', 1079.5);
  await harness.stepFrames(1);
  let previous = rgb(harness.getCurrentRuntimeScene().getBackgroundColor());
  let largestJump = 0;
  await harness.stepFrames(60, {
    onFrame: () => {
      const current = rgb(harness.getCurrentRuntimeScene().getBackgroundColor());
      largestJump = Math.max(largestJump, ...current.map((channel, i) => Math.abs(channel - previous[i])));
      previous = current;
    }
  });
  harness.assert(largestJump <= 2, 'Sunset colors change smoothly between consecutive frames');

  harness.setSceneVariable('WorldDay', 9);
  harness.setSceneVariable('WorldMinutes', 1439.95);
  await harness.stepFrames(4);
  harness.assert(value('WorldDay') === 10 && value('WorldMinutes') < 0.1
    && text('TimeDisplay') === '00:00', 'Natural midnight preserves fractional minutes and pads the clock');
  // Accelerate the configurable day for a complete natural 24 hour traversal.
  harness.setSceneVariable('DayLengthSeconds', 60);
  const startMinutes = value('WorldMinutes');
  await harness.stepFrames(1800, { dtMs: 1000 / 30 });
  harness.assert(value('WorldDay') === 11 && Math.abs(value('WorldMinutes') - startMinutes) < 0.01,
    'A full automatic cycle advances one day without accumulating a clock offset');
  harness.setSceneVariable('DayLengthSeconds', 720);

  await tap('Escape');
  const paused = value('WorldMinutes');
  const pausedSky = harness.getCurrentRuntimeScene().getBackgroundColor();
  await harness.stepFrames(60);
  await tap('F7');
  harness.assert(value('Mode') === 2 && value('WorldMinutes') === paused
    && harness.getCurrentRuntimeScene().getBackgroundColor() === pausedSky
    && harness.getObjects('WorldStatusText')[0]?.text?.includes(text('TimeDisplay')) === true,
    'Pause freezes the world clock, blocks time skipping and displays the real saved time');
  const photo = harness.getObjects('Photo')[0];
  harness.setMousePosition(photo.centerX, photo.centerY, photo.layer);
  harness.setMouseButtonPressed(true, 'left');
  await harness.stepFrames(1);
  harness.setMouseButtonPressed(false, 'left');
  await harness.stepFrames(30);
  harness.assert(value('Mode') === 5 && value('WorldMinutes') === paused
    && harness.getRuntimeLayer('HUD')?.isVisible() === false,
    'Photo mode keeps the time and lighting frozen and hides the clock');
  await tap('Escape');
  harness.setSceneVariable('Mode', 0);
  await harness.stepFrames(1);
  await tap('F3');
  const reference = value('WorldMinutes');
  await harness.stepFrames(30);
  await tap('F7');
  harness.assert(value('WorldMinutes') === reference && harness.getObjects('TimeStatus')[0]?.hidden === true,
    'Reference mode hides the clock and disables both automatic and manual advancement');
  await tap('F3');
  await harness.stepFrames(2);
  harness.assert(value('WorldMinutes') > reference && harness.getObjects('TimeStatus')[0]?.hidden === false,
    'Returning to gameplay resumes the same clock');

  for (const mode of [1, 3, 4, 6, 7]) {
    harness.setSceneVariable('Mode', mode);
    const frozen = value('WorldMinutes');
    await harness.stepFrames(5);
    await tap('F7');
    harness.assert(value('WorldMinutes') === frozen, `Time remains frozen in menu or death mode ${mode}`);
  }
  harness.assert(['TimePanel', 'TimeStatus'].every(name => harness.getObjects(name).length === 1),
    'Day transitions and menus never duplicate the clock objects');
  harness.watch('TimeStatus');
} finally {
  harness.releaseAllInputs();
}
