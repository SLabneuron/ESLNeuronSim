# -*- coding: utf-8 -*-
"""
Created on: 2023-7-23
Updated on: 2024-11-15

@author: shirafujilab
"""


import numpy as np
import math

from numba import njit, prange


@njit(parallel=True)
def _make_lut_numba(N, M, s1, s2, gamma_X, gamma_Y, Tc, Tx, Ty,
              tau1, b1, S, WE11, WE12, WI11, WI12,
              tau2, b2, WE21, WE22, WI21, WI22):

    Fin = np.zeros((N,N))
    Gin = np.zeros((N,N))


    for idx in prange(N*N):

        x = idx//N
        y = idx%N

        F = (1/tau1)*((b1*S+WE11*(x/s1)**2+WE12*(y/s2)**2)*(1-x/s1)
                        -(1+WI11*(x/s1)**2+WI12*(y/s2)**2)*x/s1)

        if F >= 0 and F < 0.001:
            Fin[x, y] = M-1
        elif F >= 0 and F >=0.001:
            Fin[x, y] = math.ceil(1/(gamma_X*F/(Tc/Tx)))
        elif F < 0 and F < -0.001:
            Fin[x, y] = -(M-1)
        else:
            Fin[x, y] = math.floor(1/(gamma_X*F/(Tc/Tx)))

        G = (1/tau2)*((b2*S+WE21*(x/s1)**2+WE22*(y/s2)**2)*(1-y/s2)
                        -(1+WI21*(x/s1)**2+WI22*(y/s2)**2)*y/s2)

        if G >= 0 and G < 0.001:
            Gin[x, y] = M-1
        elif G >= 0 and G >=0.001:
            Gin[x, y] = math.ceil(1/(gamma_Y*G/(Tc/Ty)))
        elif G < 0 and G < -0.001:
            Gin[x, y] = -(M-1)
        else:
            Gin[x, y] = math.floor(1/(gamma_Y*G/(Tc/Ty)))

    return Fin, Gin



def _make_lut_numpy(N, M, s1, s2, gamma_X, gamma_Y, Tc, Tx, Ty,
              tau1, b1, S, WE11, WE12, WI11, WI12,
              tau2, b2, WE21, WE22, WI21, WI22):

    _x = np.arange(N); _y = np.arange(N)
    x, y = np.meshgrid(_x, _y, indexing="ij")

    F = np.zeros((N,N), dtype=np.int32)
    G = np.zeros((N,N), dtype=np.int32)

    F = (1/tau1)*((b1*S+WE11*(x/s1)**2+WE12*(y/s2)**2)*(1-x/s1)
                        -(1+WI11*(x/s1)**2+WI12*(y/s2)**2)*x/s1)

    Fin = np.where(F>=0,
            np.where(F < 0.0001, M-1, np.ceil(1/(gamma_X*F/(Tc/Tx)))),
                np.where(F <- 0.0001, -(M-1), np.floor(1/(gamma_X*F/(Tc/Tx)))))

    G = (1/tau2)*((b2*S+WE21*(x/s1)**2+WE22*(y/s2)**2)*(1-y/s2)
                    -(1+WI21*(x/s1)**2+WI22*(y/s2)**2)*y/s2)

    Gin = np.where(G>=0,
            np.where(G < 0.0001, M-1, np.ceil(1/(gamma_Y*G/(Tc/Ty)))),
                np.where(G <- 0.0001, -(M-1), np.floor(1/(gamma_Y*G/(Tc/Ty)))))

    return Fin, Gin



@njit
def calc_time_evolution_eca(init_X, init_Y, init_P, init_Q, init_phX, init_phY,
                        N, M, Tc, Tx, Ty,
                        sT, eT, Fin, Gin):

    # variables
    x_next = x_previous = init_X
    y_next = y_previous = init_Y
    p_next = p_previous = init_P
    q_next = q_previous = init_Q
    phx_next = phx_previous = init_phX
    phy_next = phy_previous = init_phY
    Cx = np.zeros_like(init_phX)
    Cy = np.zeros_like(init_phY)

    # Time
    T = 0

    # Calculate total step for storing
    total_step = int(eT/Tc)+1
    index_start = int(sT/Tc)
    store_step = (total_step - index_start) // 100 + 1 if total_step > index_start else 0

    # Get size of x, y
    n = init_X.size if init_X.ndim>0 else 1

    # store return arrays
    t_hist = np.zeros(store_step)
    x_hist = np.zeros((n, store_step))
    y_hist = np.zeros((n, store_step))

    Fx = np.empty(len(x_previous), dtype=np.int32)
    Fy = np.empty(len(x_previous), dtype=np.int32)

    idx = 0


    for i in range(total_step):

        # time evolution
        T, phx_next, phy_next, Cx, Cy = time_evolution(Tc, Tx, Ty, T, phx_previous, phy_previous)

        # calculate
        for f_idx in range(len(x_previous)):
            Fx[f_idx] = Fin[x_previous[f_idx], y_previous[f_idx]]
            Fy[f_idx] = Gin[x_previous[f_idx], y_previous[f_idx]]

        absFx = np.abs(Fx)
        absFy = np.abs(Fy)

        # cal auxiliary variables
        p_next = np.where(Cx==1,
                            np.where((p_previous < absFx) & (p_previous < M - 1), p_previous + 1, 0), p_previous).astype(np.int32)

        q_next = np.where(Cy==1,
                            np.where((q_previous < absFy) & (q_previous < M - 1), q_previous + 1, 0), q_previous).astype(np.int32)

        x_next = np.where(Cx==1,
                            np.where((p_previous >= absFx) | (p_previous >= M -1),
                                np.where((Fx >=0) & (x_previous < N-1), x_previous + 1,
                                    np.where((Fx < 0) & (x_previous > 0), x_previous - 1, x_previous)),
                                x_previous),
                            x_previous).astype(np.int32)

        y_next = np.where(Cy==1,
                            np.where((q_previous >= absFy) | (q_previous >= M -1),
                                np.where((Fy >=0) & (y_previous < N-1), y_previous + 1,
                                    np.where((Fy < 0) & (y_previous > 0), y_previous - 1, y_previous)),
                                y_previous),
                            y_previous).astype(np.int32)

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
                x_hist[:, idx_insert] = x_previous
                y_hist[:, idx_insert] = y_previous

            idx += 1


    return t_hist, x_hist, y_hist




@njit
def time_evolution(Tc, Tx, Ty, T, phx_previous, phy_previous):

    T = T + Tc

    Cx = np.where(phx_previous >= (1-Tc/Tx), 1, 0)
    Cy = np.where(phy_previous >= (1-Tc/Ty), 1, 0)

    phx_next = phx_previous + Tc/Tx
    phy_next = phy_previous + Tc/Ty

    phx_next = np.where(phx_next >= 1, phx_next - 1, phx_next)
    phy_next = np.where(phy_next >= 1, phy_next - 1, phy_next)


    return T, phx_next, phy_next, Cx, Cy