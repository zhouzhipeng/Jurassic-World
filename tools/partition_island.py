"""Losslessly spatially partition the static island GLB (run with Blender).

Usage: blender --background --python tools/partition_island.py -- INPUT OUTPUT
Keeps triangle winding and every vertex attribute byte; only batches change.
"""
import collections
import copy
import json
import pathlib
import struct
import sys


def read_glb(path):
    data = pathlib.Path(path).read_bytes()
    assert struct.unpack_from('<III', data) == (0x46546C67, 2, len(data))
    size, kind = struct.unpack_from('<II', data, 12)
    assert kind == 0x4E4F534A
    doc = json.loads(data[20:20 + size])
    bin_size, bin_kind = struct.unpack_from('<II', data, 20 + size)
    assert bin_kind == 0x004E4942
    return doc, data[28 + size:28 + size + bin_size]


def rows(doc, binary, index):
    accessor = doc['accessors'][index]
    assert 'sparse' not in accessor
    view = doc['bufferViews'][accessor['bufferView']]
    size = {5121: 1, 5123: 2, 5125: 4, 5126: 4}[accessor['componentType']]
    size *= {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[accessor['type']]
    offset = view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
    stride = view.get('byteStride', size)
    return [binary[offset + i * stride:offset + i * stride + size]
            for i in range(accessor['count'])]


def triangles(doc, binary, primitive):
    accessor = doc['accessors'][primitive['indices']]
    fmt = {5121: '<B', 5123: '<H', 5125: '<I'}[accessor['componentType']]
    indices = [struct.unpack(fmt, row)[0] for row in rows(doc, binary, primitive['indices'])]
    assert len(indices) % 3 == 0 and primitive.get('mode', 4) == 4
    return [indices[i:i + 3] for i in range(0, len(indices), 3)]


def signature(doc, binary):
    result = collections.Counter()
    for mesh in doc['meshes']:
        for primitive in mesh['primitives']:
            attributes = [rows(doc, binary, index) for name, index in
                          sorted(primitive['attributes'].items())]
            for triangle in triangles(doc, binary, primitive):
                result[(primitive.get('material'), tuple(
                    b''.join(attribute[i] for attribute in attributes) for i in triangle))] += 1
    return result


def partition(source, destination):
    doc, binary = read_glb(source)
    assert not doc.get('animations') and not doc.get('skins') and not doc.get('images')
    before = signature(doc, binary)
    out = copy.deepcopy(doc)
    out['accessors'], out['bufferViews'] = [], []
    buffer = bytearray()

    def append_accessor(template, data, target, positions=None):
        while len(buffer) % 4:
            buffer.append(0)
        content = b''.join(data)
        view = len(out['bufferViews'])
        out['bufferViews'].append(dict(buffer=0, byteOffset=len(buffer), byteLength=len(content), target=target))
        buffer.extend(content)
        accessor = {k: v for k, v in template.items() if k not in
                    ('bufferView', 'byteOffset', 'count', 'min', 'max')}
        accessor.update(bufferView=view, count=len(data))
        if positions is not None:
            accessor['min'] = [min(p[axis] for p in positions) for axis in range(3)]
            accessor['max'] = [max(p[axis] for p in positions) for axis in range(3)]
        out['accessors'].append(accessor)
        return len(out['accessors']) - 1

    for original, mesh in zip(doc['meshes'], out['meshes']):
        mesh['primitives'] = []
        for primitive in original['primitives']:
            assert not primitive.get('targets') and not primitive.get('extensions')
            attrs = {name: rows(doc, binary, index) for name, index in primitive['attributes'].items()}
            positions = [struct.unpack('<fff', row) for row in attrs['POSITION']]
            tris = triangles(doc, binary, primitive)
            centers = [tuple(sum(positions[i][axis] for i in tri) / 3 for axis in range(3)) for tri in tris]
            leaves = []

            def split(ids):
                if len(ids) <= 256:
                    leaves.append(ids)
                    return
                spans = [max(centers[i][axis] for i in ids) - min(centers[i][axis] for i in ids) for axis in range(3)]
                axis = max(range(3), key=lambda a: spans[a])
                ids.sort(key=lambda i: centers[i][axis])
                half = len(ids) // 2
                split(ids[:half])
                split(ids[half:])

            split(list(range(len(tris))))
            for leaf in leaves:
                used = sorted({i for t in leaf for i in tris[t]})
                remap = {old: new for new, old in enumerate(used)}
                part = copy.deepcopy(primitive)
                part['attributes'] = {
                    name: append_accessor(doc['accessors'][primitive['attributes'][name]],
                        [data[i] for i in used], 34962,
                        [positions[i] for i in used] if name == 'POSITION' else None)
                    for name, data in attrs.items()}
                part['indices'] = append_accessor({'componentType': 5123, 'type': 'SCALAR'},
                    [struct.pack('<H', remap[i]) for t in leaf for i in tris[t]], 34963)
                mesh['primitives'].append(part)
    out['buffers'] = [dict(byteLength=len(buffer))]
    encoded = json.dumps(out, separators=(',', ':')).encode()
    encoded += b' ' * (-len(encoded) % 4)
    buffer += b'\0' * (-len(buffer) % 4)
    payload = (struct.pack('<III', 0x46546C67, 2, 28 + len(encoded) + len(buffer)) +
        struct.pack('<II', len(encoded), 0x4E4F534A) + encoded +
        struct.pack('<II', len(buffer), 0x004E4942) + buffer)
    assert before == signature(out, buffer), 'Triangle/material/attribute preservation failed'
    assert out['nodes'] == doc['nodes'] and out['materials'] == doc['materials']
    pathlib.Path(destination).write_bytes(payload)
    check_doc, check_bin = read_glb(destination)
    assert signature(check_doc, check_bin) == before
    print(json.dumps(dict(triangles=before.total(), bytes=len(payload),
        primitivesBefore=sum(len(m['primitives']) for m in doc['meshes']),
        primitivesAfter=sum(len(m['primitives']) for m in out['meshes']),
        exactTriangleAttributesPreserved=True)))


if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--') + 1:]
    partition(*args)
