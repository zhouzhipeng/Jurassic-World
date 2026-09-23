# Construction extension boundary

`JurassicConstruction` owns the building prefabs and the save and restore workflow. The generated `.gdevelop/project-module-map.json` is the source for the current component inventory; this document records the integration contract.

## Signal contract

Signals are scene local and delivered on the following frame. `Game` has one `ConstructionController` prefab instance, which subscribes in `onCreated`.

| Signal | Sender | Payload | Receiver effect |
| --- | --- | --- | --- |
| `Construction.Save` | `Game` | Storage name | Controller serializes live buildings and writes `BuildingsV2`. |
| `Construction.Load` | `Game` | Storage name | Controller reads `BuildingsV2`, falling back to `BuildingsV1`, then emits `Construction.Restore`. |
| `Construction.Restore` | `Game` or controller | JSON array of building records | Controller recreates up to 128 buildings. |
| `Construction.Restored` | Controller | Building count as text | `Game/sceneSignal` updates the compatibility count. |
| `Construction.RecordsRestored` | Controller | Restored JSON array | `Game/sceneSignal` refreshes the compatibility record array. |

Building `Slot` values are array indices. Empty records have `Kind = 0`. The controller restores position, angle, parent, level, open state and bounds; each modular prefab applies `BaseZ` to its 3D position in `doStepPostEvents`.

## Remaining scene compatibility layer

The scene still owns construction input, preview, placement validation, demolition and world interaction in `scenes/Game/external-events/`. These events also read and update `BuildingRecords` directly. They must be migrated before the extension is fully independent. Keep the signal boundary for all new scene to extension communication and preserve the existing scene variable mirrors until their callers are moved.

The focused save and restore regression is `tests/ConstructionSignals.js`. `tests/ConstructionSupport.js` covers placement support and demolition behavior.
