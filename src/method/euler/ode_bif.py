# -*- coding: utf-8 -*-
"""
Created on: 2024-10-22
Updated on: 2024-11-12

@author: shirafujilab

Contents: bifurcation for S

"""

# import standard library
import numpy as np
import pandas as pd
import os

from numba import njit, prange

import datetime

# import my library
from src.method.euler.ode_basic import calc_time_evolution_ode


class BifODE:

    def __init__(self, params, filename):

        # get params
        self.params = params

        self.filename = filename
        print(self.filename)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)


    def run(self):

        """ Conditions """

        # get params
        params = self.params

        # variables
        self.x = np.arange(0, 0.81, 0.02)
        self.y = np.arange(0, 0.81, 0.02)

        init_x, init_y = np.meshgrid(self.x, self.y)

        init_x = init_x.flatten()
        init_y = init_y.flatten()

        num_IC = init_x.size

        # bifurcation parameter

        bif_S = np.arange(0, 0.81, 0.01)
        num_S = len(bif_S)

        """ parameters """

        # time
        sT, eT, h = 1000, 1300, params["h"]

        # params (fx)
        tau1, b1, WE11, WE12, WI11, WI12 = params['tau1'], params['b1'], params['WE11'], params['WE12'], params['WI11'], params['WI12']

        # params (fy)
        tau2, b2, WE21, WE22, WI21, WI22 = params['tau2'], params['b2'], params['WE21'], params['WE22'], params['WI21'], params['WI22']

        # store hist
        max_values = np.zeros((num_S, num_IC))
        min_values = np.zeros((num_S, num_IC))

        """ run simulation """
        bench_sT = datetime.datetime.now()
        print("\n start: ", bench_sT)

        max_values, min_values = self.calc_bifurcation(init_x, init_y,
                                                        sT, eT, h,
                                                        tau1, b1, bif_S, WE11, WE12, WI11, WI12,
                                                        tau2, b2, WE21, WE22, WI21, WI22,
                                                        max_values, min_values)

        bench_eT = datetime.datetime.now()
        print("end: ", bench_eT)

        print("bench mark: ", bench_eT - bench_sT)


        """ Store results as a DataFrame """

        num_points = len(self.x)
        df = pd.DataFrame({
            "Q": self.params["Q"],
            "S": np.repeat(bif_S, num_points ** 2),  # Repeat S for each grid point
            "x": np.tile(self.params["init_x"], num_S),
            "y": np.tile(self.params["init_y"], num_S),
            "max_val": max_values.flatten(),
            "min_val": min_values.flatten()
        })

        """ Save to CSV """

        try:
            df.to_csv(self.filename, index=False)
            print(f"Results saved to {self.filename}")
        except Exception as e:
            print(f"Error saving results to {self.filename}: {e}")


    @staticmethod
    @njit(parallel=True)
    def calc_bifurcation(init_x, init_y,
                         sT, eT, h,
                         tau1, b1, bif_S, WE11, WE12, WI11, WI12,
                         tau2, b2, WE21, WE22, WI21, WI22,
                         max_values, min_values):

        for idx in prange(len(bif_S)):

            S = bif_S[idx]

            _, x_hist, _ = calc_time_evolution_ode(init_x, init_y,
                                                sT, eT, h,
                                                tau1, b1, S, WE11, WE12, WI11, WI12,
                                                tau2, b2, WE21, WE22, WI21, WI22)

            num_steps, num_vars = x_hist.shape           # transpose

            x_max = np.full(num_vars, -np.inf)
            x_min = np.full(num_vars, np.inf)

            # max, min (numba does not support)
            for j in prange(num_vars):
                for i in range(num_steps):
                    val = x_hist[i, j]
                    if val > x_max[j]:
                        x_max[j] = val
                    if val < x_min[j]:
                        x_min[j] = val

            max_values[idx, :] = x_max
            min_values[idx, :] = x_min

        return max_values, min_values
