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

import numba
numba.set_num_threads(15)
from numba import njit, prange

import datetime, time

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

        """ Initialization """

        # get params
        params = self.params

        # variables
        x = np.arange(0, 0.80, 0.05)
        y = np.arange(0, 0.80, 0.05)

        xx_mesh, yy_mesh = np.meshgrid(x, y)
        xx, yy = xx_mesh.flatten(), yy_mesh.flatten()
        conds_size = xx.size

        # parameter
        sT, eT, h = 500, 700, params["h"]
        tau1, b1, WE11, WE12, WI11, WI12 = params['tau1'], params['b1'], params['WE11'], params['WE12'], params['WI11'], params['WI12']
        tau2, b2, WE21, WE22, WI21, WI22 = params['tau2'], params['b2'], params['WE21'], params['WE22'], params['WI21'], params['WI22']

        # store step
        total_step = int(eT/h)+1
        index_start = int(sT/h)
        store_step = (total_step - index_start) // 100 + 1 if total_step > index_start else 0

        """ bifurcation """

        # Conditions of S
        bif_S = np.arange(0.20, 0.70, 0.005)
        num_S = len(bif_S)
        
        Q = params["Q"]

        # store hist
        Q_hist = np.zeros((num_S, conds_size))
        S_hist = np.zeros((num_S, conds_size))
        max_hist = np.zeros((num_S, conds_size))
        min_hist = np.zeros((num_S, conds_size))

        """ run simulation """
        bench_sT = datetime.datetime.now()
        print("\n start: ", bench_sT)

        for idx in range(num_S):

            x_max, x_min = self.calc_bifurcation(xx, yy, h,
                                                 tau1, b1, bif_S[idx], WE11, WE12, WI11, WI12,
                                                 tau2, b2, WE21, WE22, WI21, WI22,
                                                 total_step, index_start, store_step)

            Q_hist[idx, :] = Q
            S_hist[idx, :] = bif_S[idx]
            max_hist[idx, :] = x_max
            min_hist[idx, :] = x_min

            print("proccess: -*-*-*-*- ", round((idx/ num_S*100),  2), "% -*-*-*-*- ")

        bench_eT = datetime.datetime.now()

        print("end: ", bench_eT)
        print("bench mark: ", bench_eT - bench_sT)


        """ Store results as a DataFrame """

        df = pd.DataFrame({
            "Q": Q_hist.flatten(),
            "S": S_hist.flatten(),
            "max_val": max_hist.flatten(),
            "min_val": min_hist.flatten()
        })

        """ Save to CSV """

        try:
            df.to_csv(self.filename, index=False)
            print(f"Results saved to {self.filename}")
        except Exception as e:
            print(f"Error saving results to {self.filename}: {e}")


    @staticmethod
    @njit(parallel=True)
    def calc_bifurcation(xx, yy, h,
                         tau1, b1, S, WE11, WE12, WI11, WI12,
                         tau2, b2, WE21, WE22, WI21, WI22,
                         total_step, index_start, store_step):

        # conditions number (x, y)
        total_conds = xx.size

        # return
        x_max_hist = np.empty(total_conds, dtype=np.float32)
        x_min_hist = np.empty(total_conds, dtype=np.float32)

        for idx in prange(total_conds):

            _, x_hist, _ = calc_time_evolution_ode(xx[idx], yy[idx], h,
                                                   tau1, b1, S, WE11, WE12, WI11, WI12,
                                                   tau2, b2, WE21, WE22, WI21, WI22,
                                                   total_step, index_start, store_step)

            # store return hist
            x_max_hist[idx] = np.max(x_hist)
            x_min_hist[idx] = np.min(x_hist)

        return x_max_hist, x_min_hist
