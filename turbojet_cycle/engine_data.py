import numpy as np

# Атмосфера
atm_data = {
    4: {'P': 61650, 'T': 262, 'a': 324},
    5: {'P': 54040, 'T': 256, 'a': 320},
    6: {'P': 47210, 'T': 249, 'a': 316},
    7: {'P': 41010, 'T': 243, 'a': 312},
    8: {'P': 35650, 'T': 236, 'a': 308},
    9: {'P': 30790, 'T': 230, 'a': 304},
    10: {'P': 26500, 'T': 223, 'a': 299},
    11: {'P': 22700, 'T': 216, 'a': 295},
    12: {'P': 19400, 'T': 216, 'a': 295},
    13: {'P': 16570, 'T': 216, 'a': 295},
    14: {'P': 14160, 'T': 216, 'a': 295}
}

# Компрессоры
pi_LPC = 3.54
pi_HPC = 6.46
eta_LPC = 0.85
eta_HPC = 0.84

# Камера сгорания
Tg_star = 1665.0
sigma_cc = 0.941
eta_cc = 0.98
Hu = 42900000.0
L0 = 14.8

# Турбины
pi_HPT = 2.9
pi_LPT = 2.3
eta_HPT = 0.89
eta_LPT = 0.91
g_cool = 0.04

# Свойства
cp_air = 1005.0
R_air = 287.0
k_air = 1.4
cp_gas = 1165.0
R_gas = 293.0
k_gas = 1.33

phi_c = 0.98


def diffuser(T_atm, P_atm, M, k, R, cp, sigma_sub=0.97, sigma_super_coeff=0.1):
    T2_star = T_atm * (1 + (k - 1) / 2 * M ** 2)
    if M <= 1:
        sigma_v = sigma_sub
    else:
        sigma_v = sigma_sub - sigma_super_coeff * (M - 1) ** 1.5
    P2_star = P_atm * (1 + (k - 1) / 2 * M ** 2) ** (k / (k - 1)) * sigma_v
    return T2_star, P2_star


def compressor(T_in, P_in, pi, eta, cp, R, k):
    L = cp * T_in * (pi ** ((k - 1) / k) - 1) / eta
    T_out = T_in + L / cp
    P_out = P_in * pi
    return T_out, P_out, L


def combustor(T4, P4, T5, sigma, eta_cc, Hu, cp_air, cp_gas, L0, T0=288.15):
    P5 = P4 * sigma
    numerator = cp_gas * T5 - cp_air * T4
    denominator = Hu * eta_cc - cp_gas * T5 + cp_air * T0
    q_t = numerator / denominator
    alpha = 1.0 / (q_t * L0)
    g_g = 1 + q_t
    return P5, q_t, alpha, g_g


def turbine(T_in, P_in, pi, eta, cp, R, k):
    L = cp * T_in * (1 - (1 / pi) ** ((k - 1) / k)) * eta
    T_out = T_in - L / cp
    P_out = P_in / pi
    return T_out, P_out, L


def mixing(T_hpt_out, T_hpc_out, g_gas, g_cool, cp_gas, cp_air):
    T_mix = (cp_gas * g_gas * T_hpt_out + cp_air * g_cool * T_hpc_out) / (cp_gas * (g_gas + g_cool))
    g_total = g_gas + g_cool
    return T_mix, g_total


def nozzle(T_in, P_in, P_atm, k, R, phi):
    pi_er = P_in / P_atm
    if pi_er > 1:
        C = phi * np.sqrt(2 * (k / (k - 1)) * R * T_in * (1 - (1 / pi_er) ** ((k - 1) / k)))
        T_stat = T_in * (1 / pi_er) ** ((k - 1) / k)
    else:
        C = 0.0
        T_stat = T_in
    return C, T_stat, pi_er


def entropy_change(T1, T2, P1, P2, cp, R):
    return cp * np.log(T2 / T1) - R * np.log(P2 / P1)


def calculate_cycle(H, M):
    P_atm = atm_data[H]['P']
    T_atm = atm_data[H]['T']

    T2_star, P2_star = diffuser(T_atm, P_atm, M, k_air, R_air, cp_air)
    T3_star, P3_star, _ = compressor(T2_star, P2_star, pi_LPC, eta_LPC, cp_air, R_air, k_air)
    T4_star, P4_star, _ = compressor(T3_star, P3_star, pi_HPC, eta_HPC, cp_air, R_air, k_air)
    P5_star, _, _, g_gas = combustor(T4_star, P4_star, Tg_star, sigma_cc, eta_cc, Hu, cp_air, cp_gas, L0)
    T5_star = Tg_star
    T6_star, P6_star, _ = turbine(T5_star, P5_star, pi_HPT, eta_HPT, cp_gas, R_gas, k_gas)
    T6p_star, _ = mixing(T6_star, T4_star, g_gas, g_cool, cp_gas, cp_air)
    P6p_star = P6_star
    T7_star, P7_star, _ = turbine(T6p_star, P6p_star, pi_LPT, eta_LPT, cp_gas, R_gas, k_gas)

    # Расчёт статической температуры на срезе сопла
    _, T8_stat, _ = nozzle(T7_star, P7_star, P_atm, k_gas, R_gas, phi_c)

    points = {
        '1': (T_atm, P_atm),
        '2': (T2_star, P2_star),
        '3': (T3_star, P3_star),
        '4': (T4_star, P4_star),
        '5': (T5_star, P5_star),
        '6': (T6_star, P6_star),
        '6p': (T6p_star, P6p_star),
        '7': (T7_star, P7_star),
        '8': (T8_stat, P_atm)
    }

    order = ['1', '2', '3', '4', '5', '6', '6p', '7', '8']
    cp_dict = dict.fromkeys(order[:4], cp_air)
    cp_dict.update(dict.fromkeys(order[4:], cp_gas))
    R_dict = dict.fromkeys(order[:4], R_air)
    R_dict.update(dict.fromkeys(order[4:], R_gas))

    s_vals = [0.0]
    T_vals = [T_atm]
    for i in range(1, len(order)):
        p_prev = order[i - 1]
        p_curr = order[i]
        T1, P1 = points[p_prev]
        T2, P2 = points[p_curr]
        ds = entropy_change(T1, T2, P1, P2, cp_dict[p_curr], R_dict[p_curr])
        s_vals.append(s_vals[-1] + ds)
        T_vals.append(T2)

    s8 = s_vals[-1]
    T8 = T_vals[-1]
    if abs(np.log(T_atm / T8)) > 1e-6:
        cp_closure = (0 - s8) / np.log(T_atm / T8)
    else:
        cp_closure = 1e6
    s_vals.append(0)
    T_vals.append(T_atm)
    full_labels = order + ['1']
    return s_vals, T_vals, full_labels, cp_closure