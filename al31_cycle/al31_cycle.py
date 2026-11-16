import numpy as np
import matplotlib.pyplot as plt


points = {
    '1':  {'T': 230.0,   'P': 30790.0},
    '2':  {'T': 265.62,  'P': 49438.0},
    '3':  {'T': 401.57,  'P': 175010.0},
    '4':  {'T': 738.16,  'P': 1130567.0},
    '5':  {'T': 1665.0,  'P': 1063864.0},
    '6':  {'T': 1316.28, 'P': 366850.0},
    '6p': {'T': 1291.38, 'P': 366850.0},
    '7':  {'T': 1068.98, 'P': 159500.0},
    '8':  {'T': 710.0,   'P': 30790.0}
}

cp_air = 1005      # J/(kg·K)
R_air = 287        # J/(kg·K)
cp_gas = 1165      # J/(kg·K)
R_gas = 293        # J/(kg·K)

def delta_s(T1, T2, P1, P2, cp, R):
    return cp * np.log(T2 / T1) - R * np.log(P2 / P1)


s_nodes = [0.0]
T_nodes = [points['1']['T']]
labels = ['1']

# 1→2→3→4 (air)
for i, nxt in [('1','2'), ('2','3'), ('3','4')]:
    ds = delta_s(points[i]['T'], points[nxt]['T'],
                 points[i]['P'], points[nxt]['P'],
                 cp_air, R_air)
    s_nodes.append(s_nodes[-1] + ds)
    T_nodes.append(points[nxt]['T'])
    labels.append(nxt)

# 4→5 (combustor, gas)
ds = delta_s(points['4']['T'], points['5']['T'],
             points['4']['P'], points['5']['P'],
             cp_gas, R_gas)
s_nodes.append(s_nodes[-1] + ds)
T_nodes.append(points['5']['T'])
labels.append('5')

# 5→6→6p→7→8 (gas)
for i, nxt in [('5','6'), ('6','6p'), ('6p','7'), ('7','8')]:
    ds = delta_s(points[i]['T'], points[nxt]['T'],
                 points[i]['P'], points[nxt]['P'],
                 cp_gas, R_gas)
    s_nodes.append(s_nodes[-1] + ds)
    T_nodes.append(points[nxt]['T'])
    labels.append(nxt)

# 8→1 closing isobar (effective cp to force s1 = 0)
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

def add_arrow(s_curve, T_curve, pos=0.7, color='black', size=12):
    if len(s_curve) < 2:
        return
    idx = int(pos * (len(s_curve) - 1))
    idx = min(idx, len(s_curve) - 2)
    s1, T1 = s_curve[idx], T_curve[idx]
    s2, T2 = s_curve[idx+1], T_curve[idx+1]
    plt.annotate('', xy=(s2, T2), xytext=(s1, T1),
                 arrowprops=dict(arrowstyle='->', color=color, lw=1.5, shrinkA=0, shrinkB=0))


plt.figure(figsize=(11, 7.5))

curves = []


for k in range(len(s_nodes) - 2):
    s1k, s2k = s_nodes[k], s_nodes[k+1]
    T1k, T2k = T_nodes[k], T_nodes[k+1]
    p1, p2 = labels[k], labels[k+1]

    # Isobar only for mixing (6-6p); others use polytrope (including 4-5)
    if p1 == '6' and p2 == '6p':
        s_c, T_c = isobar_curve(s1k, T1k, s2k, cp_gas, 150)
        plt.plot(s_c, T_c, 'b-', linewidth=2.2)
        curves.append((s_c, T_c))
    else:
        s_c, T_c = polytrope_curve(s1k, T1k, s2k, T2k, 150)
        plt.plot(s_c, T_c, 'b-', linewidth=2.2)
        curves.append((s_c, T_c))


s8_val = s_nodes[-2]
T8_val = T_nodes[-2]
s1_val = s_nodes[-1]
T1_val = T_nodes[-1]
s_close, T_close = isobar_curve(s8_val, T8_val, s1_val, cp_closure, 180)
plt.plot(s_close, T_close, 'b-', linewidth=2.2, label='Isobar 8→1 (cooling)')
curves.append((s_close, T_close))


for s_c, T_c in curves:
    add_arrow(s_c, T_c, pos=0.65, color='black', size=12)


s_arr = np.array(s_nodes)
T_arr = np.array(T_nodes)
plt.plot(s_arr, T_arr, 'ro', markersize=7, zorder=5)


for i, lbl in enumerate(labels):
    if lbl == '6p':
        display_label = "6'"
    else:
        display_label = lbl
    plt.annotate(display_label, (s_arr[i], T_arr[i]), textcoords="offset points",
                 xytext=(7, 7), ha='center', fontsize=11, fontweight='bold')


plt.title('T‑s Diagram of the AL‑31 Engine Cycle (closed)\n'
          'H = 9000 m, M = 0.88, cp_gas = 1165 J/(kg·K)',
          fontsize=13, fontweight='bold')
plt.xlabel('Specific entropy s, J/(kg·K)', fontsize=12)
plt.ylabel('Temperature T, K', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(loc='lower right')
plt.tight_layout()
plt.show()

print(f"Effective cp for 8→1 isobar: {cp_closure:.1f} J/(kg·K)")