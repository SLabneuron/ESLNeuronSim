# -*- coding: utf-8 -*-
"""
Created on: 2023-7-23
Updated on: 2024-11-15

@author: shirafujilab

Efficiency:

    毎ステップ計算 vs LUT (numpy) vs LUT (namba)
    ⇒毎ステップするよりも時間半分くらいLUTの方が早い．また，いろんなシナジー的にnambaでやった方が楽（np.meshgrid がnopythonで not supported）．

    Better : LUT (numba)

"""


import numpy as np
import math

import numba
numba.set_num_threads(15) 
from numba import njit, prange



@njit(parallel=True)
def _make_lut_numba(N, M, s1, s2, gamma_X, gamma_Y, Tc, Tx, Ty,
                    tau1, b1, S, WE11, WE12, WI11, WI12,
                    tau2, b2, WE21, WE22, WI21, WI22):

    Fin = np.zeros((N,N), dtype=np.int16)
    Gin = np.zeros((N,N), dtype=np.int16)

    for idx in prange(N*N):

        x = idx//N
        y = idx%N

        F = (1/tau1)*((b1*S+WE11*(x/s1)**2+WE12*(y/s2)**2)*(1-x/s1)
                        -(1+WI11*(x/s1)**2+WI12*(y/s2)**2)*x/s1)

        if F >= 0   and F <  0.0001: Fin[x, y] = M-1
        elif F < 0  and F > -0.0001: Fin[x, y] = -(M-1)
        elif F >= 0 and F >= 0.0001: Fin[x, y] = math.ceil(1/(F/(Tc/Tx)))
        else: Fin[x, y] = math.floor(1/(F/(Tc/Tx)))

        G = (1/tau2)*((b2*S+WE21*(x/s1)**2+WE22*(y/s2)**2)*(1-y/s2)
                        -(1+WI21*(x/s1)**2+WI22*(y/s2)**2)*y/s2)

        if G >= 0   and G <  0.0001: Gin[x, y] = M-1
        elif G < 0  and G > -0.0001: Gin[x, y] = -(M-1)
        elif G >= 0 and G >= 0.0001: Gin[x, y] = math.ceil(1/(G/(Tc/Ty)))
        else: Gin[x, y] = math.floor(1/(G/(Tc/Ty)))

    return Fin, Gin



@njit(parallel=True)
def _make_rotated_lut_numba(N, M, s1, s2, gamma_X, gamma_Y, Tc, Tx, Ty,
              tau1, b1, S, WE11, WE12, WI11, WI12,
              tau2, b2, WE21, WE22, WI21, WI22,
              rotated_x, rotated_y, deg):

    Fin = np.zeros((N,N), dtype=np.int16)
    Gin = np.zeros((N,N), dtype=np.int16)

    theta = deg * math.pi / 180 # pi/180 (radian) = 1 [degree]

    for idx in prange(N*N):

        ix = idx//N
        iy = idx%N

        x = rotated_x[ix, iy]
        y = rotated_y[ix, iy]

        # calculate vector field function of new ladder
        f = (1/tau1)*((b1*S+WE11*(x/s1)**2+WE12*(y/s2)**2)*(1-x/s1)
                        -(1+WI11*(x/s1)**2+WI12*(y/s2)**2)*x/s1)

        g = (1/tau2)*((b2*S+WE21*(x/s1)**2+WE22*(y/s2)**2)*(1-y/s2)
                        -(1+WI21*(x/s1)**2+WI22*(y/s2)**2)*y/s2)

        # adjust vector field toward basis vector
        F = f * math.cos(theta) - g * math.sin(theta)
        G = f * math.sin(theta) + g * math.cos(theta)

        if F >= 0   and F <  0.0001: Fin[ix, iy] = M-1
        elif F < 0  and F > -0.0001: Fin[ix, iy] = -(M-1)
        elif F >= 0 and F >= 0.0001: Fin[ix, iy] = math.ceil(1/(F/(Tc/Tx)))
        else: Fin[ix, iy] = math.floor(1/(F/(Tc/Tx)))

        if G >= 0   and G <  0.0001: Gin[ix, iy] = M-1
        elif G < 0  and G > -0.0001: Gin[ix, iy] = -(M-1)
        elif G >= 0 and G >= 0.0001: Gin[ix, iy] = math.ceil(1/(G/(Tc/Ty)))
        else: Gin[ix, iy] = math.floor(1/(G/(Tc/Ty)))

    return Fin, Gin


@njit
def calc_time_evolution_eca(init_X, init_Y, init_P, init_Q, init_phX, init_phY,
                        N, M, Tc, Tx, Ty,
                        total_step, index_start, store_step, Fin, Gin):

    # variables
    x_next = x_previous = init_X
    y_next = y_previous = init_Y
    p_next = p_previous = init_P
    q_next = q_previous = init_Q
    phx_next = phx_previous = init_phX
    phy_next = phy_previous = init_phY
    Cx = 0
    Cy = 0
    T = 0

    # store return arrays
    t_hist = np.zeros(store_step)
    x_hist = np.zeros(store_step, dtype=np.int16)
    y_hist = np.zeros(store_step, dtype=np.int16)

    idx = 0


    for i in range(total_step):

        # time evolution
        T, phx_next, phy_next, Cx, Cy = time_evolution(Tc, Tx, Ty, T, phx_previous, phy_previous)

        # calculate
        Fx = Fin[x_previous, y_previous]
        Fy = Gin[x_previous, y_previous]

        absFx = abs(Fx)
        absFy = abs(Fy)

        # cal auxiliary variables
        if Cx == 1:
            if (p_previous < absFx) and (p_previous < M - 1):
                p_next = p_previous + 1
            else:
                p_next = 0

                # state transition of x
                if (Fx >=0) and (x_previous < N-1):
                    x_next = x_previous + 1
                elif (Fx < 0) and (x_previous > 0):
                    x_next = x_previous -1
                else:
                    x_next = x_previous
        else:
            x_next = x_previous
            p_next = p_previous


        # cal auxiliary variables
        if Cy == 1:
            if (q_previous < absFy) and (q_previous < M - 1):
                q_next = q_previous + 1
            else:
                q_next = 0

                # state transition of y
                if (Fy >=0) and (y_previous < N-1):
                    y_next = y_previous + 1
                elif (Fy < 0) and (y_previous > 0):
                    y_next = y_previous -1
                else:
                    y_next = y_previous
        else:
            y_next = y_previous
            q_next = q_previous


        # update variables
        x_previous = x_next
        y_previous = y_next
        p_previous = p_next
        q_previous = q_next
        phx_previous = phx_next
        phy_previous = phy_next

        # store registers
        if i >= index_start:

            if (idx % 100) == 0:

                idx_insert = int(idx/100)

                t_hist[idx_insert] = T

                # x_hist, y_hist shape: (time, state variables)
                x_hist[idx_insert] = x_previous
                y_hist[idx_insert] = y_previous

            idx += 1


    return t_hist, x_hist, y_hist




@njit
def time_evolution(Tc, Tx, Ty, T, phx_previous, phy_previous):

    T = T + Tc

    Cx = 1 if phx_previous >= (1-Tc/Tx) else 0
    Cy = 1 if phy_previous >= (1-Tc/Ty) else 0

    phx_next = phx_previous + Tc/Tx
    phy_next = phy_previous + Tc/Ty

    phx_next = phx_next - math.floor(phx_next)
    phy_next = phy_next - math.floor(phy_next)


    return T, phx_next, phy_next, Cx, Cy