# Coastal environment

Added camera-centred photographic sky and an independent 680 m wide sea.
The sky uses Poly Haven's CC0 Kloppenheim 05 Pure Sky panorama; provenance is
in assets/environment/LICENSE.md. It is embedded into coastal-sky.glb.

CoastalSky.tsl.ts controls horizon haze, cloud dimming, dusk and night colors.
CoastalOcean.tsl.ts combines warped swells, fine ripples, angle-dependent sky
reflection approximation, sun glints and near/offshore color. This is a surface
shader, not screen-space reflections, refraction, swimming or water physics.
Both materials follow the existing weather/daylight system through
scenes/Game/external-events/CoastalEnvironment.events. Wave time follows
WeatherMotion so opening a gameplay menu freezes it with the existing weather.

The sea is placed at -80 game units, above the old static water at -95; maximum
vertex displacement is below 11 units even with full cloud strength, so the old surface cannot z-fight. No
existing island model, collision, save data or walkable surface was replaced.
Renderer world positions use metres with inverted Y, while event uniforms use
game units. Keep the conversion in CoastalOcean when editing its wave formulas.

Regenerate assets with Blender 5.1:

    blender --background --python ABSOLUTE_PROJECT/tools/build_coastal_environment.py

The script preserves existing island assets, saves a separate .blend, embeds
the sky texture, exports two GLBs and performs a round-trip mesh check.

Verification: both materials passed model-level WebGL validation. Final fresh
preview passed six assertions: one sky, one sea, visible 3D meshes, zero runtime
errors, zero World3D texture failures and zero World3D rejected objects.
Day, night, rain and two camera headings were visually inspected. Screenshots
are in artifacts/verification/coastal/coastal-*.png; coastal-final.png is the final source revision.

An engine bug found by this scene was fixed in D:/code/GDevelop, commit
32beb54b01 (Preserve RGB type for inherited TSL base color inputs). The runtime
and browser validator now expose the documented RGB baseColor for mapped
materials. All 28 TSL runtime tests passed and the runtime was rebuilt.
Other machines require that engine fix to use the photographic sky material.
