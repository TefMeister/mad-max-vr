import sys, time, os, ctypes
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import game_harness as gh
S = os.path.dirname(os.path.abspath(__file__))
hwnd, _ = gh.find_window("Mad Max"); gh.focus(hwnd)
u = gh.u
def screen(cx, cy):
    pt = gh.w.POINT(int(cx), int(cy)); u.ClientToScreen(hwnd, ctypes.byref(pt)); return pt.x, pt.y
def btn(flag):
    i = gh.INPUT(type=gh.INPUT_MOUSE, u=gh._I(mi=gh.MOUSEINPUT(0, 0, 0, flag, 0, None)))
    u.SendInput(1, ctypes.byref(i), ctypes.sizeof(gh.INPUT))
def drag(x0, y0, x1, y1, steps=20):
    sx, sy = screen(x0, y0); ex, ey = screen(x1, y1)
    u.SetCursorPos(sx, sy); time.sleep(0.2); btn(gh.MOUSEEVENTF_LEFTDOWN); time.sleep(0.15)
    for k in range(1, steps+1):
        u.SetCursorPos(int(sx + (ex-sx)*k/steps), int(sy + (ey-sy)*k/steps)); time.sleep(0.03)
    time.sleep(0.15); btn(gh.MOUSEEVENTF_LEFTUP); time.sleep(0.5)
gh.click(hwnd, 85, 174); time.sleep(0.8); gh.grab(hwnd).save(f"{S}/19a.png")
for _ in range(6): gh.click(hwnd, 272, 189); time.sleep(0.25)
time.sleep(0.8); gh.grab(hwnd).save(f"{S}/19b.png"); gh.hold("numpad3", 0.3); time.sleep(1.2)
drag(162, 189, 258, 189); time.sleep(0.8); gh.grab(hwnd).save(f"{S}/19c.png"); gh.hold("numpad3", 0.3); time.sleep(1.2)
print("done")
