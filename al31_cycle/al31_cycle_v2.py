import numpy as np
import matplotlib.pyplot as plt

points = {
    '1':  {'T': 230.0,    'P': 30790.0},
    '2':  {'T': 265.62,   'P': 49438.0},
    '2c': {'T': 248.59,   'P': 49438.0},
    '3':  {'T': 383.035,  'P': 186381.0},
    '4':  {'T': 712.82,   'P': 1258072.0},
    '5':  {'T': 1712.49,  'P': 1183846.0},
    '6':  {'T': 1498.23,  'P': 642820.0},
    '6p': {'T': 1580.5,   'P': 642820.0},
    '7':  {'T': 1495.78,  'P': 503224.0},
    '8':  {'T': 990.18,   'P': 30790.0}
}

segments = [
    ('1', '2',   1012, 287.0),
    ('2', '2c',  1012, 288.5),
    ('2c', '3',  1012, 288.5),
    ('3', '4',   1012, 288.5),
    ('4', '5',   1491, 293.0),
    ('5', '6',   1661, 293.0),
    ('6', '6p',  1661, 293.0),
    ('6p', '7',  1005, 287.0),
    ('7', '8',   1165, 293.0)
]

def delta_s(T1, T2, P1, P2, cp, R):
    return cp * np.log(T2 / T1) - R * np.log(P2 / P1)

s_nodes = [0.0]
T_nodes = [points['1']['T']]
labels = ['1']

for from_key, to_key, cp, R in segments:
    T1, P1 = points[from_key]['T'], points[from_key]['P']
    T2, P2 = points[to_key]['T'],   points[to_key]['P']
    ds = delta_s(T1, T2, P1, P2, cp, R)
    s_nodes.append(s_nodes[-1] + ds)
    T_nodes.append(T2)
    labels.append(to_key)

s8 = s_nodes[-1]
T8 = points['8']['T']
s1 = 0.0
T1 = points['1']['T']
cp_closure = (s1 - s8) / np.log(T1 / T8)
s_nodes.append(s1)
T_nodes.append(T1)
labels.append('1')

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

def add_arrow(s_curve, T_curve, pos=0.65, color='black', size=12):
    if len(s_curve) < 2:
        return
    idx = int(pos * (len(s_curve) - 1))
    idx = min(idx, len(s_curve) - 2)
    x1, y1 = s_curve[idx], T_curve[idx]
    x2, y2 = s_curve[idx+1], T_curve[idx+1]
    plt.annotate('', xy=(x2, y2), xytext=(x1, y1),
                 arrowprops=dict(arrowstyle='->', color=color, lw=1.5))

plt.figure(figsize=(11, 7.5))
curves = []

for k in range(len(s_nodes) - 2):
    s1k, s2k = s_nodes[k], s_nodes[k+1]
    T1k, T2k = T_nodes[k], T_nodes[k+1]
    p1, p2 = labels[k], labels[k+1]

    if p1 == '4' and p2 == '5':
        s_c, T_c = polytrope_curve(s1k, T1k, s2k, T2k, 150)
    elif p1 == '8' and p2 == '1':
        continue
    else:
        s_c = np.array([s1k, s2k])
        T_c = np.array([T1k, T2k])

    plt.plot(s_c, T_c, color='red', linewidth=2.2)
    curves.append((s_c, T_c))

s8_val, T8_val = s_nodes[-2], T_nodes[-2]
s1_val, T1_val = s_nodes[-1], T_nodes[-1]
s_close, T_close = isobar_curve(s8_val, T8_val, s1_val, cp_closure, 180)
plt.plot(s_close, T_close, color='red', linewidth=2.2, label='Isobar 8→1 (cooling)')
curves.append((s_close, T_close))

for s_c, T_c in curves:
    add_arrow(s_c, T_c, pos=0.65, color='red', size=12)

s_arr = np.array(s_nodes)
T_arr = np.array(T_nodes)
plt.plot(s_arr, T_arr, 'ro', markersize=7, zorder=5)

for i, lbl in enumerate(labels):
    if lbl == '6p':
        display_label = "6'"
    elif lbl == '2c':
        display_label = '2c'
    else:
        display_label = lbl
    plt.annotate(display_label, (s_arr[i], T_arr[i]),
                 textcoords='offset points', xytext=(7, 7),
                 ha='center', fontsize=11, fontweight='bold')

plt.title('T–s Diagram of the AL‑31 Engine Cycle with MIPCC\n'
          'H = 9000 m, M = 0.88',
          fontsize=13, fontweight='bold')
plt.xlabel('Specific entropy s, J/(kg·K)', fontsize=12)
plt.ylabel('Temperature T, K', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(loc='lower right')
plt.tight_layout()
plt.show()

print(f"Effective cp for 8→1 isobar: {cp_closure:.1f} J/(kg·K)")