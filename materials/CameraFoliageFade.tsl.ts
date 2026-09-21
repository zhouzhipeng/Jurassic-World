import { defineMaterial } from '@gdevelop/tsl';

export default defineMaterial({
  apiVersion: 1,
  base: 'inherit',
  label: 'Camera foliage fade',
  parameters: {
    opacity: { type: 'number', default: 1, min: 0, max: 1 },
  },
  build({ material, inputs, parameters }) {
    material.opacityNode = inputs.opacity.mul(parameters.opacity);
    material.transparent = true;
    material.depthWrite = false;
  },
});
