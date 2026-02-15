# -*- coding: utf-8 -*-
"""
Created on: 2024-10-22
Updated on: 2024-11-12

@author: shirafujilab

Contents: Parameter region analysis for bifurcation diagram with two parameters (S and Q)

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


class PRODE:

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
        x = np.arange(0, 0.80, 0.1)
        y = np.arange(0, 0.80, 0.1)

        xx_mesh, yy_mesh = np.meshgrid(x, y)
        xx, yy = xx_mesh.flatten(), yy_mesh.flatten()
        conds_size = xx.size

        # parameter
        sT, eT, h = 1500, 2000, params["h"]
        tau1, b1, WE11, WE12, WI11, WI12 = params['tau1'], params['b1'], params['WE11'], params['WE12'], params['WI11'], params['WI12']
        tau2, b2, WE21, WE22, WI21, WI22 = params['tau2'], params['b2'], params['WE21'], params['WE22'], params['WI21'], params['WI22']

        # store step
        total_step = int(eT/h)+1
        index_start = int(sT/h)
        store_step = (total_step - index_start) // 100 + 1 if total_step > index_start else 0

        """ bifurcation """

        # Conditions of S, Q
        bif_S = np.arange(0.20, 0.70, 0.01)
        bif_Q = np.arange(0.20, 0.70, 0.01)

        num_S = bif_S.size
        num_Q = bif_Q.size

        # for store results
        S_hist = np.zeros((num_S, num_Q, conds_size))
        Q_hist = np.zeros((num_S, num_Q, conds_size))
        xmax_hist = np.zeros((num_S, num_Q, conds_size))
        xmin_hist = np.zeros((num_S, num_Q, conds_size))

        """ run simulation """
        bench_sT = datetime.datetime.now()
        print("\n start: ", bench_sT)

        for idx_s in range(num_S):

            for idx_q in range(num_Q):

                Q = bif_Q[idx_q]

                # update relative values
                if params["param set"] in ["set 1", "set 2", "set 3"]:
                    b1, b2, WI12 = 0.13 * (1 + Q), 0, 0.5*Q

                else:
                    b1, b2, WI12 = 0.13*(1-Q), 0.26*Q, 0

                x_max, x_min = self.calc_parameter_region(xx, yy, h,
                                                          tau1, b1, bif_S[idx_s], WE11, WE12, WI11, WI12,
                                                          tau2, b2, WE21, WE22, WI21, WI22,
                                                          total_step, index_start, store_step)

                S_hist[idx_s, idx_q, :] = bif_S[idx_s]
                Q_hist[idx_s, idx_q, :] = Q
                xmax_hist[idx_s, idx_q, :] = x_max
                xmin_hist[idx_s, idx_q, :] = x_min

                print("proccess: -*-*-*-*- ", round(((idx_s*num_S + idx_q)/ num_S/num_Q *100),  2), "% -*-*-*-*- ")

        bench_eT = datetime.datetime.now()

        print("end: ", bench_eT)
        print("bench mark: ", bench_eT - bench_sT)

        """ analysis state in (Q, S) """
        result_list = []

        for idx_s in range(num_S):
            for idx_q in range(num_Q):
                result = self.analyze_results(bif_Q[idx_q], bif_S[idx_s], xmax_hist[idx_s, idx_q, :], xmin_hist[idx_s, idx_q, :])
                result_list.append(result)

        """ Store results as a DataFrame """

        # make dataframe
        df = pd.DataFrame(result_list)

        # specify column order
        df = df[["Q", "S", "max_1", "max_2", "max_3",
                 "min_1", "min_2", "min_3", "state"]]

        """ Save to CSV """

        try:
            df.to_csv(self.filename, index=False)
            print(f"Results saved to {self.filename}")
        except Exception as e:
            print(f"Error saving results to {self.filename}: {e}")


    @staticmethod
    @njit(parallel = True)
    def calc_parameter_region(xx, yy, h,
                              tau1, b1, S, WE11, WE12, WI11, WI12,
                              tau2, b2, WE21, WE22, WI21, WI22,
                              total_step, index_start, store_step):


        # total
        total_conds = xx.size

        x_max_hist = np.empty(total_conds, dtype=np.float32)
        x_min_hist = np.empty(total_conds, dtype=np.float32)

        for idx in prange(total_conds):

            _, x_hist, _ = calc_time_evolution_ode(xx[idx], yy[idx], h,
                                                   tau1, b1, S, WE11, WE12, WI11, WI12,
                                                   tau2, b2, WE21, WE22, WI21, WI22,
                                                   total_step, index_start, store_step)

            # return
            x_max_hist[idx] = np.max(x_hist)
            x_min_hist[idx] = np.min(x_hist)

        return x_max_hist, x_min_hist


    def analyze_results(self, Q, S, x_max, x_min):

        # round operation
        x_max_rounded = np.round(x_max, 3)
        x_min_rounded = np.round(x_min, 3)

        # [(x_max[0], x_min[0]), (x_max[1], x_min[1]), ...]
        x_max_min = np.column_stack((x_max_rounded, x_min_rounded))

        # get unique (max, min) combination
        x_max_min_sort = np.unique(x_max_min, axis=0)

        """ analysis """

        required = 3
        current = x_max_min_sort.shape[0]

        if current < required:
            padding = np.array([[None, None]] * (required - current), dtype=object)
            x_max_min_sort = np.vstack((x_max_min_sort, padding))
        else:
            x_max_min_sort = x_max_min_sort[:required]

        # get arrays without (None, None)
        valid_pairs = x_max_min_sort[~np.any(x_max_min_sort == None, axis=1)]

        # judge equilibrium (eq) or periodic orbit (po)
        eq_pairs = []
        po_pairs = []

        for pair in valid_pairs:

            # equilibrium ( < 0.005)
            if pair[0] - pair[1] < 0.005: eq_pairs.append(pair)

            # periodic orbit
            else: po_pairs.append(pair)

        # get unique equilibrium (distance >= 0.015)
        unique_eq = []
        for eq in eq_pairs:
            if all(np.linalg.norm(eq - existing_eq) >= 0.015 for existing_eq in unique_eq):
                unique_eq.append(eq)

        num_eq = len(unique_eq)
        num_po = len(po_pairs)

        """ classified state """

        # 1. monostable
        if num_eq == 1 and num_po == 0: state = 1

        # 2. bistable
        elif num_eq == 2 and num_po == 0: state = 2

        # 3. periodic orbit
        elif num_eq == 0 and num_po == 1: state = 3

        # 4. coexistence (1 eq and 1 po)
        elif num_eq == 1 and num_po == 1: state = 4

        # 5. others
        else: state = 5

        """ Summarized results """
        result = {
            "Q": Q,
            "S": S,
            "max_1": x_max_min_sort[0][0],
            "max_2": x_max_min_sort[1][0],
            "max_3": x_max_min_sort[2][0],
            "min_1": x_max_min_sort[0][1],
            "min_2": x_max_min_sort[1][1],
            "min_3": x_max_min_sort[2][1],
            "state": state
        }

        return result