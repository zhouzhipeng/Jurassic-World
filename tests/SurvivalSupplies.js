// Inputs exercise the entire food, fire, water and canteen loop.
const n = name => Number(harness.getSceneVariable(name)?.value);
const o = (name, key) => Number(harness.getObjectVariable(name, key)?.value);
async function tap(key) {
  harness.setKeyPressed(key, true); await harness.stepFrames(1);
  harness.setKeyPressed(key, false); await harness.stepFrames(1);
}
async function move(x, y) {
  harness.setObjectPosition(harness.getObjects('Player3D')[0].id, x, y, 0);
  await harness.stepFrames(3);
}
try {
  await harness.goToScene('Game'); await harness.stepFrames(3);
  harness.setSceneVariable('SaveStorage', 'JurassicWorldTests_SurvivalSupplies');
  harness.assert(harness.getObjects('SpringWater').length === 3 && harness.getObjects('MetalDeposit').length === 6,
    'The island contains three fresh-water sources and six mineable metal seams');
  await move(0, 400);
  harness.setSceneVariable('Water', 40);
  await tap('f');
  harness.assert(n('Water') === 40 && n('NavMode') === 1, 'Drinking away from water gives directions without free water');
  harness.setSceneVariable('Hunger', 40);
  const berries = n('Berries'); await tap('Num3');
  harness.assert(n('Berries') === berries - 1 && n('Hunger') === 48, 'Hotbar 3 consumes one berry and restores eight hunger');
  await move(-650, 300);
  const raw = n('Meat'); await tap('c');
  harness.assert(n('Meat') === raw && o('CampHearth', 'Cooking') === 0, 'An unlit fire cannot consume raw meat');
  const wood = n('Wood'); await tap('v');
  harness.assert(n('Wood') === wood - 1 && o('CampHearth', 'Fuel') > 44, 'One wood starts a 45-second campfire');
  await tap('c');
  harness.assert(n('Meat') === raw - 1 && o('CampHearth', 'Cooking') === 1, 'C queues one piece of meat at the nearby fire');
  await tap('c');
  harness.assert(n('Meat') === raw - 1, 'Repeated cooking input cannot charge for a second occupied slot');
  await tap('Escape');
  const frozen = [o('CampHearth', 'Fuel'), o('CampHearth', 'CookTime')];
  await harness.stepFrames(180);
  harness.assert(o('CampHearth', 'Fuel') === frozen[0] && o('CampHearth', 'CookTime') === frozen[1],
    'Fuel and cooking freeze while the pause menu is open');
  await tap('Escape'); await harness.stepFrames(500);
  harness.assert(n('CookedMeat') === 1 && n('MealsCooked') === 1 && o('CampHearth', 'Cooking') === 0,
    'Eight active seconds complete exactly one meal');
  const hunger = n('Hunger'); await tap('Num5');
  harness.assert(n('CookedMeat') === 0 && n('MeatEaten') === 1 && n('Hunger') >= hunger + 29.5,
    'Hotbar 5 consumes cooked meat for a substantial meal');
  await move(-1020, 440);
  const hide = n('Hide'), fiber = n('Fiber'); await tap('i');
  harness.assert(n('Canteen') === 1 && n('Hide') === hide - 2 && n('Fiber') === fiber - 4,
    'The workbench crafts one canteen from hide and fiber');
  await tap('i');
  harness.assert(n('Hide') === hide - 2, 'A second canteen input cannot charge materials again');
  await move(-220, 1060); await tap('f');
  harness.assert(n('Water') === 100 && n('CanteenCharges') === 3 && n('WaterVisits') === 1,
    'A spring restores water and fills all three canteen portions');
  await move(100, 400); harness.setSceneVariable('Water', 50); await tap('f');
  harness.assert(n('Water') === 90 && n('CanteenCharges') === 2, 'A wilderness drink spends one stored portion for forty water');
  harness.setSceneVariable('Water', 100); await tap('f');
  harness.assert(n('CanteenCharges') === 2, 'Drinking while fully hydrated cannot waste stored water');
  const before = harness.getObjects('Player3D')[0]; await tap('q');
  const after = harness.getObjects('Player3D')[0];
  harness.assert(Math.hypot(after.x-before.x,after.y-before.y)<1, 'Q changes navigation without teleporting the player');
} finally { harness.releaseAllInputs(); }
