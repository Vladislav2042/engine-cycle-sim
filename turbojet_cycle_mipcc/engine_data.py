import numpy as np

CONSTANTS = {
    'air': {'cp': 1012, 'R': 287.0},
    'mix': {'cp': 1012, 'R': 288.5},
    'gas_hpt': {'cp': 1491, 'R': 293.0},
    'gas_lpt': {'cp': 1661, 'R': 293.0},
    'cooling': {'cp': 1165, 'R': 293.0}
}

SEGMENTS = [
    ('1', '2', 'air'),
    ('2', '2c', 'mix'),
    ('2c', '3', 'mix'),
    ('3', '4', 'mix'),
    ('4', '5', 'gas_hpt'),
    ('5', '6', 'gas_lpt'),
    ('6', '6p', 'gas_lpt'),
    ('6p', '7', 'air'),
    ('7', '8', 'cooling')
]

def atmosphere(H_km):
    H = H_km * 1000
    if H < 11000:
        T = 288.15 - 0.0065 * H
        P = 101325 * (288.15 / T) ** (-5.25588)
    else:
        T = 216.65
        P = 22632 * np.exp(-(H - 11000) / 6341.8)
    return T, P

def calculate_cycle(H, M):
    T_atm, P_atm = atmosphere(H)
    k = 1.4
    T2_star = T_atm * (1 + (k - 1)/2 * M**2)
    P2_star = P_atm * (1 + (k - 1)/2 * M**2) ** (k/(k-1))
    sigma_diff = 0.97 if M <= 1 else 0.97 - 0.1*(M-1)**1.5
    P2_star *= sigma_diff

    base_T = {
        '1': T_atm,
        '2': T2_star,
        '2c': T2_star * (248.59/265.62),
        '3': T2_star * (383.035/265.62),
        '4': T2_star * (712.823/265.62),
        '5': T2_star * (1712.492/265.62),
        '6': T2_star * (1498.23/265.62),
        '6p': T2_star * (1580.5/265.62),
        '7': T2_star * (1495.787/265.62),
        '8': T2_star * (990.18/265.62)
    }
    base_P = {
        '1': P_atm,
        '2': P2_star,
        '2c': P2_star,
        '3': P2_star * (186381.0/49438.0),
        '4': P2_star * (1258072.0/49438.0),
        '5': P2_star * (1183846.0/49438.0),
        '6': P2_star * (642820.0/49438.0),
        '6p': P2_star * (642820.0/49438.0),
        '7': P2_star * (503224.0/49438.0),
        '8': P_atm
    }
    points = {key: {'T': base_T[key], 'P': base_P[key]} for key in base_T}

    s_vals = [0.0]
    T_vals = [points['1']['T']]
    labels = ['1']
    current_s = 0.0
    for p1, p2, const_key in SEGMENTS:
        cp = CONSTANTS[const_key]['cp']
        R = CONSTANTS[const_key]['R']
        T1, P1 = points[p1]['T'], points[p1]['P']
        T2, P2 = points[p2]['T'], points[p2]['P']
        ds = cp * np.log(T2 / T1) - R * np.log(P2 / P1)
        current_s += ds
        s_vals.append(current_s)
        T_vals.append(points[p2]['T'])
        labels.append(p2)

    s8 = s_vals[-1]
    T8 = points['8']['T']
    cp_closure = (0.0 - s8) / np.log(T_atm / T8) if abs(np.log(T_atm / T8)) > 1e-6 else 1e6
    s_vals.append(0.0)
    T_vals.append(T_atm)
    labels.append('1')
    return s_vals, T_vals, labels, cp_closure