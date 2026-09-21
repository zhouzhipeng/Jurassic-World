import { defineMaterial } from '@gdevelop/tsl';
import { dot, normalView, positionView, smoothstep } from 'three/tsl';

export default defineMaterial({
  apiVersion: 1,
  base: 'basic',
  label: 'Player occlusion outline',
  parameters: {
    tint: { type: 'color', default: '#8fffe8' },
    visibility: { type: 'number', default: 1, min: 0, max: 1 },
  },
  build({ material, parameters }) {
    const facing = dot(normalView.normalize(), positionView.normalize()).abs();
    const rim = smoothstep(0.3, 0.8, facing.oneMinus());
    material.colorNode = parameters.tint;
    // A faint interior keeps the small, low-poly limbs readable behind a tree.
    material.opacityNode = rim.mul(0.82).add(0.12).mul(parameters.visibility);
    material.transparent = true;
    material.depthTest = false;
    material.depthWrite = false;
    material.side = 'front';
  },
});
