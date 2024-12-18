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

from src.graphics.graphic_analysis_phase_plane import PhasePlanePlotter


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

        """

        Calculate Attraction Basins

        for state variables

            xx, yy: divided into 4 or 8 (ex. 32*32, 32*32, 32*32, 32*32): 1024 per 1 cell

            for conditions

                pp, qq, phX, phY: 625 per 1 cell

        """

        """ conditions """

        # get params
        params = self.params

        # variables
        self.x = np.arange(0, self.params["N"], 2)
        self.y = np.arange(0, self.params["N"], 2)
        self.p = np.array([0, 2, 4, 8, 16, 32], dtype=np.int32)         # 0, 2, 4, 8, 16, 32
        self.q = np.array([0, 2, 4, 8, 16, 32], dtype=np.int32)
        self.phX = np.arange(0, 1.0, 0.2, dtype=np.float64)             # 0, 0.2, 0.4, 0.6, 0.8
        self.phY = np.arange(0, 1.0, 0.2, dtype=np.float64)

        # reshape array
        x_divided = self.x.reshape(2, -1)                               # [[*,*,*], [*,*,*]]
        y_divided = self.y.reshape(2, -1)

        pp, qq, phxx, phyy = np.meshgrid(self.p, self.q, self.phX, self.phY)
        pp, qq = pp.flatten(), qq.flatten()
        phxx, phyy = phxx.flatten(), phyy.flatten()

        # the number of init state variables
        val_init_conds= self.x.size * self.y.size                       # initial condtions
        aux_init_conds = self.p.size * self.q.size
        pha_init_conds = self.phX.size * self.phY.size

        # summarized conditions P, Q, phX, phY
        total_conds = pha_init_conds * aux_init_conds

        """ parameters """

        # time
        sT, eT = 300, 400

        # params (fx)
        tau1, b1, S, WE11, WE12, WI11, WI12 = params['tau1'], params['b1'], params['S'], params['WE11'], params['WE12'], params['WI11'], params['WI12']

        # params (fy)
        tau2, b2, WE21, WE22, WI21, WI22 = params['tau2'], params['b2'], params['WE21'], params['WE22'], params['WI21'], params['WI22']

        # CA params
        N, M, s1, s2, gamma_X, gamma_Y, Tc, Tx, Ty = params["N"], params["M"], params["s1"], params["s2"], params["gamma_X"], params["gamma_Y"], params["Tc"], params["Tx"], params["Ty"]

        # store_step
        total_step = int(eT/Tc)+1
        index_start = int(sT/Tc)
        store_step = (total_step - index_start) // 100 + 1 if total_step > index_start else 0

        # results
        self.x_hist = np.zeros((total_conds, store_step, val_init_conds))
        self.y_hist = np.zeros((total_conds, store_step, val_init_conds))


        """ run simulation """
        bench_sT = datetime.datetime.now()
        print("\n start: ", bench_sT)
        print("proccess: -*-*-*-*- ", 0, "% -*-*-*-*- ")

        for iter_x, xx in enumerate(x_divided):
            for iter_y, yy in enumerate(y_divided):

                init_xx, init_yy = np.meshgrid(xx, yy)
                init_xx, init_yy = init_xx.flatten(), init_yy.flatten()

                x_hist, y_hist = self.calc_attraction_basin(init_xx, init_yy, pp, qq, phxx, phyy,
                                                            N,  M, s1, s2, gamma_X, gamma_Y, Tc, Tx, Ty,
                                                            sT, eT,
                                                            tau1, b1, S, WE11, WE12, WI11, WI12,
                                                            tau2, b2, WE21, WE22, WI21, WI22)

                s_iter = (iter_x + iter_y) * len(init_xx)
                e_iter = (iter_x + iter_y + 1) * len(init_xx)

                self.x_hist[:, :, s_iter:e_iter] = x_hist
                self.y_hist[:, :, s_iter:e_iter] = y_hist

                print("proccess: -*-*-*-*- ", round((iter_x*len(y_divided) + iter_y + 1)/(len(x_divided) + len(y_divided))*100,  2), "% -*-*-*-*- ")

        bench_eT = datetime.datetime.now()
        print("end: ", bench_eT)

        print("bench mark: ", bench_eT - bench_sT)

        """ analysis heatmap"""

        result_list = self.analysis_phase_plain_new(val_init_conds, self.x_hist, self.y_hist)

        print("get result_list")

        """ analysis nullcline for graphics """

        # get nullclines
        self.nullclines_for_graphics()
        
        print("set nullcline")


        """ Store results as a DataFrame """

        init_x, init_y = np.meshgrid(self.x, self.y)
        init_x, init_y = init_x.flatten(), init_y.flatten()

        # make df
        df = pd.DataFrame({
            "init_x": init_x,
            "init_y": init_y,
            "state": result_list
        })

        # specify column order
        df = df[["init_x", "init_y",  "state"]]

        # Save to CSV
        try:
            df.to_csv(self.filename, index=False)
            print(f"Results saved to {self.filename}")
        except Exception as e:
            print(f"Error saving results to {self.filename}: {e}")


        """ graphics """

        # heatmap, nullclines, timewaveform
        self.graphics_all(init_xx, init_yy, result_list)


    @staticmethod
    @njit(parallel=True)
    def calc_attraction_basin(init_x, init_y, init_P, init_Q, init_phX, init_phY,
                              N,  M, s1, s2, gamma_X, gamma_Y, Tc, Tx, Ty,
                              sT, eT,
                              tau1, b1, S, WE11, WE12, WI11, WI12,
                              tau2, b2, WE21, WE22, WI21, WI22
                              ):

        # conditions number (init_P, init_Q, init_phX, init_phY)
        total_iters =init_P.size
        num_init_conds = init_x.size

        # store_step
        total_step = int(eT/Tc)+1
        index_start = int(sT/Tc)
        store_step = (total_step - index_start) // 100 + 1 if total_step > index_start else 0

        # return
        x_list = np.empty((total_iters, store_step, num_init_conds), dtype=np.int32)
        y_list = np.empty((total_iters, store_step, num_init_conds), dtype=np.int32)

        # loop
        for idx in prange(total_iters):

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

            x_list[idx, :, :] = x_hist
            y_list[idx, :, :] = y_hist

        return x_list, y_list


    def analysis_phase_plain_new(self, num_IC, x_hist, y_hist):

        """ pre processing """
        # x_hist, y_hist: shape (num_IC, time_steps, xy_val)

        # get x_max, x_min, y_max, y_min by taking max/min along time axis
        x_max, x_min = np.max(x_hist, axis=1), np.min(x_hist, axis=1)
        y_max, y_min = np.max(y_hist, axis=1), np.min(y_hist, axis=1)

        # center point
        x_cen, y_cen = (x_max + x_min)/2, (y_max + y_min)/2

        # (x,y)の中心値を格納
        # x_cen, y_cenはshape (num_IC, xy_val)を想定、もしxy_val=1ならflattenしてもOK
        # 以下はxy_val=1の場合を想定
        x_cen = x_cen.ravel()
        y_cen = y_cen.ravel()

        xy = np.column_stack((x_cen, y_cen))

        """ start classified """

        # judge equ or po 
        # 2D版に合わせて閾値を0.005に戻します
        condition_po = (x_max.ravel() - x_min.ravel()) > 0.005
        po_idx = np.where(condition_po)[0]

        if len(po_idx) == num_IC:
            # 全てが周期軌道
            eq_idx = np.array([])
        else:
            eq_idx = np.where(~condition_po)[0]

            # メインとなる平衡点のインデックス
            pri_eq_idx = np.min(eq_idx)

            # pri_eq_idx番目のxyと等しいものをequ_1とする
            # xy[eq_idx]は (len(eq_idx), 2)の2次元配列、xy[pri_eq_idx]は(2,)の1次元配列
            # 同一判定は全成分が一致するものを抽出
            equ_1_mask = np.all(xy[eq_idx] == xy[pri_eq_idx], axis=1)
            equ_1_idx = eq_idx[equ_1_mask]

            # equ_1でないeq_idxをequ_2_idxとする
            equ_2_idx = eq_idx[~equ_1_mask]

        """ classified state """
        result_list = []

        self.equ_1_idx = None
        self.equ_2_idx = None
        self.po_idx = None

        for idx in range(num_IC):

            # 1. converging to equ_1
            if idx in equ_1_idx:
                state = 1
                if self.equ_1_idx is None:
                    self.equ_1_idx = idx

            # 2. converging to equ_2
            elif idx in equ_2_idx:
                state = 2
                if self.equ_2_idx is None:
                    self.equ_2_idx = idx

            # 3. periodic orbit
            elif idx in po_idx:
                state = 3
                if self.po_idx is None:
                    self.po_idx = idx

            # 4. others
            else:
                state = 4

            result_list.append(state)

        return result_list




    def analysis_phase_plain(self, num_IC, x_hist, y_hist):

        """ pre processing """

        # get x_max, x_min, y_max, y_min
        x_max, x_min = np.max(x_hist, axis=1), np.min(x_hist, axis=1)
        y_max, y_min = np.max(y_hist, axis=1), np.min(y_hist, axis=1)

        # get center point of x, y assuming equilibrium
        x_cen, y_cen = (x_max + x_min)/2, (y_max + y_min)/2

        # get (x, y) including po (periodic orbit)
        xy = np.column_stack((x_cen, y_cen))
        
        print("end prepro")

        """ start classified """

        equ_1_idx = np.array([])
        equ_2_idx = np.array([])
        po_idx = np.array([])

        # judge equ or po (sufficient x only)
        condition_po = x_max - x_min > 2
        po_idx = np.where(condition_po)[0]

        # If thee condition converging to a  periodic orbit is the same size as the total conditions
        if len(po_idx) == num_IC:
            eq_idx = np.array([])
        else:

            # judge equilibrium set
            eq_idx = np.where(~condition_po)[0]

            # get first (primary) equilibrium's index
            pri_eq_idx =np.min(eq_idx)

            equ_1_idx = np.where(xy[pri_eq_idx] == xy[eq_idx])[0]
            equ_2_idx = eq_idx[~np.isin(eq_idx, equ_1_idx)]     # from eq_idx removing equ_1_idx

        print("before classified")


        """ classified state """

        result_list = []

        self.equ_1_idx = None
        self.equ_2_idx = None
        self.po_idx = None

        for idx in range(num_IC):

            # 1. converging to equ_1
            if idx in equ_1_idx:
                state = 1
                if self.equ_1_idx == None: self.equ_1_idx = idx

            # 2. converging to equ_2
            elif idx in equ_2_idx:
                state = 2
                if self.equ_2_idx == None: self.equ_2_idx = idx

            # 3. periodic orbit
            elif idx in po_idx:
                state = 3
                if self.po_idx == None: self.po_idx = idx

            # 4. others
            else: state = 4

            result_list.append(state)

        return result_list


    def nullclines_for_graphics(self):

        # instance
        inst = Nullcline(self.params)

        # set nullclines
        self.x1_null, self.x2_null = inst.nullcline_fx_x, inst.nullcline_fx_y
        self.y1_null, self.y2_null = inst.nullcline_fy_x, inst.nullcline_fy_y


    def graphics_all(self, init_xx, init_yy, state):

        state = np.array(state)

        # instance of graphics (and graphic heatmap)
        inst = PhasePlanePlotter(init_xx, init_yy, state.reshape(init_xx.shape))

        inst.add_nullclines(self.x2_null, self.x1_null, color="blue")
        inst.add_nullclines(self.y2_null, self.y1_null, color="orange")

        # only an equilibrium
        if (self.equ_1_idx != None) and (self.equ_2_idx == None):
            inst.add_result(self.x_hist.T[self.equ_1_idx], self.y_hist.T[self.equ_1_idx], c="red", l="equ")

        # two equilibria
        elif (self.equ_1_idx != None) and (self.equ_2_idx != None):
            inst.add_result(self.x_hist.T[self.equ_1_idx], self.y_hist.T[self.equ_1_idx], c="red", l="equ 1")
            inst.add_result(self.x_hist.T[self.equ_2_idx], self.y_hist.T[self.equ_2_idx], c="blue", l="equ 2")

        # po
        if self.po_idx != None:
            inst.add_result(self.x_hist.T[self.po_idx], self.y_hist.T[self.po_idx], c="gray", l="periodic orbit")

        inst.show()