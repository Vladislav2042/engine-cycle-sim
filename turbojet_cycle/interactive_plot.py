import pickle
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from engine_data import cp_gas

# Загрузка кэша
try:
    with open('cycle_cache.pkl', 'rb') as f:
        cache = pickle.load(f)
except FileNotFoundError:
    print("Cache not found. Run precompute_cache.py first.")
    exit()

heights = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
mach_list = np.arange(0.5, 3.05, 0.1).round(2)

def smooth_isobar(s_start, T_start, s_end, cp, num=120):
    s_vals = np.linspace(s_start, s_end, num)
    T_vals = T_start * np.exp((s_vals - s_start) / cp)
    return s_vals, T_vals

def smooth_polytrope(s_start, T_start, s_end, T_end, num=120):
    s_vals = np.linspace(s_start, s_end, num)
    logT_start = np.log(T_start)
    logT_end = np.log(T_end)
    logT_vals = np.interp(s_vals, [s_start, s_end], [logT_start, logT_end])
    T_vals = np.exp(logT_vals)
    return s_vals, T_vals

def get_nearest_mach(M):
    idx = np.argmin(np.abs(np.array(mach_list) - M))
    return mach_list[idx]

# Начальные параметры
H0 = 9
M0 = 0.88
M_actual = get_nearest_mach(M0)
s0, T0, labels0, cp_close0 = cache[(H0, M_actual)]

fig, ax = plt.subplots(figsize=(10, 7))
plt.subplots_adjust(bottom=0.2)

def update_plot():
    ax.clear()
    curves = []
    for k in range(len(s0)-1):
        s1, s2 = s0[k], s0[k+1]
        T1, T2 = T0[k], T0[k+1]
        p1, p2 = labels0[k], labels0[k+1]
        if p1 == '6' and p2 == '6p':
            s_curv, T_curv = smooth_isobar(s1, T1, s2, cp_gas, 150)
        elif p1 == '8' and p2 == '1':
            s_curv, T_curv = smooth_isobar(s1, T1, s2, cp_close0, 150)
        else:
            s_curv, T_curv = smooth_polytrope(s1, T1, s2, T2, 150)
        ax.plot(s_curv, T_curv, 'b-', linewidth=2)
        curves.append((s_curv, T_curv))
    for s_c, T_c in curves:
        idx = int(0.65 * (len(s_c)-1))
        if idx < len(s_c)-1:
            ax.annotate('', xy=(s_c[idx+1], T_c[idx+1]), xytext=(s_c[idx], T_c[idx]),
                        arrowprops=dict(arrowstyle='->', color='black', lw=1))
    ax.plot(s0, T0, 'ro', markersize=6)
    for i, lbl in enumerate(labels0):
        display = "6'" if lbl == '6p' else lbl
        ax.annotate(display, (s0[i], T0[i]), xytext=(5,5), textcoords='offset points',
                    fontsize=10, fontweight='bold')
    ax.set_xlabel('Specific entropy s, J/(kg·K)')
    ax.set_ylabel('Temperature T, K')
    ax.set_title(f'T-s Diagram of AL-31\nH = {H0} km, M = {M0:.2f}')
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_xlim(min(s0)-50, max(s0)+50)
    ax.set_ylim(min(T0)-50, max(T0)+100)
    fig.canvas.draw_idle()

def update(val):
    global H0, M0, s0, T0, labels0, cp_close0
    H0 = int(slider_h.val)
    M0 = slider_m.val
    M_actual = get_nearest_mach(M0)
    key = (H0, M_actual)
    if key in cache and cache[key] is not None:
        s0, T0, labels0, cp_close0 = cache[key]
    else:
        # fallback: пересчитать напрямую (на случай, если кэш неполный)
        from engine_data import calculate_cycle
        s0, T0, labels0, cp_close0 = calculate_cycle(H0, M_actual)
    update_plot()

ax_h = plt.axes([0.2, 0.05, 0.6, 0.03])
ax_m = plt.axes([0.2, 0.1, 0.6, 0.03])
slider_h = Slider(ax_h, 'Altitude (km)', 4, 14, valinit=H0, valstep=1)
slider_m = Slider(ax_m, 'Mach number', 0.5, 3.0, valinit=M0, valstep=0.01)

slider_h.on_changed(update)
slider_m.on_changed(update)

update_plot()
plt.show()
