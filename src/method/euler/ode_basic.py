# -*- coding: utf-8 -*-
"""
Created on: 2024-10-22
Updated on: 2024-11-12

@author: shirafujilab

Contents: 


Return:

    t_hist
    x_hist
    y_hist

"""

# import my library
import numpy as np
from numba import njit



@njit
def calc_time_evolution_ode(init_x, init_y,
                        sT, eT, h,
                        tau1, b1, S, WE11, WE12, WI11, WI12,
                        tau2, b2, WE21, WE22, WI21, WI22):

    # variables
    x_next = x_previous = init_x
    y_next = y_previous = init_y

    # time
    T = 0

    # Calculate total step for storing
    total_step = int(eT/h)+1
    index_start = int(sT/h)
    store_step = (total_step - index_start) // 20 + 1 if total_step > index_start else 0

    # Get size of x, y
    n = init_x.size if init_x.ndim >0 else 1

    # store return arrays
    t_hist = np.zeros(store_step, dtype=np.float32)
    x_hist = np.zeros((store_step, n), dtype=np.float32)
    y_hist = np.zeros((store_step, n), dtype=np.float32)

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

            if (idx % 20) == 0:

                idx_insert = int(idx/20)

                t_hist[idx_insert] = T
                x_hist[idx_insert, :] = x_previous
                y_hist[idx_insert, :] = y_previous
            idx += 1

    return t_hist, x_hist, y_hist


