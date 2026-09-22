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
    const x = positionWorld.x;
    const y = positionWorld.y;
    const a = x.mul(0.012).add(y.mul(0.007)).add(t.mul(0.8));
    const b = x.mul(-0.009).add(y.mul(0.019)).sub(t.mul(1.15));
    const c = x.mul(0.062).add(y.mul(0.041)).add(sin(y.mul(0.025))).add(t.mul(1.7));
    const d = x.mul(-0.11).add(y.mul(0.083)).sub(t.mul(2.2));
    const strength = parameters.cloud.mul(0.6).add(1);
    const nx = cos(a).mul(-0.045).add(cos(b).mul(0.025)).add(cos(c).mul(-0.038)).add(cos(d).mul(0.021));
    const ny = cos(a).mul(-0.026).add(cos(b).mul(-0.053)).add(cos(c).mul(-0.025)).add(cos(d).mul(-0.016));
    const n = vec3(nx.mul(strength), ny.mul(strength), 1).normalize();
    const view = parameters.camera.sub(positionWorld).normalize();
    const facing = dot(n, view).max(0);
    const reflected = n.mul(facing.mul(2)).sub(view).normalize();
    const fresnel = facing.oneMinus().pow(5).mul(0.96).add(0.04);
    const radius = x.mul(x).add(y.sub(300).mul(y.sub(300))).pow(0.5);
    const offshore = smoothstep(3200, 7000, radius);
    const water = mix(color('#269e9c'), color('#073a59'), offshore);
    const light = parameters.daylight.mul(0.83).add(0.055).mul(parameters.cloud.mul(-0.4).add(1));
    const sky = mix(parameters.horizon, color('#267bb7').mul(light), reflected.z.max(0).pow(0.45));
    const glint = dot(reflected, parameters.sun.normalize()).max(0).pow(420).mul(parameters.daylight).mul(parameters.cloud.oneMinus());
    const glow = dot(reflected, parameters.sun.normalize()).max(0).pow(24).mul(0.15).mul(parameters.daylight);
    const sunColor = mix(color('#fff3cb'), color('#ffac64'), parameters.twilight);
    const surface = mix(water.mul(light), sky, fresnel.mul(0.85)).add(sunColor.mul(glint.mul(1.4).add(glow)));
    const crest = sin(c).mul(sin(d)).mul(0.5).add(0.5).pow(14).mul(0.045).mul(light);
    const fog = smoothstep(parameters.fogNear, parameters.fogFar, positionView.z.abs());
    const finalColor = surface.add(vec3(crest)).add(vec3(parameters.flash.mul(0.18)));
    material.fragmentNode = vec4(mix(finalColor, parameters.horizon, fog), 1);
    material.outputNode = vec4(mix(finalColor, parameters.horizon, fog), 1);
    // Blender GLB is Y-up locally; object rotation converts the vertical wave to world Z.
    const swell = sin(positionLocal.x.mul(0.48).add(t.mul(0.8))).mul(0.026)
      .add(sin(positionLocal.z.mul(0.71).sub(t.mul(1.1))).mul(0.016));
    material.positionNode = positionLocal.add(vec3(0, swell.mul(strength), 0));
    material.depthWrite = true;
    material.side = 'double';
  },
});
