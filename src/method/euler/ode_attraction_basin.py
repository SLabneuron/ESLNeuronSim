# -*- coding: utf-8 -*-
"""
Created on: 2024-10-22
Updated on: 2024-11-12

@author: shirafujilab

Contents: attracction basin

"""

# import standard library
import numpy as np
import pandas as pd
import os


import datetime

# import my library
from src.method.euler.ode_basic import  calc_time_evolution_ode


class ABODE:

    def __init__(self, params, filename):

        # get params
        self.params = params

        self.filename = filename
        print(self.filename)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)


    def run(self):

        """ Condtions """

        params = self.params

        # variables
        self.x = np.arange(0, 0.81, 0.01)
        self.y = np.arange(0, 0.81, 0.01)

        init_x, init_y = np.meshgrid(self.x, self.y)

        init_x = init_x.flatten()
        init_y = init_y.flatten()

        num_IC = init_x.size        # initial condtions

        """ parameters """

        # time
        sT, eT, h = 1000, 1300, params["h"]

        # params (fx)
        tau1, b1, S, WE11, WE12, WI11, WI12 = params['tau1'], params['b1'], params['S'], params['WE11'], params['WE12'], params['WI11'], params['WI12']

        # params (fy)
        tau2, b2, WE21, WE22, WI21, WI22 = params['tau2'], params['b2'], params['WE21'], params['WE22'], params['WI21'], params['WI22']

        # store hist
        max_values = np.zeros(num_IC)
        min_values = np.zeros(num_IC)

        """ run simulation """
        bench_sT = datetime.datetime.now()
        print("\n start: ", bench_sT)

        max_values, min_values = self.calc_attraction_basin(init_x, init_y,
                                                            sT, eT, h,
                                                            tau1, b1, S, WE11, WE12, WI11, WI12,
                                                            tau2, b2, WE21, WE22, WI21, WI22,
                                                            max_values, min_values)

        bench_eT = datetime.datetime.now()
        print("end: ", bench_eT)

        print("bench mark: ", bench_eT - bench_sT)

        """ analysis """

        # round operation
        x_max_rounded = np.round(max_values, 3)
        x_min_rounded = np.round(min_values, 3)

        # [(x_max[0], x_min[0]), (x_max[1], x_min[1]), ...]
        x_max_min = np.column_stack((x_max_rounded, x_min_rounded))

        # get unique (max, min) combination
        x_max_min_sort = np.unique(x_max_min, axis=0)

        # analysis
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

        """ Store results as a DataFrame """

        # make df
        df = pd.DataFrame({
            "init_x": self.params["init_x"],
            "init_y": self.params["init_y"],
            "max_1": x_max_min_sort[0][0],
            "max_2": x_max_min_sort[1][0],
            "max_3": x_max_min_sort[2][0],
            "min_1": x_max_min_sort[0][1],
            "min_2": x_max_min_sort[1][1],
            "min_3": x_max_min_sort[2][1],
            "state": state
        })

        # specify column order
        df = df[["init_x", "init_y", "max_1", "max_2", "max_3",
                 "min_1", "min_2", "min_3", "state"]]

        # Save to CSV
        try:
            df.to_csv(self.filename, index=False)
            print(f"Results saved to {self.filename}")
        except Exception as e:
            print(f"Error saving results to {self.filename}: {e}")

        print("end: ", datetime.datetime.now())


    def calc_attraction_basin(self, init_x, init_y,
                              sT, eT, h,
                              tau1, b1, S, WE11, WE12, WI11, WI12,
                              tau2, b2, WE21, WE22, WI21, WI22,
                              max_values, min_values):

        # Calculate
        _, x_hist, _ = calc_time_evolution_ode(init_x, init_y,
                                                sT, eT, h,
                                                tau1, b1, S, WE11, WE12, WI11, WI12,
                                                tau2, b2, WE21, WE22, WI21, WI22)

        max_values = np.max(x_hist, axis=0)
        min_values = np.min(x_hist, axis=0)

        return max_values, min_values