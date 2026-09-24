# Hill mine camera verification

- Source revision: `15676f1fb00fc6d21f7bd9e2c1199af9ff250dc2` (`Lower camera inside hill mine`)
- Changed source: `scenes/Game/external-events/CameraVisibility.events`
- Issue: `issues/issue-20260924-090753-748.md`
- Validation: `validate_project_files` passed structural, event generation, extension generation, JavaScript authoring, and semantic checks.
- Runtime: `verify_project_change` reloaded the project and launched a fresh paused `Game` preview (`preview-ws-24`); all three assertions passed and runtime error count was zero.
- Cave inspection: moved `Player3D` to the reported mine position (-1837, 621), set `MineInside=1`, advanced paused frames, and reviewed `mine-camera-after.png`. The gallery interior is visible beneath the roof.
- Scope: the screenshot verifies the cave framing at this position. Other cave positions and normal player traversal were not exercised.
