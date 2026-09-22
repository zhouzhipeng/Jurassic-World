"""Blender background script: lossless spatial query tiles from island.glb.

Run with Blender --background --python ABS_SCRIPT -- ABS_OUTPUT_DIR.
The visible island stays unchanged; hidden tiles serve bounded camera queries.
"""
import copy, json, math, struct, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from partition_island import read_glb, signature, partition
outdir=Path(sys.argv[sys.argv.index('--')+1]).resolve()
outdir.mkdir(parents=True,exist_ok=True)
partition(ROOT/'assets/models/island-camera-scenery.glb',outdir/'scenery-partitioned.glb')
doc,binary=read_glb(outdir/'scenery-partitioned.glb')
assert len(doc['meshes'])==1 and len(doc['nodes'])==1
groups={}
for p in doc['meshes'][0]['primitives']:
    a=doc['accessors'][p['attributes']['POSITION']]
    key=tuple(math.floor((a['min'][i]+a['max'][i])/2/24) for i in (0,2))
    groups.setdefault(key,[]).append(p)
manifest=[]
total=0
for index,(key,primitives) in enumerate(sorted(groups.items())):
    positions=[doc['accessors'][p['attributes']['POSITION']] for p in primitives]
    lo=[min(a['min'][i] for a in positions) for i in range(3)]
    hi=[max(a['max'][i] for a in positions) for i in range(3)]
    origin=[(lo[0]+hi[0])/2,lo[1],(lo[2]+hi[2])/2]
    position_ids={p['attributes']['POSITION'] for p in primitives}
    out=copy.deepcopy(doc);out['accessors']=[];out['bufferViews']=[];buffer=bytearray()
    remap={}
    for p in primitives:
        for ai in list(p['attributes'].values())+[p['indices']]:
            if ai in remap:continue
            a=copy.deepcopy(doc['accessors'][ai]);v=copy.deepcopy(doc['bufferViews'][a['bufferView']])
            while len(buffer)%4:buffer.append(0)
            offset=len(buffer);data=bytearray(binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']])
            if ai in position_ids:
                assert a['componentType']==5126 and a['type']=='VEC3'
                for vertex in range(a['count']):
                    at=a.get('byteOffset',0)+vertex*v.get('byteStride',12)
                    before=struct.unpack_from('<fff',data,at)
                    struct.pack_into('<fff',data,at,*(before[j]-origin[j] for j in range(3)))
                    after=struct.unpack_from('<fff',data,at)
                    assert max(abs(after[j]+origin[j]-before[j]) for j in range(3))<.00002
                a['min']=[a['min'][j]-origin[j] for j in range(3)]
                a['max']=[a['max'][j]-origin[j] for j in range(3)]
            buffer.extend(data)
            v['byteOffset']=offset;a['bufferView']=len(out['bufferViews'])
            out['bufferViews'].append(v);remap[ai]=len(out['accessors']);out['accessors'].append(a)
    selected=[]
    for p in primitives:
        p=copy.deepcopy(p);p['indices']=remap[p['indices']]
        p['attributes']={n:remap[a] for n,a in p['attributes'].items()};selected.append(p)
    out['meshes'][0]['primitives']=selected
    out['buffers']=[{'byteLength':len(buffer)}]
    encoded=json.dumps(out,separators=(',',':')).encode();encoded+=b' '*(-len(encoded)%4);buffer+=b'\0'*(-len(buffer)%4)
    filename=f'terrain-probe-{index:02}.glb'
    payload=struct.pack('<III',0x46546C67,2,28+len(encoded)+len(buffer))+struct.pack('<II',len(encoded),0x4E4F534A)+encoded+struct.pack('<II',len(buffer),0x004E4942)+buffer
    (outdir/filename).write_bytes(payload)
    check,blob=read_glb(outdir/filename);count=signature(check,blob).total();total+=count
    manifest.append(dict(name=f'TerrainProbe{index:02}',file=filename,min=[v*100 for v in lo],max=[v*100 for v in hi],origin=[v*100 for v in origin],triangles=count))
assert total==signature(doc,binary).total()
(outdir/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'tiles':len(manifest),'triangles':total,'exactTriangleAttributesPreserved':True}))
