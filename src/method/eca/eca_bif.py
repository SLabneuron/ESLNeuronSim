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