const story = () => harness.getObjects('HeyinStory')[0];
try {
  await harness.goToScene('Game');
  await harness.stepFrames(4);
  harness.setSceneVariable('Invulnerable', 9999);
  harness.setSceneVariable('HeyinStage', 2);
  harness.setSceneVariable('TouchMode', 1);
  const initial = story().text;
  await harness.stepFrames(120);
  harness.assert(story().hidden, 'The legacy story stays hidden in the touch HUD');
  harness.assert(story().text === initial,
    'Hidden touch story does not append per frame: length=' + story().text.length);
  harness.setSceneVariable('TouchMode', 0);
  await harness.stepFrames(3);
  const desktop = story().text;
  harness.assert(!story().hidden && desktop.includes('护送禾音') && desktop.includes('体力'),
    'Desktop story preserves the objective and companion status');
  await harness.stepFrames(120);
  harness.assert(story().text.length < 500 && story().text.split('体力').length === 2,
    'Desktop story contains one current status line after sustained play');
  harness.setSceneVariable('TouchMode', 1);
  await harness.stepFrames(3);
  const switched = story().text;
  await harness.stepFrames(120);
  harness.assert(story().hidden && story().text === switched,
    'Returning to touch mode freezes hidden story content rather than growing it');
  harness.assert(harness.getObjects('HudCompanionHP')[0].text.includes('生命'),
    'The current touch companion HUD remains populated');
} finally { harness.releaseAllInputs(); }
