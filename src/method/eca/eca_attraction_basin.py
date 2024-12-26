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

from numba import njit, prange

import datetime

# import my library

from src.analyses.analysis_null_cline import Nullcline

from src.method.eca.eca_basic import  calc_time_evolution_eca

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
        x = np.arange(0, params["N"], 1)                            # 0~64
        y = np.arange(0, params["N"], 1)
        p = np.array([0, 2, 4, 8, 16, 32], dtype=np.int32)         # 0, 2, 4, 8, 16, 32
        q = np.array([0, 2, 4, 8, 16, 32], dtype=np.int32)
        phX = np.arange(0, 1.0, 0.2, dtype=np.float64)             # 0, 0.2, 0.4, 0.6, 0.8
        phY = np.arange(0, 1.0, 0.2, dtype=np.float64)

        # meshgrid
        xx_mesh, yy_mesh = np.meshgrid(x, y)
        pp_mesh, qq_mesh, phxx_mesh, phyy_mesh = np.meshgrid(p, q, phX, phY)

        # flatten
        xx, yy = xx_mesh.flatten(), yy_mesh.flatten()
        pp, qq = pp_mesh.flatten(), qq_mesh.flatten()
        phxx, phyy = phxx_mesh.flatten(), phyy_mesh.flatten()

        # the number of conditions
        val_conds = x.size * y.size                                  # state variables
        all_conds = p.size * q.size * phX.size * phY.size           # (900): all conditions P, Q, phX, phY

        # parameters
        sT, eT = 300, 400
        tau1, b1, S, WE11, WE12, WI11, WI12 = params['tau1'], params['b1'], params['S'], params['WE11'], params['WE12'], params['WI11'], params['WI12']
        tau2, b2, WE21, WE22, WI21, WI22 = params['tau2'], params['b2'], params['WE21'], params['WE22'], params['WI21'], params['WI22']
        N, M, s1, s2, gamma_X, gamma_Y, Tc, Tx, Ty = params["N"], params["M"], params["s1"], params["s2"], params["gamma_X"], params["gamma_Y"], params["Tc"], params["Tx"], params["Ty"]

        # for store results
        x_max_hist = np.zeros((val_conds, all_conds))
        x_min_hist = np.zeros((val_conds, all_conds))
        y_max_hist = np.zeros((val_conds, all_conds))
        y_min_hist = np.zeros((val_conds, all_conds))
        
        print("x_max_hist: ", x_max_hist.shape)


        """ run simulation """

        bench_sT = datetime.datetime.now()
        print("\n start: ", bench_sT)
        print("proccess: -*-*-*-*- ", 0, "% -*-*-*-*- ")

        x_div = xx.reshape(4, -1)
        y_div = yy.reshape(4, -1)

        for iter, init_xx in enumerate(x_div):

            s_iter = iter * len(init_xx)
            e_iter = (iter + 1) * len(init_xx)

            x_max, x_min, y_max, y_min = self.calc_attraction_basin(
                                                        x_div[iter], y_div[iter], pp, qq, phxx, phyy,
                                                        N,  M, s1, s2, gamma_X, gamma_Y, Tc, Tx, Ty,
                                                        sT, eT,
                                                        tau1, b1, S, WE11, WE12, WI11, WI12,
                                                        tau2, b2, WE21, WE22, WI21, WI22)

            x_max_hist[s_iter:e_iter, :] = x_max
            x_min_hist[s_iter:e_iter, :] = x_min
            y_max_hist[s_iter:e_iter, :] = y_max
            y_min_hist[s_iter:e_iter, :] = y_min

            print("proccess: -*-*-*-*- ", round(((iter + 1)/ len(x_div)*100),  2), "% -*-*-*-*- ")

        bench_eT = datetime.datetime.now()

        print("end: ", bench_eT)
        print("bench mark: ", bench_eT - bench_sT)


        """ analysis and graphic heatmap """

        # determine state
        result_list = self.analysis_phase_plain(x_max_hist, x_min_hist, y_max_hist, y_min_hist)

        # get nullclines
        self.nullclines_for_graphics()

        # graphic of heatmap, nullclines, timewaveform
        self.graphics_all(xx_mesh, yy_mesh, xx, yy, pp, qq, phxx, phyy, result_list)


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
    def calc_attraction_basin(init_x, init_y, init_P, init_Q, init_phX, init_phY,
                              N,  M, s1, s2, gamma_X, gamma_Y, Tc, Tx, Ty,
                              sT, eT,
                              tau1, b1, S, WE11, WE12, WI11, WI12,
                              tau2, b2, WE21, WE22, WI21, WI22
                              ):

        # conditions number (init_P, init_Q, init_phX, init_phY)
        total_conds =init_P.size
        num_init_vals = init_x.size

        # return
        x_max_hist = np.empty((num_init_vals, total_conds), dtype=np.int32)
        x_min_hist = np.empty((num_init_vals, total_conds), dtype=np.int32)
        y_max_hist = np.empty((num_init_vals, total_conds), dtype=np.int32)
        y_min_hist = np.empty((num_init_vals, total_conds), dtype=np.int32)

        # loop
        for idx in prange(total_conds):

            # set conditions
            P = np.full_like(init_x, init_P[idx], dtype=np.int32)
            Q = np.full_like(init_x, init_Q[idx], dtype=np.int32)
            phX = np.full_like(init_x, init_phX[idx], dtype=np.float64)
            phY = np.full_like(init_x, init_phY[idx], dtype=np.float64)

            # Calculate
            _, x_hist, y_hist = calc_time_evolution_eca(init_x, init_y, P, Q, phX, phY,
                                                        N, M, s1, s2, gamma_X, gamma_Y, Tc, Tx, Ty,
                                                        sT, eT,
                                                        tau1, b1, S, WE11, WE12, WI11, WI12,
                                                        tau2, b2, WE21, WE22, WI21, WI22)

            """ get maximum and minimum """

            # get shape
            num_vars, num_steps = x_hist.shape

            # prepare max, min
            x_max = np.full(num_vars, -np.inf)
            x_min = np.full(num_vars, np.inf)
            y_max = np.full(num_vars, -np.inf)
            y_min = np.full(num_vars, np.inf)

            # max, min (numba does not support)
            for i in range(num_vars):
                for j in range(num_steps):

                    # x
                    x_val = x_hist[i, j]
                    if x_val > x_max[i]:
                        x_max[i] = x_val

                    if x_val < x_min[i]:
                        x_min[i] = x_val

                    # y
                    y_val = y_hist[i, j]
                    if y_val > y_max[i]:
                        y_max[i] = y_val

                    if y_val < y_min[i]:
                        y_min[i] = y_val

            # store results (per xy, every conditions of P, Q, phX, phY)
            x_max_hist[:, idx] = x_max
            x_min_hist[:, idx] = x_min
            y_max_hist[:, idx] = y_max
            y_min_hist[:, idx] = y_min

        return x_max_hist, x_min_hist, y_max_hist, y_min_hist


    def analysis_phase_plain(self, x_max, x_min, y_max, y_min):

        # get init conditions
        num_init_conds, num_param_conds = x_max.shape

        # center point
        x_cen, y_cen = (x_max + x_min) / 2, (y_max + y_min) / 2
        xy = np.stack((x_cen, y_cen), axis=2)

        # 状態分類用
        param_conds = np.zeros((num_init_conds, num_param_conds), dtype=int)  # 各 param_conds の状態 (1, 2, 3)
        result_list = []  # 各 init_conds の状態 (1, 2, 3, 4)

        # インデックスを保持する変数
        self.equ_1_idx = None
        self.equ_2_idx = None
        self.po_idx = None

        # 状態を保持するための変数
        equilibrium_points = {}  # 平衡点の値を管理する辞書 {(x, y): 状態番号}

        """ param_conds の分類 """

        for init_idx in range(num_init_conds):
            for param_idx in range(num_param_conds):
                if (x_max[init_idx, param_idx] - x_min[init_idx, param_idx]) > 2:
                    # 周期軌道 (3)
                    param_conds[init_idx, param_idx] = 3

                    # 周期軌道の代表インデックスを保存
                    if self.po_idx is None:
                        self.po_idx = (init_idx, param_idx)
                else:
                    # 平衡点の場合
                    current_xy = tuple(xy[init_idx, param_idx])  # (x, y) のタプル

                    if current_xy in equilibrium_points:
                        # 既に登録済みの平衡点 -> 登録されている番号を使用
                        param_conds[init_idx, param_idx] = equilibrium_points[current_xy]
                    else:
                        # 新しい平衡点 -> 最初の平衡点は1, 以降は2
                        if len(equilibrium_points) == 0:
                            equilibrium_points[current_xy] = 1  # 最初の平衡点
                            param_conds[init_idx, param_idx] = 1

                            # 平衡点1の代表インデックスを保存
                            if self.equ_1_idx is None:
                                self.equ_1_idx = (init_idx, param_idx)
                        else:
                            equilibrium_points[current_xy] = 2  # 新しい平衡点
                            param_conds[init_idx, param_idx] = 2

                            # 平衡点2の代表インデックスを保存
                            if self.equ_2_idx is None:
                                self.equ_2_idx = (init_idx, param_idx)

        """ init_conds の分類 """

        for init_idx in range(num_init_conds):
            unique_states = np.unique(param_conds[init_idx])

            if len(unique_states) == 1:
                # 1種類の状態のみ
                if unique_states[0] == 1:
                    result_list.append(1)  # 平衡点 (1)
                elif unique_states[0] == 2:
                    result_list.append(2)  # 別の平衡点 (2)
                elif unique_states[0] == 3:
                    result_list.append(3)  # 周期軌道 (3)
            else:
                # 共存解 (4)
                result_list.append(4)

        # インデックスの確認用出力
        print("Representative indices:")
        print(f"equ_1_idx: {self.equ_1_idx}")
        print(f"equ_2_idx: {self.equ_2_idx}")
        print(f"po_idx: {self.po_idx}")

        return result_list


    def nullclines_for_graphics(self):

        # instance
        inst = Nullcline(self.params)

        # set nullclines
        self.x1_null, self.x2_null = inst.nullcline_fx_x, inst.nullcline_fx_y
        self.y1_null, self.y2_null = inst.nullcline_fy_x, inst.nullcline_fy_y


    def graphics_all(self, xx_mesh, yy_mesh, init_xx, init_yy, pp, qq, phxx, phyy, state):

        state = np.array(state)

        # instance of graphics (and graphic heatmap)
        inst = PhasePlanePlotter(xx_mesh, yy_mesh, state.reshape(xx_mesh.shape))

        inst.add_nullclines(self.x1_null*self.params["s1"], self.x2_null*self.params["s2"], color="blue")
        inst.add_nullclines(self.y1_null*self.params["s1"], self.y2_null*self.params["s2"], color="orange")

        # only an equilibrium
        if (self.equ_1_idx != None) and (self.equ_2_idx == None):

            x = np.array(init_xx[self.equ_1_idx[0]])
            y = np.array(init_yy[self.equ_1_idx[0]])

            P = np.full_like(x, pp[self.equ_1_idx[1]], dtype=np.int32)
            Q = np.full_like(x, qq[self.equ_1_idx[1]], dtype=np.int32)
            phX = np.full_like(x, phxx[self.equ_1_idx[1]], dtype=np.float64)
            phY = np.full_like(x, phyy[self.equ_1_idx[1]], dtype=np.float64)

            _, x_hist, y_hist = calc_time_evolution_eca(x, y, P, Q, phX, phY,
                                                        self.params["N"], self.params["M"], self.params["s1"], self.params["s2"], self.params["gamma_X"], self.params["gamma_Y"], self.params["Tc"], self.params["Tx"], self.params["Ty"],
                                                        self.params["sT"], self.params["eT"],
                                                        self.params["tau1"], self.params["b1"], self.params["S"], self.params["WE11"], self.params["WE12"], self.params["WI11"], self.params["WI12"],
                                                        self.params["tau2"], self.params["b2"], self.params["WE21"], self.params["WE22"], self.params["WI21"], self.params["WI22"]
                                                        )

            inst.add_result(x_hist, y_hist, c="red", l="equ")

        # two equilibria
        elif (self.equ_1_idx != None) and (self.equ_2_idx != None):

            x = np.array(init_xx[self.equ_1_idx[0]])
            y = np.array(init_yy[self.equ_1_idx[0]])

            P = np.full_like(x, pp[self.equ_1_idx[1]], dtype=np.int32)
            Q = np.full_like(x, qq[self.equ_1_idx[1]], dtype=np.int32)
            phX = np.full_like(x, phxx[self.equ_1_idx[1]], dtype=np.float64)
            phY = np.full_like(x, phyy[self.equ_1_idx[1]], dtype=np.float64)

            _, x_hist, y_hist = calc_time_evolution_eca(x, y, P, Q, phX, phY,
                                                        self.params["N"], self.params["M"], self.params["s1"], self.params["s2"], self.params["gamma_X"], self.params["gamma_Y"], self.params["Tc"], self.params["Tx"], self.params["Ty"],
                                                        self.params["sT"], self.params["eT"], 
                                                        self.params["tau1"], self.params["b1"], self.params["S"], self.params["WE11"], self.params["WE12"], self.params["WI11"], self.params["WI12"],
                                                        self.params["tau2"], self.params["b2"], self.params["WE21"], self.params["WE22"], self.params["WI21"], self.params["WI22"]
                                                        )

            inst.add_result(x_hist, y_hist, c="red", l="equ 1")

            x = np.array(init_xx[self.equ_2_idx[0]])
            y = np.array(init_yy[self.equ_2_idx[0]])

            P = np.full_like(x, pp[self.equ_2_idx[1]], dtype=np.int32)
            Q = np.full_like(x, qq[self.equ_2_idx[1]], dtype=np.int32)
            phX = np.full_like(x, phxx[self.equ_2_idx[1]], dtype=np.float64)
            phY = np.full_like(x, phyy[self.equ_2_idx[1]], dtype=np.float64)

            _, x_hist, y_hist = calc_time_evolution_eca(x, y, P, Q, phX, phY,
                                                        self.params["N"], self.params["M"], self.params["s1"], self.params["s2"], self.params["gamma_X"], self.params["gamma_Y"], self.params["Tc"], self.params["Tx"], self.params["Ty"],
                                                        self.params["sT"], self.params["eT"],
                                                        self.params["tau1"], self.params["b1"], self.params["S"], self.params["WE11"], self.params["WE12"], self.params["WI11"], self.params["WI12"],
                                                        self.params["tau2"], self.params["b2"], self.params["WE21"], self.params["WE22"], self.params["WI21"], self.params["WI22"]
                                                        )

            inst.add_result(x_hist, y_hist, c="blue", l="equ 2")

        # po
        if self.po_idx != None:

            x = np.array(init_xx[self.po_idx[0]])
            y = np.array(init_yy[self.po_idx[0]])

            P = np.full_like(x, pp[self.po_idx[1]], dtype=np.int32)
            Q = np.full_like(x, qq[self.po_idx[1]], dtype=np.int32)
            phX = np.full_like(x, phxx[self.po_idx[1]], dtype=np.float64)
            phY = np.full_like(x, phyy[self.po_idx[1]], dtype=np.float64)

            _, x_hist, y_hist = calc_time_evolution_eca(x, y, P, Q, phX, phY,
                                                        self.params["N"], self.params["M"], self.params["s1"], self.params["s2"], self.params["gamma_X"], self.params["gamma_Y"], self.params["Tc"], self.params["Tx"], self.params["Ty"],
                                                        self.params["sT"], self.params["eT"],
                                                        self.params["tau1"], self.params["b1"], self.params["S"], self.params["WE11"], self.params["WE12"], self.params["WI11"], self.params["WI12"],
                                                        self.params["tau2"], self.params["b2"], self.params["WE21"], self.params["WE22"], self.params["WI21"], self.params["WI22"]
                                                        )

            inst.add_result(x_hist, y_hist, c="gray", l="periodic orbit")

        inst.show()