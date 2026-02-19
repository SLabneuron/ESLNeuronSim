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
def calc_time_evolution_ode(init_x, init_y, init_z, h,
                            a, b, c, d, r, s, X_R, Input,
                        total_step, index_start, store_step):

    # variables
    x_next = x_previous = init_x
    y_next = y_previous = init_y
    z_next = z_previous = init_z

    # time
    T = 0

    # store return arrays
    t_hist = np.zeros(store_step, dtype=np.float32)
    x_hist = np.zeros(store_step, dtype=np.float32)
    y_hist = np.zeros(store_step, dtype=np.float32)
    z_hist = np.zeros(store_step, dtype=np.float32)

    idx = 0

    for i in range(total_step):

        # calculate
        x_next = x_previous + h * (y_previous - a* x_previous**3 + b* x_previous**2 - z_previous + Input)
        y_next = y_previous + h * (c - d*x_previous**2 - y_previous)
        z_next = z_previous + h * (s*(x_previous - X_R) - z_previous)

        # update variables and time
        x_previous = x_next
        y_previous = y_next
        z_previous = z_next
        T += h

        # store registers
        if i >= index_start:

            if (idx % 100) == 0:

                idx_insert = int(idx/100)

                t_hist[idx_insert] = T
                x_hist[idx_insert] = x_previous
                y_hist[idx_insert] = y_previous
                z_hist[idx_insert] = z_previous

            idx += 1

    return t_hist, x_hist, y_hist, z_hist


