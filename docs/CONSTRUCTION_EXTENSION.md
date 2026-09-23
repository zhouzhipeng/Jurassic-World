# Construction extension boundary

`JurassicConstruction` owns the building and ghost prefabs, construction input state, snapping and placement rules, placement and demolition, door state, and save and restore. The generated `.gdevelop/project-module-map.json` lists the current components. Scene adapters remain in canonical `scenes/Game/` paths.

## Signal contract

Signals are scene local and delivered on the next frame. `Game` places one `ConstructionController` prefab. Its `onCreated` function subscribes to construction commands; `Game/sceneSignal` receives results and updates compatibility variables used by the HUD and player systems.

| Command signal | Payload | Extension effect and result |
| --- | --- | --- |
| `Construction.Input` | `Toggle`, `Enable`, `Disable`, `Select:<kind>`, `Rotate`, `LevelUp`, or `LevelDown` | Controller changes mode, kind, angle, or level and emits `Construction.InputState`. |
| `Construction.Preview` | JSON snapshot of player position, camera yaw, inventory, floor, dinosaur, harvest nodes, and wildlife | Controller snaps to a socket, evaluates costs, support, occupancy, terrain and collision, and emits `Construction.PreviewReady`. |
| `Construction.Place` | Empty command | Controller uses its own latest valid preview to create a building and emits `Construction.Placed`. The scene cannot supply coordinates or costs for creation. |
| `Construction.RemoveAt` | Empty command | Controller resolves the nearest matching building from its preview, checks dependents, then emits `Construction.Remove` or `Construction.RemovalBlocked`. |
| `Construction.Remove` | Slot number, emitted by the controller | Controller deletes the building, calculates the refund, and emits `Construction.Removed`. |
| `Construction.ToggleDoor` | Door slot number | Controller changes the door state and emits `Construction.DoorToggled`; the door prefab applies its own animation and bounds. |
| `Construction.Save` | Storage name | Controller serializes live building instances and writes `BuildingsV2`. |
| `Construction.Load` | Storage name | Controller reads `BuildingsV2`, falls back to `BuildingsV1`, and emits `Construction.Restore`. |
| `Construction.Restore` | JSON array of records | Controller recreates up to 128 buildings and emits `Construction.Restored` and `Construction.RecordsRestored`. |

`Construction.PreviewReady` carries position, height, rotated bounds, material costs, support parent, free slot, validity reason, and demolition target. `Construction.Placed`, `Construction.Removed`, and `Construction.DoorToggled` carry the committed changes. `Game/sceneSignal` mirrors these into `BuildingRecords`, `BuildCount`, inventory and UI variables. The extension remains authoritative for building instances and final placement checks.

Each signal hop takes a frame. The scene sends preview context while construction mode is active; a preview result usually reaches the HUD two frames later. Placement and demolition requests use controller state, so their committed object mutations do not depend on stale HUD mirrors.

## Scene adapters

- `ConstructionPreviewContext` captures key presses and a native-event snapshot of scene-owned player, resource, harvest, and wildlife state.
- `ConstructionGhostAndPlacementInput` positions the ghost visuals from the preview mirror and sends the place command.
- `ConstructionRemovalInput` forwards Delete or touch input.
- `HUDBuildSelection`, `HUDConstructionInput`, and touch events capture UI input; the controller owns mode, selection, rotation, and level state.
- `ConstructionWorldInteraction` keeps player movement and floor collision in the scene physics system. Its door input sends a signal; the door prefab owns open state and animation.
- `ConstructionHarvestBlocking` remains with the resource system because it changes harvest-node cooldowns in response to nearby buildings.

These adapters do not create, delete, validate, or serialize buildings. Legacy scene variables are compatibility mirrors for the HUD, player physics, and existing save menu. Building `Slot` values are array indices; empty records have `Kind = 0`. The seven modular prefabs apply `BaseZ` to their 3D positions in `doStepPostEvents`.

JavaScript in the extension handles building-instance variables and world object creation where the available native object-variable instructions are scene-scoped. The scene snapshot and signal actions use native events.

## Verification

The focused gameplay regressions are `ConstructionPlacement`, `ConstructionSupport`, `ConstructionStairs`, `ConstructionWildlife`, `ConstructionDoors`, `ConstructionPersistence`, and `ConstructionSignals` in `tests/`. Run them after changes to the signal payloads, controller logic, building prefabs, or scene adapters. Historical test results are not evidence for a new revision.
