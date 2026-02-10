# -*- coding: utf-8 -*-
"""

Created on: 2026-01-13

@author: shirafujilab

Contents: parameter region analysis for bifurcation diagram with two parameters (S and Q)

    X: 0, 4, ..., 63
    Y: 0, 4, ..., 63

    Fixed: P, Q, phX, phY

Bench mark:

    55 - 65 min



"""

# import standard library
import numpy as np
import pandas as pd
import os

import numba
numba.set_num_threads(15)
from numba import njit, prange

import datetime, time
import matplotlib.pyplot as plt

# import my library
from src.method.eca.eca_basic import  calc_time_evolution_eca, _make_lut_numba, _make_rotated_lut_numba
from src.graphics.graphic_lut import _make_rotated_coordinate
from src.graphics.graphic_param_region import match_rate_get_df


class TxTyECA:

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
        x = np.arange(0, self.params["N"], 4, dtype=np.int16)
        y = np.arange(0, self.params["N"], 4, dtype=np.int16)

        xx_mesh, yy_mesh = np.meshgrid(x, y)
        xx, yy = xx_mesh.flatten(), yy_mesh.flatten()
        conds_size = xx.size        # initial conditions

        # parameters
        sT, eT = 300, 500
        tau1, b1, WE11, WE12, WI11, WI12 = params['tau1'], params['b1'], params['WE11'], params['WE12'], params['WI11'], params['WI12']
        tau2, b2, WE21, WE22, WI21, WI22 = params['tau2'], params['b2'], params['WE21'], params['WE22'], params['WI21'], params['WI22']
        N, M, s1, s2, gamma_X, gamma_Y, Tc = params["N"], params["M"], params["s1"], params["s2"], params["gamma_X"], params["gamma_Y"], params["Tc"]

        # store step
        total_step = int(eT/Tc)+1
        index_start = int(sT/Tc)
        store_step = (total_step - index_start) // 100 + 1 if total_step > index_start else 0

        """ bifurcation """

        # Conditions of S, Q
        bif_S = np.arange(0.20, 0.70, 0.005)
        bif_Q = np.arange(0.20, 0.70, 0.005)

        num_S = bif_S.size
        num_Q = bif_Q.size

        # for store results
        S_hist = np.zeros((num_S, num_Q, conds_size))
        Q_hist = np.zeros((num_S, num_Q, conds_size))
        xmax_hist = np.zeros((num_S, num_Q, conds_size))
        xmin_hist = np.zeros((num_S, num_Q, conds_size))

        """ system parameter """
        Tx, Ty = params["Tx"], params["Ty"]

        """ run simulation """
        bench_sT = datetime.datetime.now()
        print("\n start: ", bench_sT)
        
        if params["param set"] == "set 1":
            ode_file_path = r"c:\Storage\02_paper\04_2025_Nolta journal\04_Python\data\results\set 1\forward euler\results\parameter region\20260112155128.csv"
        elif params["param set"] == "set 2":
            ode_file_path = r"c:\Storage\02_paper\04_2025_Nolta journal\04_Python\data\results\set 2\forward euler\results\parameter region\20260112160036.csv"

        """ Store TxTy result """
        result_txty = []

        for _idx_y in range(1, 11, 2):
            for _idx_x in range(1, 11, 2):

                Tx = _idx_x * 0.01 * 2**(1/2)
                Ty = _idx_y * 0.01 * 3**(1/2)

                result_list=[]

                for idx_s in range(num_S):

                    for idx_q in range(num_Q):

                        Q = bif_Q[idx_q]

                        # update relative values
                        if params["param set"] in ["set 1", "set 2", "set 3"]:
                            b1, b2, WI12 = 0.13 * (1 + Q), 0, 0.5*Q

                        else:
                            b1, b2, WI12 = 0.13*(1-Q), 0.26*Q, 0

                        Fin, Gin = _make_lut_numba(N, M, s1, s2, gamma_X, gamma_Y, Tc, Tx, Ty,
                                                tau1, b1, bif_S[idx_s], WE11, WE12, WI11, WI12,
                                                tau2, b2, WE21, WE22, WI21, WI22)

                        x_max, x_min = self.calc_parameter_region(xx, yy, 0, 0, 0, 0,
                                                                N, M, Tc, Tx, Ty,
                                                                total_step, index_start, store_step, Fin, Gin)

                        S_hist[idx_s, idx_q, :] = bif_S[idx_s]
                        Q_hist[idx_s, idx_q, :] = Q
                        xmax_hist[idx_s, idx_q, :] = x_max
                        xmin_hist[idx_s, idx_q, :] = x_min

                        result = self.analyze_results(bif_Q[idx_q], bif_S[idx_s], xmax_hist[idx_s, idx_q, :], xmin_hist[idx_s, idx_q, :])
                        result_list.append(result)

                df = pd.DataFrame(result_list)

                df = df[["Q", "S", "max_1", "max_2", "max_3",
                 "min_1", "min_2", "min_3", "state"]]

                rate = match_rate_get_df(ode_file_path, df)
                print(Tx, Ty, f"{rate*100:.6f}")
                result_txty.append([Tx, Ty, rate*100, max(rate*100-90,0)])

                #print("proccess: -*-*-*-*- ", round(((_idx_x*10 + _idx_y)/ 100 *100),  2), "% -*-*-*-*- ")

        bench_eT = datetime.datetime.now()

        print("end: ", bench_eT)
        print("bench mark: ", bench_eT - bench_sT)

        ddf = pd.DataFrame(result_txty, columns=["x", "y", "res1", "res2"])
        Z = ddf.pivot(index="y", columns="x", values="res2")

        plt.imshow(Z.values, origin="lower", aspect="auto")
        plt.xticks(range(len(Z.columns)), Z.columns, rotation=45)
        plt.yticks(range(len(Z.index)), Z.index)
        plt.xlabel("x")
        plt.ylabel("y")
        plt.colorbar(label="4th column value")
        plt.tight_layout()
        plt.show()





    def run_rotated(self):

        """ Initialization """

        # get params
        params = self.params

        # variables
        x = np.arange(0, self.params["N"], 4, dtype=np.int16)
        y = np.arange(0, self.params["N"], 4, dtype=np.int16)

        xx_mesh, yy_mesh = np.meshgrid(x, y)
        xx, yy = xx_mesh.flatten(), yy_mesh.flatten()
        conds_size = xx.size        # initial conditions

        # parameters
        sT, eT = 300, 500
        tau1, b1, WE11, WE12, WI11, WI12 = params['tau1'], params['b1'], params['WE11'], params['WE12'], params['WI11'], params['WI12']
        tau2, b2, WE21, WE22, WI21, WI22 = params['tau2'], params['b2'], params['WE21'], params['WE22'], params['WI21'], params['WI22']
        N, M, s1, s2, gamma_X, gamma_Y, Tc = params["N"], params["M"], params["s1"], params["s2"], params["gamma_X"], params["gamma_Y"], params["Tc"]
        deg = params["deg"]

        # store step
        total_step = int(eT/Tc)+1
        index_start = int(sT/Tc)
        store_step = (total_step - index_start) // 100 + 1 if total_step > index_start else 0

        """ bifurcation """

        # Conditions of S, Q
        bif_S = np.arange(0.20, 0.70, 0.005)
        bif_Q = np.arange(0.20, 0.70, 0.005)

        num_S = bif_S.size
        num_Q = bif_Q.size

        # for store results
        S_hist = np.zeros((num_S, num_Q, conds_size))
        Q_hist = np.zeros((num_S, num_Q, conds_size))
        xmax_hist = np.zeros((num_S, num_Q, conds_size))
        xmin_hist = np.zeros((num_S, num_Q, conds_size))

        """ system parameter """
        Tx, Ty = params["Tx"], params["Ty"]

        """ run simulation """
        bench_sT = datetime.datetime.now()
        print("\n start: ", bench_sT)

        if params["param set"] == "set 1":
            ode_file_path = r"c:\Storage\02_paper\04_2025_Nolta journal\04_Python\data\results\set 1\forward euler\results\parameter region\20260112155128.csv"
        elif params["param set"] == "set 2":
            ode_file_path = r"c:\Storage\02_paper\04_2025_Nolta journal\04_Python\data\results\set 2\forward euler\results\parameter region\20260112160036.csv"

        rotated_x, rotated_y =_make_rotated_coordinate(N, deg) # (size, degree) Fig. 11 is theta = 1

        """ store TxTy result """
        result_txty = []
        
        for _idx_y in range(1, 11, 2):
            for _idx_x in range(1, 11, 2):

                Tx = _idx_x * 0.01 * 2**(1/2)
                Ty = _idx_y * 0.01 * 3**(1/2)

                result_list=[]

                for idx_s in range(num_S):

                    for idx_q in range(num_Q):

                        Q = bif_Q[idx_q]

                        # update relative values
                        if params["param set"] in ["set 1", "set 2", "set 3"]:
                            b1, b2, WI12 = 0.13 * (1 + Q), 0, 0.5*Q

                        else:
                            b1, b2, WI12 = 0.13*(1-Q), 0.26*Q, 0

                        Fin, Gin = _make_rotated_lut_numba(N, M, s1, s2, gamma_X, gamma_Y, Tc, Tx, Ty,
                                                tau1, b1, bif_S[idx_s], WE11, WE12, WI11, WI12,
                                                tau2, b2, WE21, WE22, WI21, WI22,
                                                rotated_x, rotated_y, deg)

                        x_max, x_min = self.calc_parameter_region(xx, yy, 0, 0, 0, 0,
                                                                N, M, Tc, Tx, Ty,
                                                                total_step, index_start, store_step, Fin, Gin)

                        S_hist[idx_s, idx_q, :] = bif_S[idx_s]
                        Q_hist[idx_s, idx_q, :] = Q
                        xmax_hist[idx_s, idx_q, :] = x_max
                        xmin_hist[idx_s, idx_q, :] = x_min
                        
                        result = self.analyze_results(bif_Q[idx_q], bif_S[idx_s], xmax_hist[idx_s, idx_q, :], xmin_hist[idx_s, idx_q, :])
                        result_list.append(result)

                df = pd.DataFrame(result_list)

                df = df[["Q", "S", "max_1", "max_2", "max_3",
                 "min_1", "min_2", "min_3", "state"]]

                rate = match_rate_get_df(ode_file_path, df)
                print(Tx, Ty, f"{rate*100:.6f}")
                result_txty.append([Tx, Ty, rate*100, max(rate*100-90,0)])


        bench_eT = datetime.datetime.now()

        print("end: ", bench_eT)
        print("bench mark: ", bench_eT - bench_sT)

        ddf = pd.DataFrame(result_txty, columns=["x", "y", "res1", "res2"])
        Z = ddf.pivot(index="y", columns="x", values="res2")

        plt.imshow(Z.values, origin="lower", aspect="auto")
        plt.xticks(range(len(Z.columns)), Z.columns, rotation=45)
        plt.yticks(range(len(Z.index)), Z.index)
        plt.xlabel("x")
        plt.ylabel("y")
        plt.colorbar(label="4th column value")
        plt.tight_layout()
        plt.show()



    @staticmethod
    @njit(parallel=True)
    def calc_parameter_region(xx, yy, pp, qq, phxx, phyy,
                              N, M, Tc, Tx, Ty,
                              total_step, index_start, store_step, Fin, Gin):

        # conditions number (x, y)
        total_conds = xx.size

        # return
        x_max_hist = np.empty(total_conds, dtype=np.int16)
        x_min_hist = np.empty(total_conds, dtype=np.int16)

        # loop
        for idx in prange(total_conds):

            _, x_hist, _ = calc_time_evolution_eca(xx[idx], yy[idx], pp, qq, phxx, phyy,
                                                   N, M, Tc, Tx, Ty,
                                                   total_step, index_start, store_step, Fin, Gin)

            # update max, min
            x_max_hist[idx] = np.max(x_hist)
            x_min_hist[idx] = np.min(x_hist)

        return x_max_hist, x_min_hist


    def analyze_results(self, Q, S, x_max, x_min):

        # [(x_max[0], x_min[0]), (x_max[1], x_min[1]), ...]
        x_max_min = np.column_stack((x_max, x_min))

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

            # equilibirum ( <= 3)
            if pair[0] - pair[1] <= 3: eq_pairs.append(pair)

            # periodic orbit
            else: po_pairs.append(pair)

        # get unique equilibrium (distance >= 3)
        unique_eq = []

        for eq in eq_pairs:
            if all(np.linalg.norm(eq - existing_eq) >= 3 for existing_eq in unique_eq):
                unique_eq.append(eq)

        # count up eq and po
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


