# -*- coding: utf-8 -*-

"""
Title: Return map

@author: shirafujilab

Created: 2024-12-23

Contents:

"""

# import standard library
import os
import tkinter as tk
from tkinter import ttk

import numpy as np
from numba import njit

import datetime


# import my library
from src.method.eca.eca_basic_step import calc_time_evolution_eca
from src.graphics.graphic_return_map import GraphicReMap


class EcaReMap:

    def __init__(self, master, filename):

        # get params
        self.params = master.params

        self.master = master

        self.filename = filename
        print(self.filename)

        #os.makedirs(os.path.dirname(self.filename), exist_ok=True)

        self.make_entry_field()


    def make_entry_field(self):

        e_field = tk.Toplevel(self.master.root)
        e_field.title("Entry Field")
        e_field.geometry("300x200")

        entries = {}

        title1 = ttk.Label(e_field, text="Range")
        title1.grid(row=0, column=0, columnspan=2)

        t1 = ttk.Label(e_field, text="l_x: ")
        t1.grid(row=1, column=0)
        e1 = ttk.Entry(e_field)
        e1.grid(row=1, column=1)
        entries["e1"] = e1

        t2 = ttk.Label(e_field, text="r_x: ")
        t2.grid(row=1, column=2)
        e2 = ttk.Entry(e_field)
        e2.grid(row=1, column=3)
        entries["e2"] = e2

        t3 = ttk.Label(e_field, text="l_y: ")
        t3.grid(row=2, column=0)
        e3 = ttk.Entry(e_field)
        e3.grid(row=2, column=1)
        entries["e3"] = e3

        t4 = ttk.Label(e_field, text="r_y: ")
        t4.grid(row=2, column=2)
        e4 = ttk.Entry(e_field)
        e4.grid(row=2, column=3)
        entries["e4"] = e4

        title2 = ttk.Label(e_field, text="ReturnMap")
        title2.grid(row=3, column=0, columnspan=2)

        b1 = ttk.Button(e_field, text="1-step", command=lambda: self.run1(entries))
        b1.grid(row=4, column=0, columnspan=2)

        b2 = ttk.Button(e_field, text="1-cycle", command=lambda: self.run2(entries))
        b2.grid(row=4, column=2, columnspan=2)


    def run1(self, entries):
        
        # parameters
        params  = self.params
        
        # ca params
        N, M, s1, s2, gamma_X, gamma_Y, Tc, Tx, Ty = params["N"], params["M"], params["s1"], params["s2"], params["gamma_X"], params["gamma_Y"], params["Tc"], params["Tx"], params["Ty"]
        tau1, b1, S, WE11, WE12, WI11, WI12 = params['tau1'], params['b1'], params['S'], params['WE11'], params['WE12'], params['WI11'], params['WI12']
        tau2, b2, WE21, WE22, WI21, WI22 = params['tau2'], params['b2'], params['WE21'], params['WE22'], params['WI21'], params['WI22']

        # get subset (return map)
        sub_x = np.arange(int(entries["e1"].get()), int(entries["e2"].get())+1, 1)
        sub_y = np.arange(int(entries["e3"].get()), int(entries["e4"].get())+1, 1)

        xx, yy = np.meshgrid(sub_x, sub_y)
        xx, yy = xx.flatten(),  yy.flatten()

        p, q = np.array([63], np.int32), np.array([63], np.int32)
        phx, phy = np.array([1.0], np.float64), np.array([1.0], np.float64)

        bench_sT = datetime.datetime.now()
        print("\n start: ", bench_sT)

        # Calculate
        x_hist, y_hist = calc_time_evolution_eca(xx, yy, p, q, phx, phy,
                                                    N, M, s1, s2, gamma_X, gamma_Y, Tc, Tx, Ty,
                                                    tau1, b1, S, WE11, WE12, WI11, WI12,
                                                    tau2, b2, WE21, WE22, WI21, WI22)

        bench_eT = datetime.datetime.now()

        print("end: ", bench_eT)
        print("bench mark: ", bench_eT - bench_sT)
        
        print()

        inst = GraphicReMap()
        inst.plot(yy, xx, y_hist, x_hist)



    def run2(self, entries):

        # get subset (return map)
        sub_x = np.arange(int(entries["e1"].get()), int(entries["e2"].get())+1, 1)
        sub_y = np.arange(int(entries["e3"].get()), int(entries["e4"].get())+1, 1)

        xx, yy = np.meshgrid(sub_x, sub_y)

        p = np.array([0, 2, 4, 8, 16, 32], dtype=np.int32)
        q = np.array([0, 2, 4, 8, 16, 32], dtype=np.int32)
        phx = np.arange(0, 1, 0.02, dtype=np.float64)
        phy = np.arange(0, 1, 0.02, dtype=np.float64)

        pp, qq = np.meshgrid(p, q)
        pp, qq = pp.flatten(), qq.flatten()
        aux_itr = pp.shape

        phxx, phyy = np.meshgrid(phx, phy)
        phxx, phyy = phxx.flatten(), phyy.flatten()
        pha_itr = phxx.shape



"""
    @staticmethod
    @njit(parallel=True)
    def next_steps(init_x, init_y, init_p, init_q, init_phx, init_phy,
                   N,  M, s1, s2, gamma_X, gamma_Y, Tc, Tx, Ty,
                   sT, eT,
                   tau1, b1, S, WE11, WE12, WI11, WI12,
                   tau2, b2, WE21, WE22, WI21, WI22):
"""




