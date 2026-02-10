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
    size of X, Y = 32*32 -> 24 sec (lut access)

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
from src.method.eca.eca_basic import  calc_time_evolution_eca, _make_lut_numba, _make_rotated_lut_numba
from src.graphics.graphic_lut import _make_rotated_coordinate


class BifECA:

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
        x = np.arange(0, params["N"], 2, dtype=np.int16)
        y = np.arange(0, params["N"], 2, dtype=np.int16)

        # meshgrid
        xx_mesh, yy_mesh = np.meshgrid(x, y)

        # flatten
        xx, yy = xx_mesh.flatten(), yy_mesh.flatten()
        conds_size = xx.size

        print("per a parameter: ", conds_size)

        # parameters
        sT, eT = params["sT"], params["eT"]
        tau1, b1, WE11, WE12, WI11, WI12 = params['tau1'], params['b1'], params['WE11'], params['WE12'], params['WI11'], params['WI12']
        tau2, b2, WE21, WE22, WI21, WI22 = params['tau2'], params['b2'], params['WE21'], params['WE22'], params['WI21'], params['WI22']
        N, M, s1, s2, gamma_X, gamma_Y, Tc, Tx, Ty = params["N"], params["M"], params["s1"], params["s2"], params["gamma_X"], params["gamma_Y"], params["Tc"], params["Tx"], params["Ty"]

        # store step
        total_step = int(eT/Tc)+1
        index_start = int(sT/Tc)
        store_step = (total_step - index_start) // 100 + 1 if total_step > index_start else 0


        """ bifurcation """

        # Condtions of S
        bif_S = np.arange(0.20, 0.70, 0.005)
        num_S = bif_S.size

        Q = params["Q"]

        # store hist
        Q_hist = np.zeros((num_S, conds_size))
        S_hist = np.zeros((num_S, conds_size))
        max_hist = np.zeros((num_S, conds_size), dtype=np.int16)
        min_hist = np.zeros((num_S, conds_size), dtype=np.int16)

        """ run simulation """
        bench_sT = datetime.datetime.now()
        print("\n start: ", bench_sT)

        for idx in range(num_S):

            Fin, Gin = _make_lut_numba(N, M, s1, s2, gamma_X, gamma_Y, Tc, Tx, Ty,
                                       tau1, b1, bif_S[idx], WE11, WE12, WI11, WI12,
                                       tau2, b2, WE21, WE22, WI21, WI22)

            x_max, x_min = self.calc_bifurcation(xx, yy, 0, 0, 0, 0,
                                                 N, M, Tc, Tx, Ty,
                                                 total_step, index_start, store_step, Fin, Gin)

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

        df = df[["Q", "S", "max_val", "min_val"]]

        """ Save to CSV """
        try:
            df.to_csv(self.filename, index=False)
            print(f"Results saved to {self.filename}")
        except Exception as e:
            print(f"Error saving results to {self.filename}: {e}")



    def run_rotated(self):

        """ Initialization """

        # get params
        params = self.params

        # variables
        x = np.arange(0, params["N"], 2, dtype=np.int16)
        y = np.arange(0, params["N"], 2, dtype=np.int16)

        # meshgrid
        xx_mesh, yy_mesh = np.meshgrid(x, y)

        # flatten
        xx, yy = xx_mesh.flatten(), yy_mesh.flatten()
        conds_size = xx.size

        print("per a parameter: ", conds_size)

        # parameters
        sT, eT = params["sT"], params["eT"]
        tau1, b1, WE11, WE12, WI11, WI12 = params['tau1'], params['b1'], params['WE11'], params['WE12'], params['WI11'], params['WI12']
        tau2, b2, WE21, WE22, WI21, WI22 = params['tau2'], params['b2'], params['WE21'], params['WE22'], params['WI21'], params['WI22']
        N, M, s1, s2, gamma_X, gamma_Y, Tc, Tx, Ty = params["N"], params["M"], params["s1"], params["s2"], params["gamma_X"], params["gamma_Y"], params["Tc"], params["Tx"], params["Ty"]
        deg = params["deg"]

        # store step
        total_step = int(eT/Tc)+1
        index_start = int(sT/Tc)
        store_step = (total_step - index_start) // 100 + 1 if total_step > index_start else 0


        """ bifurcation """

        # Condtions of S
        bif_S = np.arange(0.20, 0.70, 0.005)
        num_S = bif_S.size

        Q = params["Q"]

        # store hist
        Q_hist = np.zeros((num_S, conds_size))
        S_hist = np.zeros((num_S, conds_size))
        max_hist = np.zeros((num_S, conds_size), dtype=np.int16)
        min_hist = np.zeros((num_S, conds_size), dtype=np.int16)

        """ run simulation """
        bench_sT = datetime.datetime.now()
        print("\n start: ", bench_sT)

        rotated_x, rotated_y =_make_rotated_coordinate(N, deg) # (size, degree)

        for idx in range(num_S):

            Fin, Gin = _make_rotated_lut_numba(N, M, s1, s2, gamma_X, gamma_Y, Tc, Tx, Ty,
                                       tau1, b1, bif_S[idx], WE11, WE12, WI11, WI12,
                                       tau2, b2, WE21, WE22, WI21, WI22,
                                       rotated_x,  rotated_y, deg)

            x_max, x_min = self.calc_bifurcation(xx, yy, 0, 0, 0, 0,
                                                 N, M, Tc, Tx, Ty,
                                                 total_step, index_start, store_step, Fin, Gin)

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

        df = df[["Q", "S", "max_val", "min_val"]]

        """ Save to CSV """
        try:
            df.to_csv(self.filename, index=False)
            print(f"Results saved to {self.filename}")
        except Exception as e:
            print(f"Error saving results to {self.filename}: {e}")



    @staticmethod
    @njit(parallel=True)
    def calc_bifurcation(xx, yy, pp, qq, phxx, phyy,
                         N, M, Tc, Tx, Ty,
                         total_step, index_start, store_step, Fin, Gin):

        # conditinos number (x, y)
        total_conds = xx.size

        # return
        x_max_hist = np.empty(total_conds, dtype=np.int16)
        x_min_hist = np.empty(total_conds, dtype=np.int16)

        # loop
        for idx in prange(total_conds):

            _, x_hist, _ = calc_time_evolution_eca(xx[idx], yy[idx], pp, qq, phxx, phyy,
                                                    N, M, Tc, Tx, Ty,
                                                    total_step, index_start, store_step, Fin, Gin)

            # prepare max, min
            x_max_hist[idx] = np.max(x_hist)
            x_min_hist[idx] = np.min(x_hist)

        return x_max_hist, x_min_hist