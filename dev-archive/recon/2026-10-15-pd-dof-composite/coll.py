import re, struct, sys
data = open(sys.argv[1], 'rb').read()
d = {}
for m in re.finditer(b'DXBC', data):
    o = m.start()
    names = re.findall(rb'[A-Za-z0-9_\.]{3,}', data[max(0, o - 256):o]); name = names[-1].decode() if names else '?'
    d.setdefault(data[o+4:o+20], set()).add(name)
for k, v in d.items():
    if any(n.startswith('dof') for n in v) and len(v) > 1: print(sorted(v))
print('done')
