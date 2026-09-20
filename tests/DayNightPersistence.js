const value = name => Number(harness.getSceneVariable(name)?.value);
const storage = 'JurassicWorldGameplayTests_DayNight';
async function tap(key) {
  harness.setKeyPressed(key, true);
  await harness.stepFrames(1);
  harness.setKeyPressed(key, false);
  await harness.stepFrames(1);
}
async function click(name) {
  const object = harness.getObjects(name)[0];
  harness.setMousePosition(object.centerX, object.centerY, object.layer);
  harness.setMouseButtonPressed(true, 'left');
  await harness.stepFrames(1);
  harness.setMouseButtonPressed(false, 'left');
  await harness.stepFrames(2);
}
try {
  await harness.goToScene('Game');
  await harness.stepFrames(2);
  harness.setSceneVariable('SaveStorage', storage);
  harness.setSceneVariable('WorldDay', 17);
  harness.setSceneVariable('WorldMinutes', 1337.5);
  harness.setSceneVariable('DayLengthSeconds', 900);
  await tap('F6');
  await tap('F6');
  await harness.stepFrames(60);
  await tap('Escape');
  const names = ['WorldDay', 'WorldMinutes', 'DayLengthSeconds', 'WeatherType', 'WeatherClock', 'WeatherDuration'];
  const saved = names.map(value);
  await click('Save');
  harness.assert(value('SaveFlag') === 1, 'The pause menu saves time and weather into an isolated slot');

  await harness.goToScene('Game');
  await harness.stepFrames(2);
  harness.setSceneVariable('SaveStorage', storage);
  const morningSky = harness.getCurrentRuntimeScene().getBackgroundColor();
  harness.assert(value('WorldDay') === 1 && value('Daylight') === 1 && value('DayLengthSeconds') === 720,
    'Starting a new scene uses fresh morning defaults until the player loads');
  await tap('Escape');
  await click('Load');
  harness.assert(names.every((name, i) => value(name) === saved[i]),
    'Load restores the exact day, fractional minutes, day speed and weather state together');
  const display = String(harness.getSceneVariable('TimeDisplay')?.value);
  harness.assert(value('Daylight') === 0
    && harness.getCurrentRuntimeScene().getBackgroundColor() !== morningSky
    && harness.getObjects('TimeStatus')[0]?.text?.includes('第 17 天') === true
    && harness.getObjects('WorldStatusText')[0]?.text?.includes(display) === true,
    'Loaded night lighting and both clocks update immediately while paused');
  await harness.stepFrames(30);
  harness.assert(value('WorldMinutes') === saved[1], 'A loaded clock stays frozen until gameplay resumes');
  await tap('Escape');
  const resumed = value('WorldMinutes');
  await harness.stepFrames(60, { dtMs: 1000 / 60 });
  harness.assert(Math.abs(value('WorldMinutes') - resumed - 1.6) < 0.001
    && value('WeatherClock') > saved[4] && value('WeatherRain') > 0.2,
    'Resuming uses the saved day speed and continues the saved rainfall');
} finally {
  harness.releaseAllInputs();
}
