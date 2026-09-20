"""Focused fixes found while exercising the modular construction preview."""
from pathlib import Path
P=Path(__file__).resolve().parents[1]; E=P/'scenes/Game/external-events/ModularConstruction.events'
s=E.read_text(encoding='utf-8')
# Socket checks must use persisted position, since opening a door moves its mesh.
s=s.replace('abs(BuildX-ModularParts.X())+abs(BuildY-ModularParts.Y())','abs(BuildX-BuildingRecords[ModularParts.Variable(Slot)].X)+abs(BuildY-BuildingRecords[ModularParts.Variable(Slot)].Y)')
s=s.replace('DistanceBetweenPositions(BuildX,BuildY,AllBuildings.X(),AllBuildings.Y())','DistanceBetweenPositions(BuildX,BuildY,BuildingRecords[AllBuildings.Variable(Slot)].X,BuildingRecords[AllBuildings.Variable(Slot)].Y)')
# Filter elevation before nearest selection, allowing independently stacked walls.
needle='>> if NumberObjectVariable object="AllBuildings" variable="Kind" comparison_sign="=" value=expr(BuildKind)'
s=s.replace(needle,needle+'\n>> if BuiltinCommonInstructions::CompareNumbers first_expression=expr(abs(BuildingRecords[AllBuildings.Variable(Slot)].Z-BuildZ)) comparison_sign="<" second_expression=1')
# An open door still has a thin swung collision leaf outside the clear opening.
s=s.replace('>>> if NumberObjectVariable object="ModularParts" variable="Kind" comparison_sign="=" value=expr(15)\n>>> if NumberObjectVariable object="ModularParts" variable="Open" comparison_sign="=" value=expr(1)\n>>> do SetNumberVariable variable="BuildBlocked" modification_sign="=" value=expr(0)\n\n','')
needle='>> do SetAngle object="PartDoor" modification_sign="=" angle_in_degrees=expr(PartDoor.Variable(BaseAngle)+PartDoor.Variable(Open)*90)'
s=s.replace(needle,needle+'\n>> do SetNumberObjectVariable object="PartDoor" variable="WorldHX" modification_sign="=" value=expr(abs(cos(ToRad(PartDoor.Angle())))*78+abs(sin(ToRad(PartDoor.Angle())))*12)\n>> do SetNumberObjectVariable object="PartDoor" variable="WorldHY" modification_sign="=" value=expr(abs(sin(ToRad(PartDoor.Angle())))*78+abs(cos(ToRad(PartDoor.Angle())))*12)')
# In-place ceilings over an ascending staircase have no head clearance.
where=s.index('if NumberVariable variable="Mode" comparison_sign="=" value=0\nif NumberVariable variable="RenderMode" comparison_sign="=" value=1\nif NumberVariable variable="Riding" comparison_sign="=" value=0\nif NumberVariable variable="BuildMode" comparison_sign="=" value=1\nif NumberVariable variable="Wood"')
guard='if NumberVariable variable="Mode" comparison_sign="=" value=0\nif NumberVariable variable="BuildMode" comparison_sign="=" value=1\n'
checks=''
for selected,existing,zoffset in [(14,16,300),(16,14,-300)]:
 checks+=guard+'\n> for each ModularParts\n'+f'>> if NumberVariable variable="BuildKind" comparison_sign="=" value={selected}\n>> if NumberObjectVariable object="ModularParts" variable="Kind" comparison_sign="=" value={existing}\n>> if BuiltinCommonInstructions::CompareNumbers first_expression=expr(abs(BuildX-ModularParts.X())+abs(BuildY-ModularParts.Y())) comparison_sign="<" second_expression=1\n>> if BuiltinCommonInstructions::CompareNumbers first_expression=expr(BuildZ-ModularParts.Variable(BaseZ)) comparison_sign="=" second_expression={zoffset}\n>> do SetNumberVariable variable="BuildValid" modification_sign="=" value=0\n>> do SetStringVariable variable="BuildReason" modification_sign="=" value="楼梯上方需留洞口，请把楼板接在楼梯尽头"\n\n'
s=s[:where]+checks+s[where:]
# Let old whole-building saves remain removable without occupying a new hotkey.
where=s.rfind('\n\n',0,s.index('if NumberVariable variable="BuildDeleteSlot" comparison_sign=">="'))+2
fallback=guard+'if NumberVariable variable="BuildDeleteSlot" comparison_sign="<" value=0\n\n> for each Buildings\n>> if NumberObjectVariable object="Buildings" variable="Kind" comparison_sign="<=" value=2\n>> if BuiltinCommonInstructions::CompareNumbers first_expression=expr(DistanceBetweenPositions(BuildX,BuildY,Buildings.X(),Buildings.Y())) comparison_sign="<" second_expression=200\n>> do SetNumberVariable variable="BuildDeleteSlot" modification_sign="=" value=expr(Buildings.Variable(Slot))\n\n'
s=s[:where]+fallback+s[where:]
# The old records have no elevation; exclude them from modular elevation filtering.
s=s.replace('if NumberVariable variable="BuildKind" comparison_sign=">=" value=expr(10)\nif BuiltinCommonInstructions::CompareNumbers first_expression=expr(abs(BuildingRecords[BuildDeleteSlot].Z-BuildZ))','if NumberVariable variable="BuildingRecords[BuildDeleteSlot].Kind" comparison_sign=">=" value=expr(10)\nif BuiltinCommonInstructions::CompareNumbers first_expression=expr(abs(BuildingRecords[BuildDeleteSlot].Z-BuildZ))')
where=s.rfind('\n\n',0,s.index('if NumberVariable variable="BuildDeleteBlocked" comparison_sign="=" value=expr(0)'))+2
refund=''
for kind,wood,stone,fiber in [(1,10,5,8),(2,4,0,2)]:
 refund+=guard+f'if KeyFromTextReleased key_to_check="Delete"\nif NumberVariable variable="BuildDeleteSlot" comparison_sign=">=" value=0\nif NumberVariable variable="BuildingRecords[BuildDeleteSlot].Kind" comparison_sign="=" value={kind}\ndo SetNumberVariable variable="BuildWood" modification_sign="=" value={wood}\ndo SetNumberVariable variable="BuildStone" modification_sign="=" value={stone}\ndo SetNumberVariable variable="BuildFiber" modification_sign="=" value={fiber}\n\n'
s=s[:where]+refund+s[where:]
E.write_text(s,encoding='utf-8')
# Selection immediately clears stale placement messages.
p=P/'scenes/Game/external-events/HUDBuildSelection.events';s=p.read_text(encoding='utf-8');import re
s=re.sub(r'(do SetNumberVariable variable="BuildKind"[^\n]*\n)',r'\1do SetNumberVariable variable="BuildMessageTime" modification_sign="=" value=0\n',s);p.write_text(s,encoding='utf-8')
# Prevent a one-shot generator from reverting subsequent fixes.
p=P/'tools/author_modular_construction.py';s=p.read_text(encoding='utf-8').replace('behavior="3D"','behavior="Object3D"');s=s.replace("src=read(core);start=", "src=read(core)\nassert '@comment \"Construction placement' in src, 'Already migrated: edit the external events directly.'\nstart=");p.write_text(s,encoding='utf-8')
print('Fixed moving-door sockets, stacked demolition selection, swung-door collision, stair clearance and legacy refunds.')
