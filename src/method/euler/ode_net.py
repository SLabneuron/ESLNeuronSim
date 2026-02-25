# -*- coding: utf-8 -*-
"""
Created on: 2026-02-25

@author: shirafujilab

Contents:

    HR neuron network

Return:

    t_hist
    x_hist

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
        init_x = np.array([-2, -1.8, -1.6, -1.4, -1.2, -1.0, -0.8, -0.6, -0.4], dtype=np.float32)
        init_y = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.float32)
        init_z = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.float32)

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

        # coupling parameters
        V_s = np.float32(params["V_s"])         # default value (2)
        Theta = np.float32(params["Theta"])   # default value (-0.25)
        g_s = np.float32(params["g_s"])         # 0.429
        gamma = np.float32(params["gamma"])


        c_ij = np.array([[1, 1, 1, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 1, 1, 1, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 1, 1, 1],
                        [1, 0, 0, 1, 0, 0, 1, 0, 0],
                        [0, 1, 0, 0, 1, 0, 0, 1, 0],
                        [0, 0, 1, 0, 0, 1, 0, 0, 1],
                        [0, 0, 1, 0, 0, 1, 0, 0, 1],
                        [0, 1, 0, 0, 1, 0, 0, 1, 0],
                        [1, 0, 0, 1, 0, 0, 1, 0, 0]], dtype=np.float32)

        n = c_ij.shape[0]
        k = np.sum(c_ij[0])

        """ run simulation """
        bench_sT = datetime.datetime.now()
        t0 = time.perf_counter()
        print("\n start: ", bench_sT)

        # set calode
        t_hist, x_hist = calc_time_evolution_ode(x, y, z, h,
                                                 a, b, c, d, r, s, x_1, I_ext,
                                                 V_s, Theta, g_s,  gamma, c_ij,
                                                 n, k,
                                                 total_step, index_start, store_step)

        bench_eT = datetime.datetime.now()
        t1 = time.perf_counter()
        print("end: ", bench_eT)
        print("bench mark: ", t1 - t0)

        # Store results
        plot_time_series(t_hist, x_hist)




@njit
def calc_time_evolution_ode(init_x, init_y, init_z, h,
                            a, b, c, d, r, s, x_1, I_ext,
                            V_s, Theta, g_s,  gamma, c_ij,
                            n, k,
                            total_step, index_start, store_step):

    # variables
    x_next = x_previous = init_x
    y_next = y_previous = init_y
    z_next = z_previous = init_z

    # time
    T = 0

    # store return arrays
    t_hist = np.zeros(store_step-1, dtype=np.float32)
    x_hist = np.zeros((n, store_step-1), dtype=np.float32)
    I = np.zeros((n), dtype=np.float32)


    idx = 0

    for i in range(total_step):

        # calculate sysnapse input
        Gamma = 1.0 / (1.0 + np.exp(-gamma * (x_previous - Theta)))
        Gamma = Gamma.astype(np.float32)
        syn = c_ij @ Gamma      # shape (n,)
        I = - g_s * (x_previous - V_s) * syn

        # calculate
        x_next = x_previous + h * (y_previous - a* x_previous**3 + b* x_previous**2 - z_previous + I_ext + I)
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
                x_hist[:, idx_insert] = x_previous

            idx += 1

    return t_hist, x_hist


""" test """

def plot_time_series(t_hist, x_hist):

    n  = x_hist.shape[0]

    fig, ax = plt.subplots(figsize=(10, 7))

    for idx in range(n):
        ax.plot(t_hist, x_hist[idx], lw=0.8)

    ax.set_ylabel("x")
    ax.set_xlabel("time")

    plt.tight_layout()
    plt.show()





if __name__ == "__main__":

    # variables
    x = np.array([-2, -1.8, -1.6, -1.4, -1.2, -1.0, -0.8, -0.6, -0.4], dtype=np.float32)
    y = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.float32)
    z = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.float32)

    # parameters
    a = np.float32(1)
    b = np.float32(3)
    c = np.float32(1)
    d = np.float32(5)

    r = np.float32(0.001)
    s = np.float32(4)

    # x_1
    p = (d - b) / a
    q = c / a

    coef = [1, p, 0, -q]
    x_1 = np.float32(np.roots(coef)[0])

    print(x_1)

    I_ext = np.float32(2)

    # coupling parameters
    V_s = np.float32(2)         # default value (2)
    Theta = np.float32(-0.25)   # default value (-0.25)
    g_s = np.float32(0.4)         # 0.429
    gamma = np.float32(10)

    c_ij = np.array([[1, 1, 1, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 1, 1, 1, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 1, 1, 1],
                    [1, 0, 0, 1, 0, 0, 1, 0, 0],
                    [0, 1, 0, 0, 1, 0, 0, 1, 0],
                    [0, 0, 1, 0, 0, 1, 0, 0, 1],
                    [0, 0, 1, 0, 0, 1, 0, 0, 1],
                    [0, 1, 0, 0, 1, 0, 0, 1, 0],
                    [1, 0, 0, 1, 0, 0, 1, 0, 0]], dtype=np.float32)

    n = c_ij.shape[0]
    k = np.sum(c_ij[0])

    print(n, k)

    # time
    h = np.float32(0.001)
    sT = 000
    eT = 10000

    total_step = int(eT/h)+1
    index_start = int(sT/h)
    store_step = (total_step - index_start) // 100 + 1 if total_step > index_start else 0


    t_hist, x_hist = calc_time_evolution_ode(x, y, z, h,
                                             a, b, c, d, r, s, x_1, I_ext,
                                             V_s, Theta, g_s,  gamma, c_ij,
                                             n, k,
                                             total_step, index_start, store_step)


    print(t_hist, x_hist)

    # graphic
    plot_time_series(t_hist, x_hist)
