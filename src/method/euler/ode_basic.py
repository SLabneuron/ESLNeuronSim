# -*- coding: utf-8 -*-
"""
Created on: 2026-02-25

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
import matplotlib.pyplot as plt
import os
import datetime, time

class TimeEvolOdeSingle:

    def __init__(self, params, filename):

        # get params, filename
        self.params = params
        self.filename = filename

        # Ensure output directory exists
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)

        # Confirm: output filename
        print(filename)

    def run(self):

        params = self.params
        
        """ variables """
        init_x = np.float32(params["init_x"])
        init_y = np.float32(params["init_y"])
        init_z = np.float32(params["init_z"])

        """ sim config """

        # time
        sT, eT, h = params["sT"], params["eT"], np.float32(params["h"])

        # store step
        total_step = int(eT/h)+1
        index_start = int(sT/h)
        store_step = (total_step - index_start) // 100 + 1 if total_step > index_start else 0

        """ params """

        # parameters
        a, b, c, d, r, s = np.float32(params['a']), np.float32(params['b']), np.float32(params['c']), np.float32(params['d']), np.float32(params['r']), np.float32(params['s'])
        I_ext = np.float32(params["I_ext"])

        # x_1
        p = (d - b) / a
        q = c / a

        coef = [1, p, 0, -q]   # x^3 + p x^2 - q = 0
        x_1 = np.roots(coef)[0]


        """ run simulation """
        bench_sT = datetime.datetime.now()
        t0 = time.perf_counter()
        print("\n start: ", bench_sT)

        # set calode
        t_hist, x_hist = calc_time_evolution_ode(init_x, init_y, init_z, h,
                                                 a, b, c, d, r, s, x_1, I_ext,
                                                 total_step, index_start, store_step)

        bench_eT = datetime.datetime.now()
        t1 = time.perf_counter()
        print("end: ", bench_eT)
        print("bench mark: ", t1 - t0)

        # Store results
        plot_time_series(t_hist, I_hist, x_hist, y_hist, z_hist)


@njit
def calc_time_evolution_ode(init_x, init_y, init_z, h,
                            a, b, c, d, r, s, x_1, I,
                            total_step, index_start, store_step):

    # variables
    x_next = x_previous = init_x
    y_next = y_previous = init_y
    z_next = z_previous = init_z

    # time
    T = 0

    # store return arrays
    t_hist = np.zeros(store_step, dtype=np.float32)
    I_hist = np.zeros(store_step, dtype=np.float32)
    x_hist = np.zeros(store_step, dtype=np.float32)
    y_hist = np.zeros(store_step, dtype=np.float32)
    z_hist = np.zeros(store_step, dtype=np.float32)

    idx = 0

    for i in range(total_step):

        # calculate
        x_next = x_previous + h * (y_previous - a* x_previous**3 + b* x_previous**2 - z_previous + I[i])
        y_next = y_previous + h * (c - d*x_previous**2 - y_previous)
        z_next = z_previous + h * r*(s*(x_previous - x_1) - z_previous)

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
                I_hist[idx_insert] = I[i]
                x_hist[idx_insert] = x_previous
                y_hist[idx_insert] = y_previous
                z_hist[idx_insert] = z_previous

            idx += 1

    return t_hist, I_hist, x_hist, y_hist, z_hist


""" test """

def plot_time_series(t_hist, I_hist, x_hist, y_hist, z_hist):

    fig, ax = plt.subplots(4, 1, figsize=(10, 7), sharex=True)

    ax[0].plot(t_hist, I_hist, lw=0.8)
    ax[0].set_ylabel("Input")

    ax[1].plot(t_hist, x_hist, lw=0.8)
    ax[1].set_ylabel("x")

    ax[2].plot(t_hist, y_hist, lw=0.8)
    ax[2].set_ylabel("y")

    ax[3].plot(t_hist, z_hist, lw=0.8)
    ax[3].set_ylabel("z")
    ax[3].set_xlabel("time")

    plt.tight_layout()
    plt.show()


def plot_phase(x_hist, y_hist, z_hist):

    fig = plt.figure(figsize=(6,5))
    ax = fig.add_subplot(projection="3d")

    ax.plot(x_hist, y_hist, z_hist, lw=0.6)

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")

    plt.tight_layout()
    plt.show()



if __name__ == "__main__":

    # variables
    x = np.float32(-1)
    y = np.float32(0)
    z = np.float32(0)

    # parameters
    a = 1
    b = 3
    c = 1
    d = 5

    r = 0.001
    s = 4

    # x_1
    p = (d - b) / a
    q = c / a

    coef = [1, p, 0, -q]
    x_1 = np.roots(coef)[0]

    # time
    h = 0.001
    sT = 000
    eT = 10000

    total_step = int(eT/h)+1
    index_start = int(sT/h)
    store_step = (total_step - index_start) // 100 + 1 if total_step > index_start else 0

    # Input
    #I = np.zeros(total_step)
    #I[200000:220000] = -3
    #I[220000:250000] = 4

    #I = np.full(total_step, 0.4)    # single bursting and resting state
    I = np.full(total_step, 2)      # periodic bursting
    #I = np.full(total_step, 4)      # high-frequency tonic spiking


    t_hist, I_hist, x_hist, y_hist, z_hist = calc_time_evolution_ode(x, y, z, h,
                                                             a, b, c, d, r, s, x_1, I,
                                                             total_step, index_start, store_step)


    print(t_hist, x_hist)

    # graphic
    plot_time_series(t_hist, I_hist, x_hist, y_hist, z_hist)
    # plot_phase(x_hist, y_hist, z_hist)
