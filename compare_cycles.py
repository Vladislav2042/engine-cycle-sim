import numpy as np
import matplotlib.pyplot as plt

points1 = {
    '1': {'T': 230.0,   'P': 30790.0},
    '2': {'T': 265.62,  'P': 49438.0},
    '3': {'T': 401.57,  'P': 175010.0},
    '4': {'T': 738.16,  'P': 1130567.0},
    '5': {'T': 1665.0,  'P': 1063864.0},
    '6': {'T': 1316.28, 'P': 366850.0},
    '6p':{'T': 1291.38, 'P': 366850.0},
    '7': {'T': 1068.98, 'P': 159500.0},
    '8': {'T': 710.0,   'P': 30790.0}
}
cp_air = 1005
R_air = 287
cp_gas = 1165
R_gas = 293

def delta_s(T1, T2, P1, P2, cp, R):
    return cp * np.log(T2 / T1) - R * np.log(P2 / P1)

s1 = [0.0]
T1 = [points1['1']['T']]
labels1 = ['1']
for a, b in [('1','2'), ('2','3'), ('3','4')]:
    ds = delta_s(points1[a]['T'], points1[b]['T'], points1[a]['P'], points1[b]['P'], cp_air, R_air)
    s1.append(s1[-1] + ds)
    T1.append(points1[b]['T'])
    labels1.append(b)
ds = delta_s(points1['4']['T'], points1['5']['T'], points1['4']['P'], points1['5']['P'], cp_gas, R_gas)
s1.append(s1[-1] + ds)
T1.append(points1['5']['T'])
labels1.append('5')
for a, b in [('5','6'), ('6','6p'), ('6p','7'), ('7','8')]:
    ds = delta_s(points1[a]['T'], points1[b]['T'], points1[a]['P'], points1[b]['P'], cp_gas, R_gas)
    s1.append(s1[-1] + ds)
    T1.append(points1[b]['T'])
    labels1.append(b)
s8_1 = s1[-1]
T8_1 = points1['8']['T']
cp_closure1 = (0.0 - s8_1) / np.log(points1['1']['T'] / T8_1)
s1.append(0.0)
T1.append(points1['1']['T'])
labels1.append('1')

points2 = {
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
    ('1','2', 1012,287.0), ('2','2c',1012,288.5), ('2c','3',1012,288.5),
    ('3','4', 1012,288.5), ('4','5',1491,293.0), ('5','6',1661,293.0),
    ('6','6p',1661,293.0), ('6p','7',1005,287.0), ('7','8',1165,293.0)
]

s2 = [0.0]
T2 = [points2['1']['T']]
labels2 = ['1']
for a, b, cp, R in segments:
    ds = delta_s(points2[a]['T'], points2[b]['T'], points2[a]['P'], points2[b]['P'], cp, R)
    s2.append(s2[-1] + ds)
    T2.append(points2[b]['T'])
    labels2.append(b)
s8_2 = s2[-1]
T8_2 = points2['8']['T']
cp_closure2 = (0.0 - s8_2) / np.log(points2['1']['T'] / T8_2)
s2.append(0.0)
T2.append(points2['1']['T'])
labels2.append('1')

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

def build_contour_noMIPCC(s_nodes, T_nodes, labels, cp_closure):
    contour_s = []
    contour_T = []
    num = 150
    for k in range(len(s_nodes)-1):
        s1k, s2k = s_nodes[k], s_nodes[k+1]
        T1k, T2k = T_nodes[k], T_nodes[k+1]
        p1, p2 = labels[k], labels[k+1]
        if p1 == '6' and p2 == '6p':
            s_curv, T_curv = isobar_curve(s1k, T1k, s2k, cp_gas, num)
        elif p1 == '8' and p2 == '1':
            s_curv, T_curv = isobar_curve(s1k, T1k, s2k, cp_closure, num)
        else:
            s_curv, T_curv = polytrope_curve(s1k, T1k, s2k, T2k, num)
        if k == 0:
            contour_s.extend(s_curv)
            contour_T.extend(T_curv)
        else:
            contour_s.extend(s_curv[1:])
            contour_T.extend(T_curv[1:])
    contour_s.append(contour_s[0])
    contour_T.append(contour_T[0])
    return np.array(contour_s), np.array(contour_T)

def build_contour_MIPCC(s_nodes, T_nodes, labels, cp_closure):
    contour_s = []
    contour_T = []
    num = 150
    for k in range(len(s_nodes)-1):
        s1k, s2k = s_nodes[k], s_nodes[k+1]
        T1k, T2k = T_nodes[k], T_nodes[k+1]
        p1, p2 = labels[k], labels[k+1]
        if p1 == '4' and p2 == '5':
            s_curv, T_curv = polytrope_curve(s1k, T1k, s2k, T2k, num)
        elif p1 == '8' and p2 == '1':
            s_curv, T_curv = isobar_curve(s1k, T1k, s2k, cp_closure, num)
        else:
            s_curv = np.linspace(s1k, s2k, num)
            T_curv = np.linspace(T1k, T2k, num)
        if k == 0:
            contour_s.extend(s_curv)
            contour_T.extend(T_curv)
        else:
            contour_s.extend(s_curv[1:])
            contour_T.extend(T_curv[1:])
    contour_s.append(contour_s[0])
    contour_T.append(contour_T[0])
    return np.array(contour_s), np.array(contour_T)

def cycle_area(s_arr, T_arr):
    area = 0.0
    for i in range(len(s_arr)-1):
        area += 0.5 * (T_arr[i] + T_arr[i+1]) * (s_arr[i+1] - s_arr[i])
    return area

s_cont1, T_cont1 = build_contour_noMIPCC(s1, T1, labels1, cp_closure1)
area1 = cycle_area(s_cont1, T_cont1)

s_cont2, T_cont2 = build_contour_MIPCC(s2, T2, labels2, cp_closure2)
area2 = cycle_area(s_cont2, T_cont2)

print(f"Cycle area WITHOUT MIPCC: {area1:.2f} J/(kg·K)")
print(f"Cycle area WITH MIPCC:    {area2:.2f} J/(kg·K)")
print(f"Work increase: {(area2-area1)/area1*100:.1f}%")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

ax1.plot(s_cont1, T_cont1, 'b-', linewidth=2, label='Without MIPCC')
ax1.plot(s_cont2, T_cont2, 'r-', linewidth=2, label='With MIPCC')
ax1.plot(s1, T1, 'bo', markersize=5)
ax1.plot(s2, T2, 'ro', markersize=5)
ax1.set_xlabel('Specific entropy s, J/(kg·K)')
ax1.set_ylabel('Temperature T, K')
ax1.set_title('T-s cycles comparison (H=9 km, M=0.88)')
ax1.grid(True, linestyle='--', alpha=0.5)
ax1.legend()

bars = ax2.bar(['Without MIPCC', 'With MIPCC'], [area1, area2], color=['blue', 'red'])
ax2.set_ylabel('Specific work, J/(kg·K)')
ax2.set_title('Cycle area comparison')
for bar, val in zip(bars, [area1, area2]):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
             f'{val:.0f}', ha='center', va='bottom', fontweight='bold')
plt.tight_layout()
plt.show()