# Coastal swimming verification

Source revision: `be1e855680fc5e0b930472b7caeb422a395034ad`.

- `artifacts/verification/coastal-swimming-v1/beach.png`: reviewed running preview on the west beach, with the player standing on dry sand beside the shallow water.
- `artifacts/verification/coastal-swimming-v1/surface-swim.png`: reviewed running preview at the sea surface, with the swimming pose visible and no camera occlusion silhouette.
- `tests/CoastalSwimming.js`: gameplay operation `gameplay-tests-69d37455-64ad-45f9-a9bc-0f7f4582bd4a` passed all seven assertions, covering the dry beach, sea entry, swimming, diving, breath use, resurfacing and return to shore.
- Fresh `Game` preview `preview-ws-29`: runtime verification passed; zero runtime errors or failed textures, with the 3D renderer active.
