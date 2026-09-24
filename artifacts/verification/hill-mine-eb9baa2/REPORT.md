# West hill mine runtime review

Source revision: `eb9baa2` (the game source before this evidence-only report).

Reviewed screenshots:

- `artifacts/verification/hill-mine-eb9baa2/entrance.png`: the cut in the west hill opens onto the supported gallery.
- `artifacts/verification/hill-mine-eb9baa2/interior.png`: the camera is under the intact hill roof, with crystals, ore, supports, and a giant spider visible.

Validation: GDevelop structural validation, event code generation, and semantic lint all passed. The paused `Game` preview (`preview-ws-22`) reported no runtime errors and the expected mine instance counts: one gallery, four veins, three crystal clusters, two spiders, and one serpent.

Runtime checks: walking west from the entrance kept `MineInside=1` and matched `PlayerFloor` to the excavated tunnel floor at about 199.6 game units. Holding E beside the first vein awarded two titanium ore. A spider hit removed eight health. Moving east beyond the entrance restored the previous camera distance and pitch, cleared `MineInside`, and showed the player again.
