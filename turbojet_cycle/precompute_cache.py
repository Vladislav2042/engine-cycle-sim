import pickle
import numpy as np
from engine_data import calculate_cycle

heights = [4,5,6,7,8,9,10,11,12,13,14]
mach_list = np.arange(0.5, 3.05, 0.1).round(2)

cache = {}
for H in heights:
    for M in mach_list:
        print(f"Calculating H={H} km, M={M:.2f}")
        try:
            s, T, labels, cp_close = calculate_cycle(H, M)
            cache[(H, M)] = (s, T, labels, cp_close)
        except Exception as e:
            print(f"Error: {e}")
            cache[(H, M)] = None

with open('cycle_cache.pkl', 'wb') as f:
    pickle.dump(cache, f)
print("Cache saved to cycle_cache.pkl")