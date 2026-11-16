import pickle
import numpy as np
import matplotlib.pyplot as plt
from engine_data import CONSTANTS

def smooth_isobar(s_start, T_start, s_end, cp, num=200):
    s_vals = np.linspace(s_start, s_end, num)
    T_vals = T_start * np.exp((s_vals - s_start) / cp)
    return s_vals, T_vals

def smooth_polytrope(s_start, T_start, s_end, T_end, num=200):
    s_vals = np.linspace(s_start, s_end, num)
    logT_start = np.log(T_start)
    logT_end = np.log(T_end)
    logT_vals = np.interp(s_vals, [s_start, s_end], [logT_start, logT_end])
    T_vals = np.exp(logT_vals)
    return s_vals, T_vals

def cycle_area(s_arr, T_arr):
    if len(s_arr) != len(T_arr):
        raise ValueError("Arrays must have the same length")
    area = 0.0
    for i in range(len(s_arr) - 1):
        area += 0.5 * (T_arr[i] + T_arr[i+1]) * (s_arr[i+1] - s_arr[i])
    return area

def build_contour(s_nodes, T_nodes, labels, cp_closure):
    contour_s = []
    contour_T = []
    num_points = 150

    for k in range(len(s_nodes) - 1):
        s1, s2 = s_nodes[k], s_nodes[k+1]
        T1, T2 = T_nodes[k], T_nodes[k+1]
        p1, p2 = labels[k], labels[k+1]


        if p1 == '6' and p2 == '6p':

            cp = CONSTANTS['gas_lpt']['cp']
            s_curve, T_curve = smooth_isobar(s1, T1, s2, cp, num_points)
        elif p1 == '8' and p2 == '1':

            s_curve, T_curve = smooth_isobar(s1, T1, s2, cp_closure, num_points)
        else:

            s_curve, T_curve = smooth_polytrope(s1, T1, s2, T2, num_points)

        if k == 0:
            contour_s.extend(s_curve)
            contour_T.extend(T_curve)
        else:
            contour_s.extend(s_curve[1:])
            contour_T.extend(T_curve[1:])

    # Замыкаем контур
    contour_s.append(contour_s[0])
    contour_T.append(contour_T[0])
    return np.array(contour_s), np.array(contour_T)

def main():
    try:
        with open('cycle_cache.pkl', 'rb') as f:
            cache = pickle.load(f)
        print("Cache loaded.")
    except FileNotFoundError:
        print("Cache file 'cycle_cache.pkl' not found. Run precompute_cache.py first.")
        return

    results = {}
    for (H, M), data in cache.items():
        if data is None:
            continue
        s_nodes, T_nodes, labels, cp_closure = data
        try:
            s_contour, T_contour = build_contour(s_nodes, T_nodes, labels, cp_closure)
            area = cycle_area(s_contour, T_contour)
            results[(H, M)] = area
        except Exception as e:
            print(f"Error computing area for H={H}, M={M}: {e}")
            results[(H, M)] = np.nan

    best_pair = max(results, key=results.get)
    best_area = results[best_pair]
    print(f"Maximum cycle work (area) = {best_area:.2f} J/(kg·K) at H = {best_pair[0]} km, M = {best_pair[1]:.2f}")

    heights = sorted(set(h for (h, m) in results.keys()))
    plt.figure(figsize=(10, 6))
    for H in heights:
        machs = []
        areas = []
        for (h, m), area in results.items():
            if h == H and not np.isnan(area):
                machs.append(m)
                areas.append(area)
        if machs:
            idx = np.argsort(machs)
            machs = np.array(machs)[idx]
            areas = np.array(areas)[idx]
            plt.plot(machs, areas, 'o-', label=f'H = {H} km')
    plt.xlabel('Mach number M')
    plt.ylabel('Cycle work (area), J/(kg·K)')
    plt.title('Work vs Mach number for different altitudes (AL-31 with MIPCC)')
    plt.grid(True, alpha=0.4)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()