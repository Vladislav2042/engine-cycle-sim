import pickle
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from engine_data import CONSTANTS

DURATION = 10.0
FPS = 10
TOTAL_FRAMES = int(DURATION * FPS)
output_video = 'cycle_animation_mipcc.mp4'

try:
    with open('cycle_cache.pkl', 'rb') as f:
        cache = pickle.load(f)
    print("Cache loaded.")
except FileNotFoundError:
    print("cycle_cache.pkl not found. Run precompute_cache.py first.")
    exit()

heights = list(range(4, 15))
mach_list = np.arange(0.5, 3.05, 0.1).round(2)

def get_nearest_mach(M):
    M = min(M, 2.8)
    idx = np.argmin(np.abs(np.array(mach_list) - M))
    return mach_list[idx]

def isobar_curve(s_start, T_start, s_end, cp, num=120):
    s_vals = np.linspace(s_start, s_end, num)
    T_vals = T_start * np.exp((s_vals - s_start) / cp)
    return s_vals, T_vals

def polytrope_curve(s_start, T_start, s_end, T_end, num=120):
    s_vals = np.linspace(s_start, s_end, num)
    logT_start = np.log(T_start)
    logT_end = np.log(T_end)
    logT_vals = np.interp(s_vals, [s_start, s_end], [logT_start, logT_end])
    T_vals = np.exp(logT_vals)
    return s_vals, T_vals

def add_arrow(s_curve, T_curve, ax, pos=0.65, color='red', size=12):
    if len(s_curve) < 2:
        return
    idx = int(pos * (len(s_curve) - 1))
    idx = min(idx, len(s_curve) - 2)
    x1, y1 = s_curve[idx], T_curve[idx]
    x2, y2 = s_curve[idx+1], T_curve[idx+1]
    return ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                       arrowprops=dict(arrowstyle='->', color=color, lw=1.5))

frames = []
for i in range(TOTAL_FRAMES):
    t = i / (TOTAL_FRAMES - 1) if TOTAL_FRAMES > 1 else 0
    H = int(round(4 + t * (14 - 4)))
    M_cont = 0.5 + t * (2.8 - 0.5)
    M = get_nearest_mach(M_cont)
    key = (H, M)
    if key in cache and cache[key] is not None:
        s_vals, T_vals, labels, cp_close = cache[key]
        frames.append((H, M, s_vals, T_vals, labels, cp_close))
    else:
        if frames:
            frames.append(frames[-1])
        else:
            print("No valid frames.")
            exit()

print(f"Prepared {len(frames)} frames")

fig, ax = plt.subplots(figsize=(11, 7.5))
plt.subplots_adjust(left=0.12, bottom=0.12)

all_s = []
all_T = []
for (_, _, s, T, _, _) in frames:
    all_s.extend(s)
    all_T.extend(T)
s_min, s_max = min(all_s), max(all_s)
T_min, T_max = min(all_T), max(all_T)
s_margin = 0.05 * (s_max - s_min) if s_max > s_min else 50
T_margin = 0.05 * (T_max - T_min) if T_max > T_min else 50
ax.set_xlim(s_min - s_margin, s_max + s_margin)
ax.set_ylim(T_min - T_margin, T_max + T_margin)
ax.set_xlabel('Specific entropy s, J/(kg·K)', fontsize=12)
ax.set_ylabel('Temperature T, K', fontsize=12)
ax.grid(True, linestyle='--', alpha=0.5)

lines = []
arrows = []
points, = ax.plot([], [], 'ro', markersize=7, zorder=5)
annotations = []
max_labels = max(len(f[4]) for f in frames)
for _ in range(max_labels):
    ann = ax.annotate("", xy=(0,0), xytext=(7,7), textcoords='offset points',
                      fontsize=11, fontweight='bold', ha='center')
    annotations.append(ann)

title = ax.set_title('', fontsize=13, fontweight='bold')

def init():
    points.set_data([], [])
    for ann in annotations:
        ann.set_text("")
    title.set_text("")
    for line in lines:
        line.remove()
    for arrow in arrows:
        arrow.remove()
    lines.clear()
    arrows.clear()
    return [points, title] + annotations

def animate(i):
    H, M, s_vals, T_vals, labels, cp_close = frames[i]

    for line in lines:
        line.remove()
    for arrow in arrows:
        arrow.remove()
    lines.clear()
    arrows.clear()

    for k in range(len(s_vals)-1):
        s1, s2 = s_vals[k], s_vals[k+1]
        T1, T2 = T_vals[k], T_vals[k+1]
        p1, p2 = labels[k], labels[k+1]

        if (p1 == '2' and p2 == '2c') or (p1 == '8' and p2 == '1'):
            cp = CONSTANTS['mix']['cp'] if p1 == '2' else cp_close
            s_curv, T_curv = isobar_curve(s1, T1, s2, cp, 180)
            line, = ax.plot(s_curv, T_curv, 'red', linewidth=2.2, zorder=2)
            lines.append(line)
            arr = add_arrow(s_curv, T_curv, ax, color='red')
            if arr:
                arrows.append(arr)
        elif p1 == '4' and p2 == '5':
            s_curv, T_curv = polytrope_curve(s1, T1, s2, T2, 150)
            line, = ax.plot(s_curv, T_curv, 'red', linewidth=2.2, zorder=2)
            lines.append(line)
            arr = add_arrow(s_curv, T_curv, ax, color='red')
            if arr:
                arrows.append(arr)
        else:
            s_curv = np.array([s1, s2])
            T_curv = np.array([T1, T2])
            line, = ax.plot(s_curv, T_curv, 'red', linewidth=2.2, zorder=2)
            lines.append(line)
            arr = add_arrow(s_curv, T_curv, ax, color='red')
            if arr:
                arrows.append(arr)

    points.set_data(s_vals, T_vals)

    for j, (s, T, lbl) in enumerate(zip(s_vals, T_vals, labels)):
        if j < len(annotations):
            display = "6'" if lbl == '6p' else lbl
            annotations[j].xy = (s, T)
            annotations[j].set_text(display)
    for j in range(len(s_vals), len(annotations)):
        annotations[j].set_text("")

    title.set_text(f'AL-31 with MIPCC\nH = {H} km, M = {M:.2f}')

    return [points, title] + annotations + lines + arrows

ani = animation.FuncAnimation(fig, animate, init_func=init,
                              frames=len(frames), interval=1000/FPS, blit=False)

try:
    writer = animation.FFMpegWriter(fps=FPS, bitrate=2000)
    ani.save(output_video, writer=writer)
    print(f"Video saved as {output_video}")
except Exception as e:
    print(f"Cannot save video: {e}")
    print("Displaying animation on screen...")
    plt.show()