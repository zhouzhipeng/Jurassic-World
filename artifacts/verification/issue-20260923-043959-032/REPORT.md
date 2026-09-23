# Rowing animation verification

- Issue: `issues/issue-20260923-043959-032.md`
- Project source revision: `1f0efa9b05cc58c311ab003c8e8cb501a2aba315`
- Engine source revision: `cb24802273c3ee769875743e710cf29a9b9e8e9c`
- Changed project source: `scenes/Game/external-events/CoastalVoyage.events`
- Engine change: preserve animation tracks on independent root meshes when root motion is disabled.

## Result

The seated rider and both oars now use the rowing clips together when movement input is held. When input stops, the rider and oars use their resting clips. The boat no longer selects rest and rowing clips in the same frame.

## Evidence

- `validate_project_files`: valid, structural validation, event code generation, extension generated code, JavaScript authoring, and semantic lint all passed.
- `reload_project`: completed for project revision `1f0efa9`.
- Fresh paused Game preview `preview-ws-21`: held W while sailing; `Player3D.AnimationState` was 13. With the boat held against the water boundary, its position was `(6522.409, -4497.686)` in both sampled frames, while the oars changed stroke angle. Releasing W returned `Player3D.AnimationState` to 12. See [stroke A](rowing-stroke-a.png) and [stroke B](rowing-stroke-b.png).
- Runtime inspection: no errors; World3D had a Three scene, group, and camera, 137 visible meshes, zero rejected 3D objects, and zero failed textures.
- Engine regression tests: the two `3D model root motion filtering` tests passed in headless Chrome. The full TypeScript check still reports unrelated existing errors in other tests; none refer to the changed engine files.

The two screenshots document separate points in the stroke while input was held. They are visual evidence for the current project and engine revisions above, not a performance benchmark.
