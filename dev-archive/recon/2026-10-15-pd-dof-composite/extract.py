import re, struct, sys, os
src, out, pat = sys.argv[1], sys.argv[2], sys.argv[3]
data = open(src, 'rb').read()
os.makedirs(out, exist_ok=True)
rows = []
for m in re.finditer(b'DXBC', data):
    o = m.start()
    size = struct.unpack_from('<I', data, o + 24)[0]
    # name: last printable run of >=3 chars in the 256 bytes before the blob
    pre = data[max(0, o - 256):o]
    names = re.findall(rb'[A-Za-z0-9_\.]{3,}', pre)
    name = names[-1].decode() if names else '?'
    chk = data[o + 4:o + 20]
    # shader type from SHEX version token
    shex = data.find(b'SHEX', o, o + size)
    kind = '?'
    if shex > 0:
        ver = struct.unpack_from('<I', data, shex + 8)[0]
        kind = {0: 'ps', 1: 'vs', 2: 'gs', 3: 'hs', 4: 'ds', 5: 'cs'}.get(ver >> 16, '?')
    rows.append((o, size, name, kind, chk.hex()))
    if re.search(pat, name):
        fn = os.path.join(out, '%s_%s_%08x.cso' % (name, kind, o))
        open(fn, 'wb').write(data[o:o + size])
print(len(rows), 'blobs')
for r in rows:
    if re.search(pat, r[2]):
        print('%08x %6d %-40s %s %s' % r)
