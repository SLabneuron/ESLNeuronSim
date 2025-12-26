# -*- coding: utf-8 -*-
"""
Created on: 2023-7-23
Updated on: 2024-11-15

@author: shirafujilab
"""


import numpy as np

from numba import njit


@njit
def calc_time_evolution_eca(init_X, init_Y, init_P, init_Q, init_phX, init_phY,
                        N, M, s1, s2, gamma_X, gamma_Y, Tc, Tx, Ty,
                        sT, eT,
                        tau1, b1, S, WE11, WE12, WI11, WI12,
                        tau2, b2, WE21, WE22, WI21, WI22):

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

    idx = 0


    for i in range(total_step):

        # time evolution
        T, phx_next, phy_next, Cx, Cy = time_evolution(Tc, Tx, Ty, T, phx_previous, phy_previous)

        # calculate
        Fx = dde_X(tau1, b1, S, WE11, WE12, WI11, WI12, M, s1, s2, gamma_X, Tc, Tx ,x_previous, y_previous)
        Fy = dde_Y(tau2, b2, S, WE21, WE22, WI21, WI22, M, s1, s2, gamma_Y, Tc, Ty ,x_previous, y_previous)

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
def dde_X(tau1, b1, S, WE11, WE12, WI11, WI12,
          M, s1, s2, gamma_X, Tc, Tx ,x_previous, y_previous):

    Fin = (1/tau1)*((b1*S+WE11*(x_previous/s1)**2+WE12*(y_previous/s2)**2)*(1-x_previous/s1)
                        -(1+WI11*(x_previous/s1)**2+WI12*(y_previous/s2)**2)*x_previous/s1)

    # First: if Fin == 0, result = M-1
    #Fin = np.where(np.abs(Fin) <= 0.0001, M-1, gamma_X/Fin*(Tc/Tx))
    Fin = np.where(np.abs(Fin) <= 0.0001, M-1, 1/(gamma_X*Fin/(Tc/Tx)))

    # Second: if Fin > 0
    positive_condition = np.floor(Fin) >= M - 1
    Fin = np.where(positive_condition, M-1, Fin)

    # Third: if Fin < 0
    negative_condition = np.ceil(Fin) <= -(M - 1)
    Fin = np.where(negative_condition, -(M-1), Fin)

    Fin = np.where(Fin >= 0, np.ceil(Fin), np.floor(Fin))

    return Fin

@njit
def dde_Y(tau2, b2, S, WE21, WE22, WI21, WI22,
          M, s1, s2, gamma_Y, Tc, Ty ,x_previous, y_previous):

    Gin = (1/tau2)*((b2*S+WE21*(x_previous/s1)**2+WE22*(y_previous/s2)**2)*(1-y_previous/s2)
                        -(1+WI21*(x_previous/s1)**2+WI22*(y_previous/s2)**2)*y_previous/s2)

    # First: if Gin == 0, result = M-1
    #Gin = np.where(np.abs(Gin) <= 0.0001, M-1, gamma_Y/Gin*(Tc/Ty))
    Gin = np.where(np.abs(Gin) <= 0.0001, M-1, 1/(gamma_Y*Gin/(Tc/Ty)))

    # Second: if Gin > 0
    positive_condition = np.floor(Gin) >= M - 1
    Gin = np.where(positive_condition, M-1, Gin)

    # Third: if Gin < 0
    negative_condition = np.ceil(Gin) <= -(M - 1)
    Gin = np.where(negative_condition, -(M-1), Gin)

    Gin = np.where(Gin >= 0, np.ceil(Gin), np.floor(Gin))

    return Gin

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





# -*- coding: utf-8 -*-
"""
Created on: 2024-10-22
Updated on: 2024-11-12

@author: shirafujilab

Contents: bifurcation for S
    X: 0, 2, 4, ..., 63
    Y: 0, 2, 4, ..., 63

    Fixed: Q, P, Q, phX, phY


Benchmark:

    size of X, Y = 64*64 -> 14 minutes
    size of X, Y = 32*64 -> 3.5 minutes
    
    size of X, Y = 32*32 -> 50 sec

"""

# import standard library
import numpy as np
import pandas as pd
import os

from numba import njit, prange

import datetime

# import my library
from src.method.eca.eca_basic import  calc_time_evolution_eca


