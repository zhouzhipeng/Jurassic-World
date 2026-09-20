const value = name => Number(harness.getSceneVariable(name)?.value);
const storage = 'JurassicWorldGameplayTests_Weather';
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
  await tap('F6');
  await tap('F6');
  await harness.stepFrames(60);
  await tap('Escape');
  const saved = ['WeatherType', 'WeatherClock', 'WeatherDuration'].map(value);
  await click('Save');
  harness.assert(value('SaveFlag') === 1, 'The pause menu saves weather to an isolated test slot');
  await harness.goToScene('Game');
  await harness.stepFrames(2);
  harness.setSceneVariable('SaveStorage', storage);
  harness.assert(value('WeatherType') === 0, 'A new scene starts independently of the stored weather');
  await tap('Escape');
  await click('Load');
  harness.assert(['WeatherType', 'WeatherClock', 'WeatherDuration'].every((name, i) => value(name) === saved[i]),
    'Load restores weather type, exact elapsed time and spell duration');
  harness.assert(harness.getObjects('WeatherStatus')[0]?.text?.includes('降雨') === true,
    'The restored weather name reaches the HUD while paused');
  await tap('Escape');
  await harness.stepFrames(60);
  harness.assert(value('WeatherClock') > saved[1] && value('WeatherRain') > 0.2,
    'Resuming continues the saved weather clock and fades into its rain preset');
} finally {
  harness.releaseAllInputs();
}
