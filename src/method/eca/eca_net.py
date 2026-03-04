# -*- coding: utf-8 -*-
"""
Created on: 2026-03-03


@author: shirafujilab


"""


import numpy as np
import math
import matplotlib.pyplot as plt
import numba
numba.set_num_threads(15)
from numba import njit, prange

import os
import datetime, time

class TimeEvolEcaNetwork:

    def __init__(self, params, filename):

        # get params, filename
        self.params = params
        self.filename = filename

        # Ensure output directory exists
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)

        # Confirm: output filename
        print(filename)

    def run(self):

        params = self.params

        """ For ESL """

        # variables
        init_X = np.array([0, 6, 12, 18, 24, 36, 42, 48, 24], dtype=np.int16)
        init_Y, init_Z = np.zeros_like(init_X), np.zeros_like(init_X)
        init_P, init_Q, init_R = np.zeros_like(init_X), np.zeros_like(init_X), np.zeros_like(init_X)
        init_phX, init_phY, init_phZ = np.zeros(init_X.shape, np.float32), np.zeros(init_X.shape, np.float32), np.zeros(init_X.shape, np.float32)

        # esl parameters
        N1, N2, N3, M, s1, s2, s3 = params["N1"], params["N2"], params["N3"], params["M"], params["s1"], params["s2"], params["s3"]
        Tc, Tx, Wx, Ty, Wy, Tz, Wz = params["Tc"], params["Tx"], params["Wx"], params["Ty"], params["Wy"], params["Tz"], params["Wz"]
        M_I = 2**6

        """ sim config """

        # time
        sT, eT, h = params["sT"], params["eT"], np.float32(params["h"])

        # store step
        total_step = int(eT/h)+1
        index_start = int(sT/h)
        store_step = (total_step - index_start) // 100 + 1 if total_step > index_start else 0

        """ for models """

        # parameters
        a, b, c, d, r, s = np.float32(params['a']), np.float32(params['b']), np.float32(params['c']), np.float32(params['d']), np.float32(params['r']), np.float32(params['s'])
        I_ext = np.float32(params["I_ext"])

        # x_1
        p = (d - b) / a
        q = c / a

        coef = [1, p, 0, -q]   # x^3 + p x^2 - q = 0
        x_1 = np.roots(coef)[0]

        # coupling parameters V_s, Theta, g_s, gamma, c_ij
        Theta = np.float32(params["Theta"])     # 0, 1 determined by this value　⇒ np.int16(Theta * s1)

        Th = np.int16(40) #np.int16((Theta)*(N1/s1)) -2       # exceeding over 24, connecting synapse (this function denote 1)
        V_s = np.float32(params["V_s"])         # default value (2)
        g_s = np.float32(params["g_s"])         # 0.429
        gamma = np.float32(params["gamma"])

        c_ij = np.array([[0, 1, 1, 1, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 1, 1, 1, 0, 0],
                         [1, 0, 0, 0, 0, 0, 0, 1, 1],
                         [0, 1, 0, 0, 1, 0, 0, 1, 0],
                         [0, 0, 1, 0, 0, 1, 0, 0, 1],
                         [1, 0, 0, 1, 0, 0, 1, 0, 0],
                         [0, 0, 1, 0, 0, 1, 0, 0, 1],
                         [0, 1, 0, 0, 1, 0, 1, 0, 0],
                         [1, 0, 0, 1, 0, 0, 0, 1, 0]], dtype=np.float32)

        n = c_ij.shape[0]
        k = np.sum(c_ij[0])

        """ run simulation """
        bench_sT = datetime.datetime.now()
        t0 = time.perf_counter()
        print("\n start: ", bench_sT)

        print(N1, N2, N3, M, s1, s2, s3, Tx, Wx, Ty, Wy, Tz, Wz,
                                        a, b, c, d, r, s, x_1, I_ext)

        # make lut
        Fin, Gin, Hin = _make_lut_numba(N1, N2, N3, M, s1, s2, s3, Tx, Wx, Ty, Wy, Tz, Wz,
                                        a, b, c, d, r, s, x_1, I_ext)


        # set calode
        t_hist, X_hist = calc_time_evolution_eca(init_X, init_Y, init_Z,
                                                 init_P, init_Q, init_R,
                                                 init_phX, init_phY, init_phZ,
                                                 M, N1, N2, N3,
                                                 Fin, Gin, Hin,
                                                 Tc, Tx, Wx, Ty, Wy, Tz, Wz,
                                                 M_I, s1, g_s, V_s, Th, c_ij,         # network parameters
                                                 total_step, index_start, store_step)

        bench_eT = datetime.datetime.now()
        t1 = time.perf_counter()
        print("end: ", bench_eT)
        print("bench mark: ", t1 - t0)

        # Store results
        plot_time_series(t_hist, X_hist)

        return t_hist, X_hist


