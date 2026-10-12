"""Tiny Mad Max driver: find window, send scancode keys, BitBlt screenshot of the client area, close.
usage: mm.py find | key NAME [holdms] [count] | shot FILE | close | numlock"""
import ctypes, ctypes.wintypes as W, sys, time
from PIL import Image

u = ctypes.windll.user32; g = ctypes.windll.gdi32
u.SetProcessDPIAware()
SC = {"enter": (0x1C, 0), "esc": (0x01, 0), "up": (0x48, 1), "down": (0x50, 1), "left": (0x4B, 1), "right": (0x4D, 1),
      "w": (0x11, 0), "a": (0x1E, 0), "s": (0x1F, 0), "d": (0x20, 0), "v": (0x2F, 0), "r": (0x13, 0), "space": (0x39, 0),
      "n7": (0x47, 0), "n8": (0x48, 0), "n9": (0x49, 0), "n4": (0x4B, 0), "n5": (0x4C, 0), "n6": (0x4D, 0),
      "n1": (0x4F, 0), "n2": (0x50, 0), "n3": (0x51, 0), "n0": (0x52, 0), "ndot": (0x53, 0), "numlock": (0x45, 0)}


class KI(ctypes.Structure):
    _fields_ = [("wVk", W.WORD), ("wScan", W.WORD), ("dwFlags", W.DWORD), ("time", W.DWORD), ("extra", ctypes.c_size_t)]


class INP(ctypes.Structure):
    class _U(ctypes.Union):
        _fields_ = [("ki", KI), ("pad", ctypes.c_byte * 32)]
    _anonymous_ = ("u",)
    _fields_ = [("type", W.DWORD), ("u", _U)]


def send(sc, ext, up):
    i = INP(); i.type = 1
    i.ki = KI(0, sc, 0x0008 | (0x0001 if ext else 0) | (0x0002 if up else 0), 0, 0)
    u.SendInput(1, ctypes.byref(i), ctypes.sizeof(i))


def find():
    res = []
    @ctypes.WINFUNCTYPE(W.BOOL, W.HWND, W.LPARAM)
    def cb(h, _):
        if u.IsWindowVisible(h):
            pid = W.DWORD(); u.GetWindowThreadProcessId(h, ctypes.byref(pid))
            b = ctypes.create_unicode_buffer(256); u.GetWindowTextW(h, b, 256)
            if "Mad Max" in b.value: res.append(h)
        return True
    u.EnumWindows(cb, 0)
    return res[0] if res else None


def fg(h):
    u.ShowWindow(h, 9); u.SetForegroundWindow(h); time.sleep(0.3)


def key(name, hold=250, count=1):
    sc, ext = SC[name]
    h = find()
    if h and not name.startswith("n"): fg(h)
    for _ in range(count):
        send(sc, ext, False); time.sleep(hold / 1000); send(sc, ext, True); time.sleep(0.35)


def shot(fn):
    h = find(); fg(h)
    r = W.RECT(); u.GetClientRect(h, ctypes.byref(r)); p = W.POINT(0, 0); u.ClientToScreen(h, ctypes.byref(p))
    w, hh = r.right, r.bottom
    sdc = u.GetDC(0); mdc = g.CreateCompatibleDC(sdc); bm = g.CreateCompatibleBitmap(sdc, w, hh)
    g.SelectObject(mdc, bm); g.BitBlt(mdc, 0, 0, w, hh, sdc, p.x, p.y, 0x00CC0020)
    class BIH(ctypes.Structure):
        _fields_ = [("a", W.DWORD), ("w", W.LONG), ("h", W.LONG), ("p", W.WORD), ("b", W.WORD), ("c", W.DWORD),
                    ("s", W.DWORD), ("x", W.LONG), ("y", W.LONG), ("u", W.DWORD), ("i", W.DWORD)]
    bi = BIH(40, w, -hh, 1, 32, 0, 0, 0, 0, 0, 0)
    buf = ctypes.create_string_buffer(w * hh * 4)
    g.GetDIBits(mdc, bm, 0, hh, buf, ctypes.byref(bi), 0)
    Image.frombuffer("RGBA", (w, hh), buf, "raw", "BGRA", 0, 1).convert("RGB").save(fn)
    g.DeleteObject(bm); g.DeleteDC(mdc); u.ReleaseDC(0, sdc)
    print(fn, w, hh)


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "find":
        h = find(); print(h)
        if h:
            r = W.RECT(); u.GetClientRect(h, ctypes.byref(r)); print("client", r.right, r.bottom,
                  "screen", u.GetSystemMetrics(0), u.GetSystemMetrics(1))
    elif c == "key": key(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 250, int(sys.argv[4]) if len(sys.argv) > 4 else 1)
    elif c == "shot": shot(sys.argv[2])
    elif c == "close": u.PostMessageW(find(), 0x0010, 0, 0)
    elif c == "numlock":
        if not (u.GetKeyState(0x90) & 1): key("numlock", 60)
        print("numlock", u.GetKeyState(0x90) & 1)
