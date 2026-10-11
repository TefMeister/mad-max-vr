"""List the shader bundle's DXBC blobs with the readable name stored before each; optionally disassemble matches.
usage: mm_named.py <bundle> <regex> [outdir]"""
import re, sys, struct, ctypes, os
data = open(sys.argv[1], 'rb').read()
pat = re.compile(sys.argv[2], re.I)
out = sys.argv[3] if len(sys.argv) > 3 else None
d3dc = ctypes.WinDLL('d3dcompiler_47.dll')
D = d3dc.D3DDisassemble
D.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_uint, ctypes.c_char_p, ctypes.POINTER(ctypes.c_void_p)]
def disasm(blob):
    p = ctypes.c_void_p()
    if D(blob, len(blob), 0, None, ctypes.byref(p)) != 0: return None
    vt = ctypes.cast(ctypes.cast(p, ctypes.POINTER(ctypes.c_void_p))[0], ctypes.POINTER(ctypes.c_void_p))
    getptr = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p)(vt[3])
    getsize = ctypes.CFUNCTYPE(ctypes.c_size_t, ctypes.c_void_p)(vt[4])
    return ctypes.string_at(getptr(p), getsize(p)).decode(errors='replace')
idx = 0; pos = 0; rows = []
while True:
    i = data.find(b'DXBC', pos)
    if i < 0: break
    size = struct.unpack_from('<I', data, i + 24)[0]
    back = data[max(0, i - 200):i]
    names = re.findall(rb'[A-Za-z0-9_]{4,}', back)
    name = names[-1].decode() if names else '?'
    blob = data[i:i + size]
    kind = 'VS' if b'SHEX' in blob and blob[blob.find(b'SHEX') + 10:blob.find(b'SHEX') + 12] == b'\x01\x00' else '??'
    rows.append((idx, i, size, name))
    if pat.search(name):
        txt = disasm(blob)
        first = [l for l in (txt or '').splitlines() if l.startswith(('vs_', 'ps_', 'cs_', 'gs_'))]
        print(idx, hex(i), size, name, first[0] if first else '')
        if out and txt:
            os.makedirs(out, exist_ok=True)
            open(os.path.join(out, f'{idx:04d}_{name}.asm'), 'w').write(txt)
    idx += 1; pos = i + max(size, 4)
print('total blobs', idx)
