const n=name=>Number(harness.getSceneVariable(name)?.value);
const fire=key=>Number(harness.getObjectVariable('CampHearth',key)?.value);
async function tap(key) {
  harness.setKeyPressed(key,true);await harness.stepFrames(1);
  harness.setKeyPressed(key,false);await harness.stepFrames(1);
}
try {
  await harness.goToScene('Game');await harness.stepFrames(3);
  harness.setObjectPosition(harness.getObjects('Player3D')[0].id,0,1300,0);
  harness.setSceneVariable('Water',0);harness.setSceneVariable('Hunger',60);
  const hunger=n('Hunger');await harness.stepFrames(360);
  harness.assert(n('Health')<95 && n('Hunger')<hunger,'Dehydration harms health while hunger continues to decline independently');
  harness.setSceneVariable('Water',60);harness.setSceneVariable('Hunger',0);
  const health=n('Health');await harness.stepFrames(360);
  harness.assert(n('Health')<health-4 && n('Water')<60,'Starvation harms health without freezing the water simulation');
  // Start already soaked to test the dangerous threshold without a minute of rain.
  for(const [name,value] of Object.entries({Hunger:60,Water:60,Health:80,BodyTemp:35.05,Wetness:100,WorldMinutes:1320,WeatherType:2,WeatherClock:0,WeatherDuration:180}))
    harness.setSceneVariable(name,value);
  await harness.stepFrames(600);
  harness.assert(n('BodyTemp')<35 && n('Health')<80,'A soaked player at night becomes hypothermic and takes environmental damage');
  await tap('Escape');const paused=[n('BodyTemp'),n('Wetness'),n('Health')];await harness.stepFrames(120);
  harness.assert([n('BodyTemp'),n('Wetness'),n('Health')].every((v,i)=>v===paused[i]),'Paused menus freeze exposure and environmental damage');
  await tap('Escape');
  harness.setObjectPosition(harness.getObjects('Player3D')[0].id,-650,300,0);await harness.stepFrames(3);
  await tap('v');const temperature=n('BodyTemp'),wetness=n('Wetness');await harness.stepFrames(600);
  harness.assert(n('Warmth')===1 && n('BodyTemp')>temperature+1 && n('Wetness')<wetness-40,
    'A fuelled fire warms and dries the player even during rain');
  // Arrange the end of an existing fuel charge; real C input starts the job.
  harness.setObjectVariable('CampHearth','Fuel',0.2);await tap('c');await harness.stepFrames(60);
  const stopped=fire('CookTime'),meals=n('CookedMeat');await harness.stepFrames(120);
  harness.assert(fire('Fuel')===0 && fire('Cooking')===1 && fire('CookTime')===stopped && stopped>7,
    'Fuel exhaustion pauses the unfinished cooking job');
  harness.assert(harness.getObjects('FireGlow').every(x=>x.hidden),'Extinguished fires hide their flame meshes');
  await tap('v');await harness.stepFrames(500);
  harness.assert(n('CookedMeat')===meals+1 && fire('Cooking')===0,'Adding fuel resumes the retained job and yields only one meal');
} finally {harness.releaseAllInputs();}
