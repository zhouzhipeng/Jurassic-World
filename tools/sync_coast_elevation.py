"""Sync native object-ground expressions with the walkable coast mesh profile.

Run from the project root with Python after changing mountain_profile.py.
The player height logic in MountainActors has a separate coast transition.
"""
from pathlib import Path
import re

from mountain_profile import coast_edge_expression, expression, floor_expression

def legacy_floor_expression(x, y):
    edge = coast_edge_expression(x, y)
    return (f'({expression(x, y)})*max(0,min(1,(({edge})-1200)/1200))'
            f'-140+140*max(0,min(1,({edge})/600))'
            f'+0.16*min(0,({edge}))')

ROOT = Path(__file__).resolve().parents[1]
SHEETS = {
    "MountainInitialize.events": (
        "BerryBush", "FiberFern", "WoodSapling", "StoneDeposit",
        "SpringWater", "MetalDeposit",
    ),
    "MountainActors.events": (
        "Dinosaur3D", "Triceratops", "Stegosaur", "Raptor",
        "Tyrannosaur", "Heyin",
    ),
    "MountainFoliage.events": (
        "BerryBushLOD1", "BerryBushLOD2", "FiberFernLOD1", "FiberFernLOD2",
    ),
}

for sheet, objects in SHEETS.items():
    path = ROOT / "scenes/Game/external-events" / sheet
    with path.open("r", encoding="utf-8", newline="") as source:
        contents = source.read()
    for obj in objects:
        pattern = re.compile(
            rf'(?m)^(?P<prefix>[^\r\n]*do Scene3D::Base3DBehavior::SetZ '
            rf'parameter_3d_object="{obj}"[^\r\n]* value=expr\()'
            rf'(?P<value>[^\r\n]*)(?P<suffix>\))(?P<eol>\r?)$'
        )
        matches = list(pattern.finditer(contents))
        if len(matches) != 1:
            raise ValueError(f"Expected one SetZ action for {obj} in {sheet}; found {len(matches)}")
        old = expression(f"{obj}.X()", f"{obj}.Y()")
        new = floor_expression(f"{obj}.X()", f"{obj}.Y()")
        if matches[0].group("value") not in (old, legacy_floor_expression(f"{obj}.X()", f"{obj}.Y()"), new):
            raise ValueError(f"Unexpected height expression for {obj} in {sheet}")
        contents = pattern.sub(
            lambda m: m.group("prefix") + new + m.group("suffix") + m.group("eol"),
            contents,
        )
    with path.open("w", encoding="utf-8", newline="") as target:
        target.write(contents)
    print(f"Updated {sheet}: {len(objects)} object elevations")
