# Airborne predator bite verification

- Source revision: `24409e50fa507ddbad12bdf784db5b2c0e948398` (`Preserve damage on reachable low flights`), including `f59a4bee7b9beeb078a10eafcc7921f389797ee9`.
- Changed source: `scenes/Game/functions/sceneUpdate.events`.
- Reported issue: `issues/issue-20260924-063709-136.md` (ignored diagnostic input).

The raptor and tyrannosaur attack-start and hit events now check vertical distance against their authored model heights (375 and 675 world units). Pterosaur riding no longer receives the ground-mount horizontal reach or damage reduction.

## Gates

- Final `validate_project_files`: valid, structurally valid, event code generation valid, extension generated code valid, JavaScript authoring valid, and semantic lint passed. Its runtime flags remained false as expected.
- `reload_project` operation `reload-project-235`: completed successfully after the source commit.
- Fresh paused Game preview: `preview-ws-15`; deterministic `run_frames` checks below. No runtime errors were reported.

## Runtime checks

| Setup | Frames | Result |
| --- | ---: | --- |
| Pterosaur directly above raptor at Z 1210; raptor Z 211 | 200 | Raptor stayed in chase state 2, cooldown reached 0, health stayed 100. |
| Same position, flight Z 350 | 50 | Raptor completed a bite; health fell from 100 to 88. |
| Pterosaur directly above tyrannosaur at Z 1940; tyrannosaur Z about 936 | 200 | Tyrannosaur stayed in chase state 2, cooldown reached 0, health stayed 100. |
| Same position, flight Z 1100 | 50 | Tyrannosaur completed a bite; health fell from 100 to 76. |

The preview used injected scene state and instance positions to isolate bite reach. It did not replay the original player input sequence or assess visual animation alignment at the exact vertical threshold.
