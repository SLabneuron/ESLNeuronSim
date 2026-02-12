# -*- coding: utf-8 -*-
"""
Created on: 2024-10-22
Updated on: 2024-11-12

@author: shirafujilab

Contents: attracction basin

Benchmark

    X, Y: 64 * 64
    P, Q:  8 *  8
    phX, phY: 10 * 10

    20 minutes


"""

# import standard library
import numpy as np
import pandas as pd
import os

import numba
numba.set_num_threads(15) 
from numba import njit, prange

import datetime

# import my library

from src.analyses.analysis_null_cline import Nullcline

from src.method.eca.eca_basic import  calc_time_evolution_eca, _make_lut_numba

from src.graphics.graphic_attraction_basin import PhasePlanePlotter


class ABECA:

    def __init__(self, master, filename):

        # get params
        self.params = master.params

        self.master = master

        self.filename = filename
        print(self.filename)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)


    def run(self):

        """ initialization """

        # get params
        params = self.params

        # variables
        x = np.arange(0, params["N"], 1, dtype=np.int16)
        y = np.arange(0, params["N"], 1, dtype=np.int16)
        p = np.array([0, 4, 8, 16, 32], dtype=np.int16)
        q = np.array([0, 4, 8, 16, 32], dtype=np.int16)
        phX = np.arange(0, 1.0, 0.3)
        phY = np.arange(0, 1.0, 0.3)

        # meshgrid
        xx_mesh, yy_mesh = np.meshgrid(x, y, indexing = "ij")
        pp_mesh, qq_mesh, phxx_mesh, phyy_mesh = np.meshgrid(p, q, phX, phY)

        # flatten
        xx, yy = xx_mesh.flatten(), yy_mesh.flatten()
        pp, qq, phxx, phyy = pp_mesh.flatten(), qq_mesh.flatten(), phxx_mesh.flatten(), phyy_mesh.flatten()

        # the number of conditions
        all_conds = p.size * q.size * phX.size * phY.size

        # parameters
        sT, eT = 300, 500
        tau1, b1, S, WE11, WE12, WI11, WI12 = params['tau1'], params['b1'], params['S'], params['WE11'], params['WE12'], params['WI11'], params['WI12']
        tau2, b2, WE21, WE22, WI21, WI22 = params['tau2'], params['b2'], params['WE21'], params['WE22'], params['WI21'], params['WI22']
        N, M, s1, s2, Tc, Tx, Wx, Ty, Wy = params["N"], params["M"], params["s1"], params["s2"], params["Tc"], params["Tx"], params["Wx"], params["Ty"], params["Wy"]

        # store step
        total_step = int(eT/Tc)+1
        index_start = int(sT/Tc)
        store_step = (total_step - index_start) // 100 + 1 if total_step > index_start else 0

        # lut (vector field function)
        Fin, Gin = _make_lut_numba(N, M, s1, s2, Tx, Wx, Ty, Wy,
                                    tau1, b1, S, WE11, WE12, WI11, WI12,
                                    tau2, b2, WE21, WE22, WI21, WI22)

        x_size = x.size
        y_size = y.size
        xy_size = x_size*y_size

        # for store results
        xmax_hist = np.zeros((xy_size, all_conds))
        xmin_hist = np.zeros((xy_size, all_conds))
        ymax_hist = np.zeros((xy_size, all_conds))
        ymin_hist = np.zeros((xy_size, all_conds))

        """ run simulation """

        bench_sT = datetime.datetime.now()
        print("\n start: ", bench_sT)
        print("proccess: -*-*-*-*- ", 0, "% -*-*-*-*- ")

        for idx in range(xy_size):

            x_max, x_min, y_max, y_min = self.calc_attraction_basin(
                                                        xx[idx], yy[idx], pp, qq, phxx, phyy,
                                                        N,  M, Tc, Tx, Wx, Ty, Wy,
                                                        total_step, index_start, store_step, Fin, Gin)

            xmax_hist[idx, :] = x_max
            xmin_hist[idx, :] = x_min
            ymax_hist[idx, :] = y_max
            ymin_hist[idx, :] = y_min

            print("proccess: -*-*-*-*- ", round((idx/ xy_size*100),  2), "% -*-*-*-*- ")

        bench_eT = datetime.datetime.now()

        print("end: ", bench_eT)
        print("bench mark: ", bench_eT - bench_sT)


        """ analysis and graphic heatmap """

        # determine state
        result_list = self.analysis_phase_plain(xmax_hist, xmin_hist, ymax_hist, ymin_hist)

        # get nullclines
        self.nullclines_for_graphics()

        # graphic of heatmap, nullclines, timewaveform
        self.graphics_all(xx_mesh, yy_mesh, xx, yy, pp, qq, phxx, phyy, result_list,
                          N, M, Tc, Tx, Wx, Ty, Wy,
                          total_step, index_start, store_step, Fin, Gin)


        """ Store results as a DataFrame """

        # make df
        df = pd.DataFrame({
            "init_x": xx,
            "init_y": yy,
            "state": result_list
        })

        # specify column order
        df = df[["init_x", "init_y",  "state"]]

        # Save to CSV
        try:
            df.to_csv(self.filename, index=False)
            print(f"Results saved to \n {self.filename}")
        except Exception as e:
            print(f"Error saving results to \n {self.filename}: {e}")


    @staticmethod
    @njit(parallel=True)
    def calc_attraction_basin(init_x, init_y, pp, qq, pphX, pphY,
                              N,  M, Tc, Tx, Wx, Ty, Wy,
                              total_step, index_start, store_step, Fin, Gin):

        # conditions number (init_P, init_Q, init_phX, init_phY)
        total_conds =pp.size

        # return
        x_max_hist = np.empty(total_conds, dtype=np.int16)
        x_min_hist = np.empty(total_conds, dtype=np.int16)
        y_max_hist = np.empty(total_conds, dtype=np.int16)
        y_min_hist = np.empty(total_conds, dtype=np.int16)

        # loop
        for idx in prange(total_conds):

            # Calculate
            _, x_hist, y_hist = calc_time_evolution_eca(init_x, init_y, pp[idx], qq[idx], pphX[idx], pphY[idx],
                                                        N, M, Tc, Tx, Wx, Ty, Wy,
                                                        total_step, index_start, store_step, Fin, Gin)

            # prepare max, min
            x_max_hist[idx] = np.max(x_hist)
            x_min_hist[idx] = np.min(x_hist)
            y_max_hist[idx] = np.max(y_hist)
            y_min_hist[idx] = np.min(y_hist)

        return x_max_hist, x_min_hist, y_max_hist, y_min_hist


    def analysis_phase_plain(self, x_max, x_min, y_max, y_min):

        num_xy_conds, num_pqphi_conds = x_max.shape

        # per-cell classification: 0=unclassified, 1=eq, 3=po
        cell_type = np.zeros((num_xy_conds, num_pqphi_conds), dtype=int)
        cell_pair = np.zeros((num_xy_conds, num_pqphi_conds, 2))

        for i in range(num_xy_conds):
            for j in range(num_pqphi_conds):
                cell_pair[i, j, 0] = x_max[i, j]
                cell_pair[i, j, 1] = x_min[i, j]
                if (x_max[i, j] - x_min[i, j]) > 3:
                    cell_type[i, j] = 3  # periodic orbit
                else:
                    cell_type[i, j] = 1  # equilibrium candidate

        # collect all eq pairs and all po pairs across all cells
        all_eq_pairs = []
        all_po_pairs = []

        for i in range(num_xy_conds):
            for j in range(num_pqphi_conds):
                pair = (cell_pair[i, j, 0], cell_pair[i, j, 1])
                if cell_type[i, j] == 1:
                    all_eq_pairs.append(pair)
                elif cell_type[i, j] == 3:
                    all_po_pairs.append(pair)

        # merge logic: find unique attractors
        def find_unique(pairs):
            unique = []
            for p in pairs:
                if p[0] is None:
                    continue
                p_max, p_min = p[0], p[1]
                merged = False
                for k, existing in enumerate(unique):
                    ex_max, ex_min = existing[0], existing[1]
                    if (p_max <= ex_max and p_min >= ex_min) or \
                       (abs(p_max - ex_max) <= 1 and abs(p_min - ex_min) <= 1):
                        merged = True
                        if (p_max - p_min) < (ex_max - ex_min):
                            unique[k] = p
                        break
                if not merged:
                    unique.append(p)
            return unique

        unique_eq = find_unique(all_eq_pairs)
        unique_po = find_unique(all_po_pairs)

        # assign eq index (1, 2, ...) to each unique equilibrium
        # assign each cell to its closest unique attractor
        param_conds = np.zeros((num_xy_conds, num_pqphi_conds), dtype=int)

        for i in range(num_xy_conds):
            for j in range(num_pqphi_conds):
                p_max = cell_pair[i, j, 0]
                p_min = cell_pair[i, j, 1]

                if cell_type[i, j] == 1:
                    # find which unique_eq this belongs to
                    for eq_idx, eq in enumerate(unique_eq):
                        if (p_max <= eq[0] + 1 and p_min >= eq[1] - 1) or \
                           (abs(p_max - eq[0]) <= 1 and abs(p_min - eq[1]) <= 1):
                            param_conds[i, j] = eq_idx + 1  # 1-indexed
                            break

                elif cell_type[i, j] == 3:
                    # find which unique_po this belongs to
                    for po_idx, po in enumerate(unique_po):
                        if (p_max <= po[0] + 1 and p_min >= po[1] - 1) or \
                           (abs(p_max - po[0]) <= 1 and abs(p_min - po[1]) <= 1):
                            # po is numbered after eq
                            param_conds[i, j] = len(unique_eq) + po_idx + 1
                            break

        # classify each init_cond across all param_conds
        result_list = []

        for i in range(num_xy_conds):
            unique_states = set(param_conds[i])
            unique_states.discard(0)

            num_eq_found = sum(1 for s in unique_states if s <= len(unique_eq))
            num_po_found = sum(1 for s in unique_states if s > len(unique_eq))

            if num_eq_found == 1 and num_po_found == 0:
                result_list.append(1)   # monostable
            elif num_eq_found == 2 and num_po_found == 0:
                result_list.append(2)   # bistable
            elif num_eq_found == 0 and num_po_found == 1:
                result_list.append(3)   # periodic orbit
            elif num_eq_found >= 1 and num_po_found >= 1:
                result_list.append(4)   # coexistence
            else:
                result_list.append(5)   # others

        # store representative indices
        self.equ_1_idx = None
        self.equ_2_idx = None
        self.po_idx = None

        for i in range(num_xy_conds):
            for j in range(num_pqphi_conds):
                if param_conds[i, j] == 1 and self.equ_1_idx is None:
                    self.equ_1_idx = (i, j)
                elif param_conds[i, j] == 2 and self.equ_2_idx is None:
                    self.equ_2_idx = (i, j)
                elif param_conds[i, j] > len(unique_eq) and self.po_idx is None:
                    self.po_idx = (i, j)

        return result_list


    def nullclines_for_graphics(self):

        # instance
        inst = Nullcline(self.params)

        # set nullclines
        self.x1_null, self.x2_null = inst.nullcline_fx_x, inst.nullcline_fx_y
        self.y1_null, self.y2_null = inst.nullcline_fy_x, inst.nullcline_fy_y


    def graphics_all(self, xx_mesh, yy_mesh, init_xx, init_yy, pp, qq, phxx, phyy, state,
                     N, M, Tc, Tx, Wx, Ty, Wy,
                     total_step, index_start, store_step, Fin, Gin):

        state = np.array(state)

        # instance of graphics (and graphic heatmap)
        inst = PhasePlanePlotter(xx_mesh, yy_mesh, state.reshape(xx_mesh.shape))

        inst.add_nullclines(self.x1_null*self.params["s1"], self.x2_null*self.params["s2"], color="blue")
        inst.add_nullclines(self.y1_null*self.params["s1"], self.y2_null*self.params["s2"], color="orange")

        # only an equilibrium
        if (self.equ_1_idx != None) and (self.equ_2_idx == None):

            x = init_xx[self.equ_1_idx[0]]
            y = init_yy[self.equ_1_idx[0]]

            P = pp[self.equ_1_idx[1]]
            Q = qq[self.equ_1_idx[1]]
            phX = phxx[self.equ_1_idx[1]]
            phY = phyy[self.equ_1_idx[1]]

            _, x_hist, y_hist = calc_time_evolution_eca(x, y, P, Q, phX, phY,
                                                        N, M, Tc, Tx, Wx, Ty, Wy,
                                                        total_step, index_start, store_step, Fin, Gin)

            inst.add_result(x_hist, y_hist, c="red", l="equ")

        # two equilibria
        elif (self.equ_1_idx != None) and (self.equ_2_idx != None):

            x = init_xx[self.equ_1_idx[0]]
            y = init_yy[self.equ_1_idx[0]]

            P = pp[self.equ_1_idx[1]]
            Q = qq[self.equ_1_idx[1]]
            phX = phxx[self.equ_1_idx[1]]
            phY = phyy[self.equ_1_idx[1]]

            _, x_hist, y_hist = calc_time_evolution_eca(x, y, P, Q, phX, phY,
                                                        N, M, Tc, Tx, Wx, Ty, Wy,
                                                        total_step, index_start, store_step, Fin, Gin)

            inst.add_result(x_hist, y_hist, c="red", l="equ 1")

            x = init_xx[self.equ_2_idx[0]]
            y = init_yy[self.equ_2_idx[0]]

            P = pp[self.equ_2_idx[1]]
            Q = qq[self.equ_2_idx[1]]
            phX = phxx[self.equ_2_idx[1]]
            phY = phyy[self.equ_2_idx[1]]

            _, x_hist, y_hist = calc_time_evolution_eca(x, y, P, Q, phX, phY,
                                                        N, M, Tc, Tx, Wx, Ty, Wy,
                                                        total_step, index_start, store_step, Fin, Gin)

            inst.add_result(x_hist, y_hist, c="blue", l="equ 2")

        # po
        if self.po_idx != None:

            x = init_xx[self.po_idx[0]]
            y = init_yy[self.po_idx[0]]

            P = pp[self.po_idx[1]]
            Q = qq[self.po_idx[1]]
            phX = phxx[self.po_idx[1]]
            phY = phyy[self.po_idx[1]]

            _, x_hist, y_hist = calc_time_evolution_eca(x, y, P, Q, phX, phY,
                                                        N, M, Tc, Tx, Wx, Ty, Wy,
                                                        total_step, index_start, store_step, Fin, Gin)

            inst.add_result(x_hist, y_hist, c="gray", l="periodic orbit")

        inst.show()