"""Blender: --background --python ABS_SCRIPT -- ABS_OUTPUT_JSON.

Read the editable island, preserve the 1 m ground grid, and emit conservative
camera-only boxes for each disconnected scenery component. No source writes.
"""
import bpy, json, sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(root/'sources/environment/island-mountain-source.blend'))
obj=bpy.context.scene.objects[0]; mesh=obj.data
adj=[[] for _ in mesh.vertices]
for edge in mesh.edges:
    a,b=edge.vertices;adj[a].append(b);adj[b].append(a)
seen=set();bounds=[];ground=0
for start in range(len(adj)):
    if start in seen:continue
    todo=[start];seen.add(start);ids=[]
    while todo:
        i=todo.pop();ids.append(i)
        for j in adj[i]:
            if j not in seen:seen.add(j);todo.append(j)
    if len(ids)>10000:
        ground+=1;continue
    points=[obj.matrix_world@mesh.vertices[i].co for i in ids]
    game=[(p.x*100,-p.y*100,p.z*100) for p in points]
    lo=[min(p[i] for p in game) for i in range(3)]
    hi=[max(p[i] for p in game) for i in range(3)]
    bounds.append([round(v,5) for v in lo+hi])
print("BOUND_COUNTS",len(mesh.vertices),len(mesh.edges),ground,len(bounds))
assert ground==1 and 0<len(bounds)<2000
destination=Path(sys.argv[sys.argv.index('--')+1]).resolve()
destination.parent.mkdir(parents=True,exist_ok=True)
destination.write_text(json.dumps({'source':'sources/environment/island-mountain-source.blend','groundGridExcluded':True,'boxes':bounds},indent=2),encoding='utf-8')
print(json.dumps({'boxes':len(bounds),'groundComponents':ground,'output':str(destination)}))