@njit(parallel=True)
def _make_lut_numba(N1, N2, N3, M, s1, s2, s3, Tx, Wx, Ty, Wy, Tz, Wz,
                    a, b, c, d, r, s, x_1, I_ext):

    Fin = np.zeros((N1,N2,N3), dtype=np.int16)
    Gin = np.zeros((N1,N2), dtype=np.int16)
    Hin = np.zeros((N1,N3), dtype=np.int16)

    delta_X = Wx/Tx
    delta_Y = Wy/Ty
    delta_Z = Wz/Tz

    # inputs to F: (X, Y, Z)
    for idx in prange(N1*N2*N3):

        i = idx // (N2 * N3)
        j = (idx %  (N2 * N3)) // N3
        k = idx % N3

        x = (i/s1) - 2
        y = (j/s2) - 12
        z = (k/s3)

        F = y  -  a*x**3 + b*x**2 - z + I_ext

        if F >= 0   and F <  0.0001: Fin[i, j, k] = M-1
        elif F < 0  and F > -0.0001: Fin[i, j, k] = -(M-1)
        elif F >= 0 and F >= 0.0001: Fin[i, j, k] = math.ceil(1/(F/delta_X))
        else: Fin[i, j, k] = math.floor(1/(F/delta_X))

    # inputs to G: (X, Y)
    for idx in prange(N1*N2):

        i = idx//N2
        j = idx%N2

        x = (i/s1) - 2
        y = (j/s2) - 12

        G = c - d*x**2 - y

        if G >= 0   and G <  0.0001: Gin[i, j] = M-1
        elif G < 0  and G > -0.0001: Gin[i, j] = -(M-1)
        elif G >= 0 and G >= 0.0001: Gin[i, j] = math.ceil(1/(G/delta_Y))
        else: Gin[i, j] = math.floor(1/(G/delta_Y))

    # inputs to H are (X, Z)
    for idx in prange(N1*N3):

        i = idx//N3
        k = idx%N3

        x = (i/s1) - 2
        z = (k/s3)

        H = r*(s*(x - x_1) - z)

        if H >= 0   and H <  0.0001: Hin[i, k] = M-1
        elif H < 0  and H > -0.0001: Hin[i, k] = -(M-1)
        elif H >= 0 and H >= 0.0001: Hin[i, k] =  math.ceil(1/(H/delta_Z))
        else: Hin[i, k] =  math.floor(1/(H/delta_Z))

    return Fin, Gin, Hin


@njit
def _I_lut(n, M_I, x_previous, s1,
           Tx, Wx,
           g_s, V_s, syn):

    #Iin = np.zeros((n), dtype=np.int16)

    delta_X = Wx/Tx

    # inputs to F: (X, Y, Z)
    #for idx in prange(n):

    x = (x_previous/s1) - 2

    I = - g_s * (x - V_s) * syn

    if I > 0   and I <  0.0001: Iin = 4   #M_I - 1
    elif I < 0  and I > -0.0001: Iin = -4 #-(M_I - 1)
    elif I > 0 and I >= 0.0001: Iin =  2  #math.ceil(1/(I/delta_X))
    elif I < 0 and I >= -0.0001: Iin = -2 #math.floor(1/(I/delta_X))
    elif I == 0: Iin = 0

    return Iin


