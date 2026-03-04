# -*- coding: utf-8 -*-
"""
Created on: 2026-02-26


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

class TimeEvolEcaSingle:

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
        init_X, init_Y, init_Z = np.int16(params["init_X"]), np.int16(params["init_Y"]), np.int16(params["init_Z"])
        init_P, init_Q, init_R = np.int16(params["init_P"]), np.int16(params["init_Q"]), np.int16(params["init_R"])
        init_phX, init_phY, init_phZ = np.float32(params["init_phX"]), np.float32(params["init_phY"]), np.float32(params["init_phZ"])

        # esl parameters
        N1, N2, N3, M, s1, s2, s3 = params["N1"], params["N2"], params["N3"], params["M"], params["s1"], params["s2"], params["s3"]
        Tc, Tx, Wx, Ty, Wy, Tz, Wz = params["Tc"], params["Tx"], params["Wx"], params["Ty"], params["Wy"], params["Tz"], params["Wz"]

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
        t_hist, I_hist, X_hist, Y_hist, Z_hist = calc_time_evolution_eca(init_X, init_Y, init_Z,
                                                                         init_P, init_Q, init_R,
                                                                         init_phX, init_phY, init_phZ,
                                                                         M, N1, N2, N3,
                                                                         Fin, Gin, Hin, I_ext,
                                                                         Tc, Tx, Wx, Ty, Wy, Tz, Wz,
                                                                         total_step, index_start, store_step)

        bench_eT = datetime.datetime.now()
        t1 = time.perf_counter()
        print("end: ", bench_eT)
        print("bench mark: ", t1 - t0)

        # Store results
        # plot_time_series(t_hist[:-1], I_hist[:-1], X_hist[:-1], Y_hist[:-1], Z_hist[:-1])
        
        return t_hist[:-1], I_hist[:-1], X_hist[:-1], Y_hist[:-1], Z_hist[:-1]


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
def calc_time_evolution_eca(init_X, init_Y, init_Z,
                            init_P, init_Q, init_R,
                            init_phX, init_phY, init_phZ,
                            M, N1, N2, N3,
                            Fin, Gin, Hin, I_ext,
                            Tc, Tx, Wx, Ty, Wy, Tz, Wz,
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

    Cx = 0
    Cy = 0
    Cz = 0
    T = 0

    # store return arrays
    t_hist = np.zeros(store_step)
    I_hist = np.zeros(store_step, dtype=np.int16)
    x_hist = np.zeros(store_step, dtype=np.int16)
    y_hist = np.zeros(store_step, dtype=np.int16)
    z_hist = np.zeros(store_step, dtype=np.int16)

    idx = 0

    for i in range(total_step):

        # time evolution
        T, phx_next, phy_next, phz_next, Cx, Cy, Cz = time_evolution(Tc, Tx, Wx, Ty, Wy, Tz, Wz, T, phx_previous, phy_previous, phz_previous)

        # calculate
        Fx = Fin[x_previous, y_previous, z_previous]
        Fy = Gin[x_previous, y_previous]
        Fz = Hin[x_previous, z_previous]

        absFx = abs(Fx)
        absFy = abs(Fy)
        absFz = abs(Fz)

        # cal auxiliary variables
        if Cx == 1:
            if (p_previous < absFx) and (p_previous < M - 1):
                p_next = p_previous + np.int16(1)
            else:
                p_next = 0

                # state transition of x
                if (Fx >=0) and (x_previous < N1-1):
                    x_next = x_previous + np.int16(1)
                elif (Fx < 0) and (x_previous > 0):
                    x_next = x_previous - np.int16(1)
                else:
                    x_next = x_previous
        else:
            x_next = x_previous
            p_next = p_previous


        # cal auxiliary variables
        if Cy == 1:
            if (q_previous < absFy) and (q_previous < M - 1):
                q_next = q_previous + np.int16(1)
            else:
                q_next = 0

                # state transition of y
                if (Fy >=0) and (y_previous < N2-1):
                    y_next = y_previous + np.int16(1)
                elif (Fy < 0) and (y_previous > 0):
                    y_next = y_previous - np.int16(1)
                else:
                    y_next = y_previous
        else:
            y_next = y_previous
            q_next = q_previous


        # cal auxiliary variables
        if Cz == 1:
            if (r_previous < absFz) and (r_previous < M - 1):
                r_next = r_previous + np.int16(1)
            else:
                r_next = 0

                # state transition of y
                if (Fz >=0) and (z_previous < N3-1):
                    z_next = z_previous + np.int16(1)
                elif (Fz < 0) and (z_previous > 0):
                    z_next = z_previous - np.int16(1)
                else:
                    z_next = z_previous
        else:
            z_next = z_previous
            r_next = r_previous


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

        # store registers
        if i >= index_start:

            if (idx % 100) == 0:

                idx_insert = int(idx/100)

                t_hist[idx_insert] = T

                # x_hist, y_hist shape: (time, state variables)
                I_hist[idx_insert] = I_ext
                x_hist[idx_insert] = x_previous
                y_hist[idx_insert] = y_previous
                z_hist[idx_insert] = z_previous

            idx += 1


    return t_hist, I_hist, x_hist, y_hist, z_hist




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

def plot_time_series(t_hist, I_hist, x_hist, y_hist, z_hist):
    
    # scaling to ode
    x = (x_hist/16) - 2
    y = (y_hist/4) - 12
    z = (z_hist/32)

    fig, ax = plt.subplots(4, 1, figsize=(10, 7), sharex=True)

    """
    ax[0].plot(t_hist, I_hist, lw=0.8)
    ax[0].set_ylabel("Input")

    ax[1].plot(t_hist, x_hist, lw=0.8)
    ax[1].set_ylabel("x")

    ax[2].plot(t_hist, y_hist, lw=0.8)
    ax[2].set_ylabel("y")

    ax[3].plot(t_hist, z_hist, lw=0.8)
    ax[3].set_ylabel("z")
    ax[3].set_xlabel("time")
    """
    
    ax[0].plot(t_hist, I_hist, lw=0.8)
    ax[0].set_ylabel("Input")

    ax[1].plot(t_hist, x, lw=0.8)
    ax[1].set_ylabel("x")

    ax[2].plot(t_hist, y, lw=0.8)
    ax[2].set_ylabel("y")

    ax[3].plot(t_hist, z, lw=0.8)
    ax[3].set_ylabel("z")
    ax[3].set_xlabel("time")

    plt.tight_layout()
    plt.show()