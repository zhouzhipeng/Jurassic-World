import { defineMaterial } from '@gdevelop/tsl';
import { color, cos, dot, mix, positionLocal, positionView, positionWorld, sin, smoothstep, vec3, vec4 } from 'three/tsl';

export default defineMaterial({
  apiVersion: 1,
  base: 'custom',
  label: 'Coastal ocean — moving swells, Fresnel sky and sun glints',
  parameters: {
    clock: { type: 'number', default: 0 },
    daylight: { type: 'number', default: 1, min: 0, max: 1 },
    cloud: { type: 'number', default: 0, min: 0, max: 1 },
    twilight: { type: 'number', default: 0, min: 0, max: 1 },
    flash: { type: 'number', default: 0, min: 0, max: 1 },
    camera: { type: 'vec3', default: [0, -1000, 500] },
    sun: { type: 'vec3', default: [-0.5, -0.5, 0.7] },
    horizon: { type: 'color', default: '#72bbdd' },
    fogNear: { type: 'number', default: 6500 },
    fogFar: { type: 'number', default: 26000 },
  },
  build({ material, parameters }) {
    const t = parameters.clock;
    // This scene uses 100 game units per renderer metre and inverted renderer Y.
    const world = vec3(positionWorld.x.mul(100), positionWorld.y.mul(-100), positionWorld.z.mul(100));
    const x = world.x;
    const y = world.y;
    const warp = sin(x.mul(0.0023).add(y.mul(0.0031))).mul(3)
      .add(cos(x.mul(-0.0041).add(y.mul(0.0017))).mul(2));
    const a = x.mul(0.012).add(y.mul(0.007)).add(warp).add(t.mul(2.1));
    const b = x.mul(-0.009).add(y.mul(0.019)).add(warp.mul(1.7)).sub(t.mul(2.8));
    const c = x.mul(0.062).add(y.mul(0.041)).add(sin(y.mul(0.025)).mul(3)).add(warp).add(t.mul(4.2));
    const d = x.mul(-0.11).add(y.mul(0.083)).add(warp.mul(2.3)).sub(t.mul(5.1));
    const detail = smoothstep(1200, 9000, positionView.z.abs().mul(100)).oneMinus();
    const strength = parameters.cloud.mul(0.6).add(1);
    const nx = cos(a).mul(-0.028).add(cos(b).mul(0.018)).add(cos(c).mul(-0.025).mul(detail)).add(cos(d).mul(0.014).mul(detail));
    const ny = cos(a).mul(-0.019).add(cos(b).mul(-0.033)).add(cos(c).mul(-0.017).mul(detail)).add(cos(d).mul(-0.01).mul(detail));
    const n = vec3(nx.mul(strength), ny.mul(strength), 1).normalize();
    const view = parameters.camera.sub(world).normalize();
    const facing = dot(n, view).max(0);
    const reflected = n.mul(facing.mul(2)).sub(view).normalize();
    const fresnel = facing.oneMinus().pow(5).mul(0.96).add(0.04);
    const radius = x.mul(x).add(y.sub(300).mul(y.sub(300))).pow(0.5);
    const offshore = smoothstep(3200, 7000, radius);
    const water = mix(color('#247eaf'), color('#0b619c'), offshore);
    const light = parameters.daylight.mul(0.83).add(0.1).mul(parameters.cloud.mul(-0.4).add(1));
    const sky = mix(parameters.horizon, color('#267bb7').mul(light), reflected.z.max(0).pow(0.45));
    const glint = dot(reflected, parameters.sun.normalize()).max(0).pow(420).mul(parameters.daylight).mul(parameters.cloud.oneMinus());
    const glow = dot(reflected, parameters.sun.normalize()).max(0).pow(24).mul(0.15).mul(parameters.daylight);
    const sunColor = mix(color('#fff3cb'), color('#ffac64'), parameters.twilight);
    const surface = mix(water.mul(light), sky, fresnel.mul(0.85)).add(sunColor.mul(glint.mul(1.4).add(glow)));
    const crest = sin(c).mul(sin(d)).mul(0.5).add(0.5).pow(10).mul(0.075).mul(light);
    const movingSheen = sin(a).mul(0.5).add(sin(b).mul(0.25)).add(0.5).saturate().mul(0.07).mul(light);
    const fog = smoothstep(parameters.fogNear, parameters.fogFar, positionView.z.abs().mul(100));
    const finalColor = surface.add(vec3(crest.add(movingSheen))).add(vec3(parameters.flash.mul(0.18)));
    material.fragmentNode = vec4(mix(finalColor, parameters.horizon, fog), 1);
    material.outputNode = vec4(mix(finalColor, parameters.horizon, fog), 1);
    // Blender GLB is Y-up locally; object rotation converts the vertical wave to world Z.
    const swell = sin(positionLocal.x.mul(0.48).add(t.mul(2.1))).mul(0.04)
      .add(sin(positionLocal.z.mul(0.71).sub(t.mul(2.8))).mul(0.025));
    material.positionNode = positionLocal.add(vec3(0, swell.mul(strength), 0));
    material.depthWrite = true;
    material.side = 'double';
  },
});
