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

from numba import njit, prange

import datetime

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

        """ Conditions """

        params = self.params

        # variables
        self.x = np.arange(0, 0.81, 0.02)
        self.y = np.arange(0, 0.81, 0.02)

        init_x, init_y = np.meshgrid(self.x, self.y)

        init_x = init_x.flatten()
        init_y = init_y.flatten()

        num_IC = init_x.size

        # Conditions of S
        bif_S = np.arange(0, 0.81, 0.01)
        num_S = len(bif_S)

        # Conditions of Q
        bif_Q = np.arange(0, 0.81, 0.01)
        num_Q = len(bif_Q)

        """ parameters """

        # time
        sT, eT, h = 1000, 1300, params["h"]

        # params (fx)
        tau1, b1, WE11, WE12, WI11, WI12 = params['tau1'], params['b1'], params['WE11'], params['WE12'], params['WI11'], params['WI12']

        # params (fy)
        tau2, b2, WE21, WE22, WI21, WI22 = params['tau2'], params['b2'], params['WE21'], params['WE22'], params['WI21'], params['WI22']

        # parameter set
        pset = params["param set"]

        """ run simulation """
        bench_sT = datetime.datetime.now()
        print("\n start: ", bench_sT)

        Q_list, S_list, x_max_list, x_min_list = self.calc_parameter_region(init_x, init_y,
                                                                            sT, eT, h,
                                                                            tau1, b1, WE11, WE12, WI11, WI12,
                                                                            tau2, b2, WE21, WE22, WI21, WI22,
                                                                            bif_Q, bif_S, pset)

        bench_eT = datetime.datetime.now()
        print("end: ", bench_eT)

        print("bench mark: ", bench_eT - bench_sT)

        """ analysis state in (Q, S) """

        result_list = []
        total_iterations = len(Q_list)

        for idx in range(total_iterations):
            Q = Q_list[idx]
            S = S_list[idx]
            x_max = x_max_list[idx]
            x_min = x_min_list[idx]

            result = self.analyze_results(Q, S, x_max, x_min)
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
    def calc_parameter_region(init_x, init_y,
                                sT, eT, h,
                                tau1, b1, WE11, WE12, WI11, WI12,
                                tau2, b2, WE21, WE22, WI21, WI22,
                                bif_Q, bif_S, pset
                                ):

        num_Q = len(bif_Q)
        num_S = len(bif_S)
        num_IC = init_x.size

        # total
        total_iterations = num_Q * num_S

        Q_list = np.empty(total_iterations)
        S_list = np.empty(total_iterations)
        x_max_list = [np.empty(num_IC) for _ in range(total_iterations)]
        x_min_list = [np.empty(num_IC) for _ in range(total_iterations)]

        for idx in prange(total_iterations):

            Q_idx = idx // num_S
            S_idx = idx % num_S

            Q = bif_Q[Q_idx]
            S = bif_S[S_idx]

            if pset == "set 1" or pset == "set 2" or pset == "set 3":

                # update relative values
                b1 = 0.13 * (1 + Q)
                b2 = 0
                WI12 = 0.5*Q

            elif pset == "set 4":

                # update relative values
                b1 = 0.13*(1-Q)
                b2 = 0.26*Q
                WI12 = 0

            else:

                # default
                b1 = 0.13 * (1 + Q)
                b2 = 0
                WI12 = 0.5*Q

            # Calculate
            _, x_hist, _ = calc_time_evolution_ode(init_x, init_y,
                                                    sT, eT, h,
                                                    tau1, b1, S, WE11, WE12, WI11, WI12,
                                                    tau2, b2, WE21, WE22, WI21, WI22)

            """ get maximum and minimum """

            num_steps, num_vars = x_hist.shape

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

            Q_list[idx] = Q
            S_list[idx] = S
            x_max_list[idx] = x_max
            x_min_list[idx] = x_min

        return Q_list, S_list, x_max_list, x_min_list



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