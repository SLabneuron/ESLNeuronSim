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

from src.analyses.analysis_null_cline import Nullcline

from src.method.euler.ode_basic import  calc_time_evolution_ode

from src.graphics.graphic_analysis_phase_plane import PhasePlanePlotter


class ABODE:

    def __init__(self, master, filename):

        # get params
        self.params = master.params

        self.master = master

        self.filename = filename
        print(self.filename)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)


    def run(self):

        """ Condtions """

        # get params
        params = self.params

        # variables
        self.x = np.arange(0, 1.01, 0.01)
        self.y = np.arange(0, 1.01, 0.01)

        init_xx, init_yy = np.meshgrid(self.x, self.y)

        init_x = init_xx.flatten()
        init_y = init_yy.flatten()

        num_IC = init_x.size        # initial condtions

        """ parameters """

        # time
        sT, eT, h = 1500, 2000, params["h"]

        # params (fx)
        tau1, b1, S, WE11, WE12, WI11, WI12 = params['tau1'], params['b1'], params['S'], params['WE11'], params['WE12'], params['WI11'], params['WI12']

        # params (fy)
        tau2, b2, WE21, WE22, WI21, WI22 = params['tau2'], params['b2'], params['WE21'], params['WE22'], params['WI21'], params['WI22']

        """ run simulation """
        bench_sT = datetime.datetime.now()
        print("\n start: ", bench_sT)

        self.x_hist, self.y_hist = self.calc_attraction_basin(init_x, init_y,
                                                            sT, eT, h,
                                                            tau1, b1, S, WE11, WE12, WI11, WI12,
                                                            tau2, b2, WE21, WE22, WI21, WI22)

        bench_eT = datetime.datetime.now()
        print("end: ", bench_eT)

        print("bench mark: ", bench_eT - bench_sT)

        """ analysis heatmap"""

        result_list = self.analysis_phase_plain(num_IC, self.x_hist, self.y_hist)

        """ analysis nullcline for graphics """

        # get nullclines
        self.nullclines_for_graphics()

        """ Store results as a DataFrame """

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


    def calc_attraction_basin(self, init_x, init_y,
                              sT, eT, h,
                              tau1, b1, S, WE11, WE12, WI11, WI12,
                              tau2, b2, WE21, WE22, WI21, WI22,
                              ):

        # Calculate
        _, x_hist, y_hist = calc_time_evolution_ode(init_x, init_y,
                                                sT, eT, h,
                                                tau1, b1, S, WE11, WE12, WI11, WI12,
                                                tau2, b2, WE21, WE22, WI21, WI22)

        return x_hist, y_hist


    def analysis_phase_plain(self, num_IC, x_hist, y_hist):

        """ pre processing """

        # get x_max, x_min, y_max, y_min
        x_max, x_min = np.max(x_hist, axis=0), np.min(x_hist, axis=0)
        y_max, y_min = np.max(y_hist, axis=0), np.min(y_hist, axis=0)

        # round operation
        x_max, x_min = np.round(x_max, 3), np.round(x_min, 3)
        y_max, y_min = np.round(y_max, 3), np.round(y_min, 3)

        # get center point of x, y assuming equilibrium
        x_cen, y_cen = (x_max + x_min)/2, (y_max + y_min)/2

        # get (x, y) including po (periodic orbit)
        xy = np.column_stack((x_cen, y_cen))

        """ start classified """

        equ_1_idx = np.array([])
        equ_2_idx = np.array([])
        po_idx = np.array([])

        # judge equ or po (sufficient x only)
        condition_po = x_max - x_min > 0.005
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

        inst.add_nullclines(self.x1_null, self.x2_null, color="blue")
        inst.add_nullclines(self.y1_null, self.y2_null, color="orange")

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