class BifECA:

    def __init__(self, params, filename):

        # get params
        self.params = params

        self.filename = filename
        print(self.filename)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)


    def run(self):

        """ Condtions """

        # get params
        params = self.params

        # variables
        self.x = np.arange(0, self.params["N"]-1, 2).astype(np.int32)
        self.y = np.arange(0, self.params["N"]-1, 2).astype(np.int32)

        init_x, init_y = np.meshgrid(self.x, self.y)

        init_x = init_x.flatten()
        init_y = init_y.flatten()

        num_IC = init_x.size

        """ bifurcation """

        # Condtions of S
        bif_S = np.arange(0, 0.81, 0.01)
        num_S = len(bif_S)

        """ parameters """

        # Expand other parameters to match the size of xx and yy
        init_P = np.full_like(init_x, self.params["init_P"], dtype=np.int32)
        init_Q = np.full_like(init_x, self.params["init_Q"], dtype=np.int32)
        init_phX = np.full_like(init_x, self.params["init_phX"], dtype=np.float64)
        init_phY = np.full_like(init_x, self.params["init_phY"], dtype=np.float64)

        # time
        sT, eT = params["sT"], params["eT"]

        # params (fx)
        tau1, b1, WE11, WE12, WI11, WI12 = params['tau1'], params['b1'], params['WE11'], params['WE12'], params['WI11'], params['WI12']

        # params (fy)
        tau2, b2, WE21, WE22, WI21, WI22 = params['tau2'], params['b2'], params['WE21'], params['WE22'], params['WI21'], params['WI22']

        # CA params
        N, M, s1, s2, gamma_X, gamma_Y, Tc, Tx, Ty = params["N"], params["M"], params["s1"], params["s2"], params["gamma_X"], params["gamma_Y"], params["Tc"], params["Tx"], params["Ty"]

        # store hist
        max_values = np.zeros((num_S, num_IC))
        min_values = np.zeros((num_S, num_IC))

        """ run simulation """
        bench_sT = datetime.datetime.now()
        print("\n start: ", bench_sT)

        max_values, min_values = self.calc_bifurcation(init_x, init_y, init_P, init_Q, init_phX, init_phY,
                        N, M, s1, s2, gamma_X, gamma_Y, Tc, Tx, Ty,
                        sT, eT,
                        tau1, b1, bif_S, WE11, WE12, WI11, WI12,
                        tau2, b2, WE21, WE22, WI21, WI22,
                        max_values, min_values)

        bench_eT = datetime.datetime.now()
        print("end: ", bench_eT)

        print("bench mark: ", bench_eT - bench_sT)

        """ Store results as a DataFrame """

        num_points = len(self.x)

        # 各カラムデータの長さを揃える
        Q_array = self.params["Q"]
        S_array = np.repeat(bif_S, num_points ** 2)
        X_array = np.tile(init_x, num_S)
        Y_array = np.tile(init_y, num_S)
        max_val_array = max_values.flatten()
        min_val_array = min_values.flatten()

        df = pd.DataFrame({
            "Q": Q_array,
            "S": S_array,               # Repeat S for each grid point
            "x": X_array,
            "y": Y_array,
            "max_val": max_val_array,
            "min_val": min_val_array
        })

        """ Save to CSV """
        try:
            df.to_csv(self.filename, index=False)
            print(f"Results saved to {self.filename}")
        except Exception as e:
            print(f"Error saving results to {self.filename}: {e}")


    @staticmethod
    @njit(parallel=True)
    def calc_bifurcation(init_x, init_y, init_P, init_Q, init_phX, init_phY,
                        N, M, s1, s2, gamma_X, gamma_Y, Tc, Tx, Ty,
                        sT, eT,
                        tau1, b1, bif_S, WE11, WE12, WI11, WI12,
                        tau2, b2, WE21, WE22, WI21, WI22,
                        max_values, min_values):

        for idx in prange(len(bif_S)):

            S = bif_S[idx]

            _, x_hist, _ = calc_time_evolution_eca(init_x, init_y, init_P, init_Q, init_phX, init_phY,
                                                         N, M, s1, s2, gamma_X, gamma_Y, Tc, Tx, Ty,
                                                         sT, eT,
                                                         tau1, b1, S, WE11, WE12, WI11, WI12,
                                                         tau2, b2, WE21, WE22, WI21, WI22)

            num_vars, num_steps = x_hist.shape

            x_max = np.full(num_vars, -np.inf)
            x_min = np.full(num_vars, np.inf)

            # max, min (numba does not support)
            for i in range(num_vars):
                for j in range(num_steps):
                    val = x_hist[i, j]
                    if val > x_max[i]:
                        x_max[i] = val
                    if val < x_min[i]:
                        x_min[i] = val

            max_values[idx, :] = x_max
            min_values[idx, :] = x_min

        return max_values, min_values