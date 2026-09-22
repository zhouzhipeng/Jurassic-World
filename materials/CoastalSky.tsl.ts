import { defineMaterial } from '@gdevelop/tsl';
import { color, dot, mix, positionLocal, smoothstep, vec3, vec4 } from 'three/tsl';

export default defineMaterial({
  apiVersion: 1,
  base: 'basic',
  label: 'Photographic coastal sky — daylight and weather',
  parameters: {
    daylight: { type: 'number', default: 1, min: 0, max: 1 },
    twilight: { type: 'number', default: 0, min: 0, max: 1 },
    cloud: { type: 'number', default: 0, min: 0, max: 1 },
    mist: { type: 'number', default: 0, min: 0, max: 1 },
    flash: { type: 'number', default: 0, min: 0, max: 1 },
    horizon: { type: 'color', default: '#72bbdd' },
  },
  build({ material, inputs, parameters }) {
    const up = positionLocal.normalize().y;
    const horizonBand = smoothstep(0.02, 0.32, up).oneMinus();
    const luminance = dot(inputs.baseColor, vec3(0.2126, 0.7152, 0.0722));
    const cloudy = mix(inputs.baseColor, vec3(luminance).mul(0.58), parameters.cloud.mul(0.8));
    const night = cloudy.mul(color('#344d85')).mul(0.055);
    const daylight = cloudy.mul(parameters.cloud.mul(-0.4).add(1));
    const twilight = color('#ee945f').mul(parameters.twilight).mul(horizonBand).mul(0.28);
    const sky = mix(night, daylight, parameters.daylight).add(twilight);
    const haze = horizonBand.mul(0.65).add(parameters.mist.mul(0.5)).saturate();
    // Output bypasses distance fog: a camera-centred sky must not become a flat fog sphere.
    material.outputNode = vec4(mix(sky, parameters.horizon, haze).add(vec3(parameters.flash.mul(0.35))), 1);
    material.side = 'back';
    material.depthWrite = false;
    material.depthTest = true;
  },
});