@njit
def calc_time_evolution_eca(init_X, init_Y, init_Z,
                            init_P, init_Q, init_R,
                            init_phX, init_phY, init_phZ,
                            M, N1, N2, N3,
                            Fin, Gin, Hin,
                            Tc, Tx, Wx, Ty, Wy, Tz, Wz,

                            M_I, s1, g_s, V_s, Th, c_ij,

                            total_step, index_start, store_step):

    # variables
    x_next = x_previous = init_X
    y_next = y_previous = init_Y
    z_next = z_previous = init_Z
    p_next = p_previous = init_P
    q_next = q_previous = init_Q
    r_next = r_previous = init_R
    phx_next = phx_previous = init_phX
    phy_next = phy_previous = init_phY
    phz_next = phz_previous = init_phZ

    n = init_X.shape[0]

    Cx = 0
    Cy = 0
    Cz = 0
    T = 0

    # store return arrays
    t_hist = np.zeros(store_step)
    x_hist = np.zeros((n, store_step), dtype=np.int16)

    I_previous = I_next = np.zeros(n, dtype=np.int16)

    idx = 0

    for i in range(total_step):

        # count the numer of synapse over threshold
        Gamma = np.where(x_previous > Th, np.float32(1), np.float32(0))
        syn = c_ij @ Gamma

        for j in range(n):

            # time evolution
            T, phx_next[j], phy_next[j], phz_next[j], Cx, Cy, Cz = time_evolution(Tc, Tx, Wx, Ty, Wy, Tz, Wz, T, phx_previous[j], phy_previous[j], phz_previous[j])

            # calculate
            Fx = Fin[x_previous[j], y_previous[j], z_previous[j]]
            Fy = Gin[x_previous[j], y_previous[j]]
            Fz = Hin[x_previous[j], z_previous[j]]

            absFx = abs(Fx)
            absFy = abs(Fy)
            absFz = abs(Fz)

            # cal auxiliary variables
            if Cx == 1:

                # Synapse Input
                FI = _I_lut(n, M_I, x_previous[j], s1, Tx, Wx, g_s, V_s, syn[j])
                absFI = abs(FI)

                #if (I_previous[j] < absFI) and (I_previous[j] < M_I - 1):
                #    I_next[j] = I_previous[j] + np.int16(1)
                #else:
                #    I_next[j] = 0

                #    if (FI >0):
                #        p_update = np.int16(1)
                #    elif (FI < 0):
                #        p_update = - np.int16(1)

                if (p_previous[j] < absFx) and (p_previous[j] < M - 1):
                    p_next[j] = p_previous[j] + np.int16(1) + FI
                else:
                    p_next[j] = 0 + FI

                    # state transition of x
                    if (Fx >=0) and (x_previous[j] < N1-1):
                        x_next[j] = x_previous[j] + np.int16(1)
                    elif (Fx < 0) and (x_previous[j] > 0):
                        x_next[j] = x_previous[j] - np.int16(1)
                    else:
                        x_next[j] = x_previous[j]


            else:
                x_next[j] = x_previous[j]
                p_next[j] = p_previous[j]
                I_next[j] = I_previous[j]


            # cal auxiliary variables
            if Cy == 1:
                if (q_previous[j] < absFy) and (q_previous[j] < M - 1):
                    q_next[j] = q_previous[j] + np.int16(1)
                else:
                    q_next[j] = 0

                    # state transition of y
                    if (Fy >=0) and (y_previous[j] < N2-1):
                        y_next[j] = y_previous[j] + np.int16(1)
                    elif (Fy < 0) and (y_previous[j] > 0):
                        y_next[j] = y_previous[j] - np.int16(1)
                    else:
                        y_next[j] = y_previous[j]
            else:
                y_next[j] = y_previous[j]
                q_next[j] = q_previous[j]


            # cal auxiliary variables
            if Cz == 1:
                if (r_previous[j] < absFz) and (r_previous[j] < M - 1):
                    r_next[j] = r_previous[j] + np.int16(1)
                else:
                    r_next[j] = 0

                    # state transition of y
                    if (Fz >=0) and (z_previous[j] < N3-1):
                        z_next[j] = z_previous[j] + np.int16(1)
                    elif (Fz < 0) and (z_previous[j] > 0):
                        z_next[j] = z_previous[j] - np.int16(1)
                    else:
                        z_next[j] = z_previous[j]
            else:
                z_next[j] = z_previous[j]
                r_next[j] = r_previous[j]


        # update variables
        x_previous = x_next
        y_previous = y_next
        z_previous = z_next
        p_previous = p_next
        q_previous = q_next
        r_previous = r_next
        phx_previous = phx_next
        phy_previous = phy_next
        phz_previous = phz_next


        """ Update """

        # store registers
        if i >= index_start:

            if (idx % 100) == 0:

                idx_insert = int(idx/100)

                t_hist[idx_insert] = T
                x_hist[:, idx_insert] = x_previous

            idx += 1


    return t_hist, x_hist




