const value = name => Number(harness.getSceneVariable(name)?.value);
async function tap(key) {
  harness.setKeyPressed(key, true);
  await harness.stepFrames(1);
  harness.setKeyPressed(key, false);
  await harness.stepFrames(1);
}
try {
  await harness.goToScene('Game'); harness.setSceneVariable('TouchMode', 0);
  await harness.stepFrames(2);
  // Keep wildlife away from the test; inputs and weather progression remain real.
  harness.setSceneVariable('Invulnerable', 9999);
  harness.assert(value('WeatherType') === 0 && harness.getObjects('WeatherCanvas').length === 1,
    'A fresh expedition starts clear with exactly one weather canvas');
  const clearSky = harness.getCurrentRuntimeScene().getBackgroundColor();
  await tap('F6');
  harness.assert(value('WeatherType') === 1 && value('WeatherCloud') > 0 && value('WeatherCloud') < 0.1,
    'F6 selects cloud cover and begins a gradual transition');
  await tap('F6');
  await harness.stepFrames(360);
  harness.assert(value('WeatherType') === 2 && value('WeatherRain') > 0.53
    && harness.getCurrentRuntimeScene().getBackgroundColor() !== clearSky,
    'Rain builds up and changes the actual scene background');
  harness.assert(harness.getObjects('WeatherStatus')[0]?.text?.includes('降雨') === true
    && value('WeatherRainVolume') > 20, 'HUD and rain ambience follow the rain state');
  const rainCanvas = harness.getObjects('WeatherCanvas')[0];
  harness.assert(!rainCanvas.hidden && rainCanvas.width > 1400 && rainCanvas.height > 800,
    'Rain strokes cover the viewport using one visible weather canvas');

  await tap('Escape');
  const frozenClock = value('WeatherClock');
  const frozenMotion = value('WeatherMotion');
  const frozenRain = value('WeatherRain');
  await harness.stepFrames(90);
  await tap('F6');
  harness.assert(value('Mode') === 2 && value('WeatherClock') === frozenClock
    && value('WeatherMotion') === frozenMotion && value('WeatherRain') === frozenRain
    && value('WeatherType') === 2 && value('WeatherRainVolume') === 0,
    'Pause freezes weather progression and particles, silences rain and blocks F6');
  const photo = harness.getObjects('Photo')[0];
  harness.setMousePosition(photo.centerX, photo.centerY, photo.layer);
  harness.setMouseButtonPressed(true, 'left');
  await harness.stepFrames(1);
  harness.setMouseButtonPressed(false, 'left');
  await harness.stepFrames(2);
  harness.assert(value('Mode') === 5 && harness.getRuntimeLayer('Weather')?.isVisible() === true
    && harness.getRuntimeLayer('HUD')?.isVisible() === false
    && value('WeatherMotion') === frozenMotion,
    'Photo mode retains the frozen weather image while hiding its HUD');
  await tap('Escape');
  // Existing Escape can return through Pause; set the play state for the next scenario.
  harness.setSceneVariable('Mode', 0);
  await harness.stepFrames(2);

  const player = harness.getObjects('Player3D')[0];
  const roof = harness.spawn('PartCeiling', player.x, player.y, 320, 'World3D');
  harness.setObjectVariable(roof.id, 'BaseZ', 320);
  await harness.stepFrames(2);
  harness.assert(value('WeatherSheltered') === 1 && value('WeatherRainVolume') < 12,
    'A ceiling above the player suppresses rain streaks and muffles rainfall');
  harness.removeObject(roof.id);
  await harness.stepFrames(2);
  harness.assert(value('WeatherSheltered') === 0 && value('WeatherRainVolume') > 20,
    'Removing overhead shelter restores outdoor rainfall');

  await tap('F6');
  await harness.stepFrames(360);
  harness.setSceneVariable('WeatherLightningClock', value('WeatherLightningWait') - 0.03);
  const strikes = value('WeatherLightningCount');
  await harness.stepFrames(4);
  harness.assert(value('WeatherType') === 3 && value('WeatherLightningCount') === strikes + 1
    && value('WeatherFlash') > 0 && value('WeatherThunderDelay') > 0,
    'A storm flashes once and schedules thunder after the light');
  await harness.stepFrames(110);
  harness.assert(value('WeatherFlash') === 0 && value('WeatherThunderDelay') === -1
    && harness.getPlayedSounds().some(sound => sound.sound.includes('weather-thunder')),
    'The flash fades and the delayed thunder sound plays');

  await tap('F6');
  await harness.stepFrames(450);
  harness.assert(value('WeatherType') === 4 && value('WeatherMist') > 0.98
    && value('WeatherRain') < 0.015 && value('WeatherThunderDelay') === -1,
    'Fog replaces the storm smoothly and clears rain and pending thunder');
  const referenceClock = value('WeatherClock');
  await tap('F3');
  await harness.stepFrames(30);
  harness.assert(harness.getRuntimeLayer('Weather')?.isVisible() === false
    && harness.getObjects('WeatherStatus')[0]?.hidden === true
    && value('WeatherClock') <= referenceClock + 0.04 && value('WeatherRainVolume') === 0,
    'Art reference mode hides weather and stops its simulation and sound');
  await tap('F3');

  await tap('F6');
  harness.setSceneVariable('WeatherClock', value('WeatherDuration') - 0.02);
  const changes = value('WeatherChanges');
  await harness.stepFrames(3);
  harness.assert(value('WeatherType') === 1 && value('WeatherChanges') === changes + 1
    && value('WeatherClock') < 0.1,
    'The automatic timer moves a clear spell into cloud cover exactly once');
  harness.assert(['WeatherCanvas', 'WeatherPanel', 'WeatherStatus'].every(name => harness.getObjects(name).length === 1),
    'Cycling, menus and reference mode do not duplicate weather objects');
  harness.watch('WeatherStatus');
} finally {
  harness.releaseAllInputs();
}
