import re, struct, sys
data = open(sys.argv[1], 'rb').read()
allchk = {}
out = []
for m in re.finditer(b'DXBC', data):
    o = m.start(); size = struct.unpack_from('<I', data, o + 24)[0]
    names = re.findall(rb'[A-Za-z0-9_\.]{3,}', data[max(0, o - 256):o]); name = names[-1].decode() if names else '?'
    chk = data[o + 4:o + 20]
    allchk.setdefault(chk, []).append(name)
    kind = 1 if name.startswith('dof_') else 2 if name.startswith('dofbokeh_') else 0
    if kind:
        out.append((kind, name, chk))
dups = [v for v in allchk.values() if len(v) > 1]
print('/* unique checksums:', len(allchk), 'of', sum(len(v) for v in allchk.values()), 'blobs; collisions among them:', len(dups), '*/', file=sys.stderr)
for kind, name, chk in out:
    words = struct.unpack('<4I', chk)
    print('    { %d, { 0x%08xu, 0x%08xu, 0x%08xu, 0x%08xu } },   /* %s */' % ((kind,) + words + (name,)))
print(len(out), file=sys.stderr)