@njit
def time_evolution(Tc, Tx, Wx, Ty, Wy, Tz, Wz, T, phx_previous, phy_previous, phz_previous):

    T = T + Tc

    Cx = 1 if phx_previous >= (1-Wx/Tx) else 0
    Cy = 1 if phy_previous >= (1-Wy/Ty) else 0
    Cz = 1 if phz_previous >= (1-Wz/Tz) else 0

    phx_next = phx_previous + Tc/Tx
    phy_next = phy_previous + Tc/Ty
    phz_next = phz_previous + Tc/Tz

    phx_next = phx_next - math.floor(phx_next)
    phy_next = phy_next - math.floor(phy_next)
    phz_next = phz_next - math.floor(phz_next)

    return T, phx_next, phy_next, phz_next, Cx, Cy, Cz




""" test """

def plot_time_series(t_hist, x_hist):

    n  = x_hist.shape[0]

    fig, ax = plt.subplots(figsize=(10, 7))

    for idx in range(n):
        ax.plot(t_hist[:-1], x_hist[idx, :-1], lw=0.8)

    ax.set_ylabel("x")
    ax.set_xlabel("time")

    plt.tight_layout()
    plt.show()
    
    



"""


# cal auxiliary variables
            if Cx == 1:
                if (p_previous[j] < absFx) and (p_previous[j] < M - 1):
                    p_next[j] = p_previous[j] + np.int16(1)
                else:
                    p_next[j] = 0

                    # state transition of x
                    if (Fx >=0) and (x_previous[j] < N1-1):
                        x_update = x_previous[j] + np.int16(1)
                    elif (Fx < 0) and (x_previous[j] > 0):
                        x_update = x_previous[j] - np.int16(1)
                    else:
                        x_update = x_previous[j]

                # Synapse Input
                FI = _I_lut(n, M_I, x_previous[j], s1, Tx, Wx, g_s, V_s, syn[j])
                absFI = abs(FI)

                if (I_previous[j] < absFI) and (I_previous[j] < M_I - 1):
                    I_next[j] = I_previous[j] + np.int16(1)
                else:
                    I_next[j] = 0

                    # state transition of x
                    if (FI >0) and (x_update < N1-1):
                        x_update = x_update + np.int16(1)
                    elif (FI < 0) and (x_update > 0):
                        x_update = x_update - np.int16(1)
                    else:
                        x_update = x_update

                x_next[j] = x_update

            else:
                x_next[j] = x_previous[j]
                p_next[j] = p_previous[j]
                I_next[j] = I_previous[j]
"""