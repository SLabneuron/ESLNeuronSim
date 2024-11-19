# -*- coding: utf-8 -*-
"""
Created on: 2024-10-22
Updated on: 2024-11-12

@author: shirafujilab

Contents: bifurcation for S

"""

# import standard library
import numpy as np

import datetime

# import my library
from src.method.euler.ode_basic import  CalODE


class BifODE:

    def __init__(self, params):

        # get params
        self.params = params

        self.make_xx_yy()


    def make_xx_yy(self):

        x = np.arange(0, 1.01, 0.01)
        y = np.arange(0, 1.01, 0.01)

        xx, yy = np.meshgrid(x, y)

        xx = xx.flatten()
        yy = yy.flatten()

        self.params["init_x"] = xx
        self.params["init_y"] = yy

        self.num_initial_conditions = xx.size


    def run(self):

        bif_S = np.arange(0, 0.81, 0.1)
        num_S = len(bif_S)
        num_IC = self.num_initial_conditions

        self.S_value = bif_S
        self.max_values = np.zeros((num_S, num_IC))
        self.min_values = np.zeros((num_S, num_IC))
        
        print("start: ", datetime.datetime.now())

        for idx, S in enumerate(bif_S):

            self.params["S"] = S

            inst = CalODE(self.params)
            inst.run()

            x_hist = inst.x_hist            # shape (num_time_steps, num_IC)

            x_max = np.max(x_hist, axis=0)  # shape (num_IC, )
            x_min = np.min(x_hist, axis=0)

            self.max_values[idx, :] = x_max
            self.min_values[idx, :] = x_min

        self.init_x_values = self.params["init_x"]
        
        print("end: ", datetime.datetime.now())