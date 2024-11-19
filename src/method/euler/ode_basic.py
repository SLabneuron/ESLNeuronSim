# -*- coding: utf-8 -*-
"""
Created on: 2024-10-22
Updated on: 2024-11-12

@author: shirafujilab

Contents: 

"""

# import my library
import numpy as np
from numba import njit


class CalODE:

    def __init__(self, params):

        # get params
        self.params = params

        # state variables
        self.init_x = np.atleast_1d(params["init_x"])
        self.init_y = np.atleast_1d(params["init_y"])

        # registers
        self.t_hist = None
        self.x_hist = None
        self.y_hist = None


    def run(self):

        # time
        sT = self.params["sT"]
        eT = self.params["eT"]
        h = self.params["h"]

        # params (fx)
        tau1 = self.params['tau1']
        b1 = self.params['b1']
        S = self.params['S']
        WE11 = self.params['WE11']
        WE12 = self.params['WE12']
        WI11 = self.params['WI11']
        WI12 = self.params['WI12']

        # params (fy)
        tau2 = self.params['tau2']
        b2 = self.params['b2']
        WE21 = self.params['WE21']
        WE22 = self.params['WE22']
        WI21 = self.params['WI21']
        WI22 = self.params['WI22']

        self.t_hist, self.x_hist, self.y_hist = self.run_simulation(self.init_x, self.init_y,
                                                                    sT, eT, h,
                                                                    tau1, b1, S, WE11, WE12, WI11, WI12,
                                                                    tau2, b2, WE21, WE22, WI21, WI22)


    @staticmethod
    @njit
    def run_simulation(init_x, init_y,
                        sT, eT, h,
                        tau1, b1, S, WE11, WE12, WI11, WI12,
                        tau2, b2, WE21, WE22, WI21, WI22):

        # Variables
        x_next = x_previous = init_x
        y_next = y_previous = init_y

        # Time
        T = 0

        # Calculate total step for storing
        total_step = int(eT/h)+1
        index_start = int(sT/h)
        store_step = total_step - index_start if total_step > index_start else 0

        # Get size of x, y
        n = init_x.size if init_x.ndim >0 else 1

        # store return arrays
        t_hist = np.zeros(store_step)
        x_hist = np.zeros((store_step, n))
        y_hist = np.zeros((store_step, n))

        idx = 0

        for i in range(total_step):

            # calculate fx fy
            fx = (1 / tau1) * ((b1 * S + WE11 * x_previous**2 + WE12 * y_previous**2) * (1 - x_previous) - (1 + WI11 * x_previous**2 + WI12 * y_previous**2) * x_previous)
            fy = (1 / tau2) * ((b2 * S + WE21 * x_previous**2 + WE22 * y_previous**2) * (1 - y_previous) - (1 + WI21 * x_previous**2 + WI22 * y_previous**2) * y_previous)

            # calculate
            x_next = x_previous + h * fx
            y_next = y_previous + h * fy

            # update variables and time
            x_previous = x_next
            y_previous = y_next
            T += h

            # store registers
            if i >= index_start:

                t_hist[idx] = T
                x_hist[idx, :] = x_previous
                y_hist[idx, :] = y_previous
                idx += 1

        return t_hist, x_hist, y_hist


