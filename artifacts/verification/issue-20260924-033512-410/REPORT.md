# Stationary boat rider jitter

- Issue: `issues/issue-20260924-033512-410.md`
- Project source revision verified: `716eb75faeee65084dc5914da8353256ec880ad4` (`Remove seated animation loop jumps`); preceding camera-order commit: `14a9ff4`.
- Changed source: `scenes/Game/functions/sceneUpdate.events`, `sources/models/survivor-swim-source.blend`, `assets/models/survivor-animated.glb`.

The recorded input log contains only pointer movement, so the stationary seated clip was inspected. In the previous GLB, `BoatSit` started with the hips at 0.9016 m, then fell to 0.49 m on the next key. `BoatRow` had the same initial pose mismatch. Both one-second clips looped, causing a repeated visible snap. The editable Blender source and exported GLB now give every animated channel in these two clips matching first and last poses. The camera update also runs after boat and rider movement.

Verification: the exported GLB retains 20 named clips, 16 bones, 7 meshes and 7 material slots. All 48 channels in each corrected boat clip have zero first-to-last difference. `validate_project_files` passed structural, event code, extension code, JavaScript authoring and semantic checks. After commit, `verify_project_change` reloaded the project and returned `runtimeVerified=true`, `completionReady=true`: Game had one rider and one boat, 402 visible World3D meshes, zero runtime errors, failed textures or rejected objects. In the fresh paused preview `preview-ws-6`, 125 idle frames left `AnimationState=12` and rider position/angle exactly matched the boat; 65 further single-frame samples kept the rider's hand and foot bone heights constant, including across the loop. The reviewed screenshot is [seated-after.png](seated-after.png).

The deterministic preview checks the corrected loop and runtime state. It does not measure frame pacing during real-time play.
