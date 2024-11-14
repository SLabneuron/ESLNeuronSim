# -*- coding: utf-8 -*-

"""
Title: frame_settings > controller setting

@author: shirafujilab

Created: 2024-11-14

Contents:

    Neumerical Integration (ni)
        - forward euler method (fem),
        - rouge kutta 4-th order (rk4),
        - scipy ode45 solver (ode45)


    Cellular Automaton (CA)
        - ergodic cellular automaton (eca)
        - regular cellular automaton (rca)


Return:

    - master.toggle_widgets (dict)

        fr_ni, fr_ca


"""

# import standard library
import tkinter as tk
from tkinter import ttk


class FrInit:

    def  __init__(self, master, fr):

        # get master
        self.master = master

        # set up
        self.set_init_window(fr)

        # grid
        self.master.toggle_widgets["fr_ca"].grid()


    def set_init_window(self, row_fr):

        # Title
        title = ttk.Label(row_fr, text="Init variables, and time step h (ni only)")
        title.grid(row=3, column=0, padx=2,  pady=2, sticky="nsew")

        """ for neumerical integration """

        # master frame
        fr_ni = ttk.Frame(row_fr, style="Custom1.TFrame")
        fr_ni.grid(row=4, column=0, padx=2,  pady=2, sticky="nsew")

        ni_atrs = [("x", "init_x"), ("y", "init_y"), ("h", "h")]

        for index, names in enumerate(ni_atrs):

            txt = ttk.Label(fr_ni, text= names[0], style="Custom1.TLabel")
            txt.grid(row=0, column=index*2, padx=4, pady=2)

            entry = ttk.Entry(fr_ni, width = 6)
            entry.grid(row=0, column=index*2+1, padx=4, pady=2)
            entry.insert(0, self.master.params[names[1]])      # Default value

            self.master.entries[names[1]] = entry

        self.master.toggle_widgets["fr_ni"] = fr_ni

        """ for cellular automaton """

        # master frame
        fr_ca = ttk.Frame(row_fr, style="Custom1.TFrame")
        fr_ca.grid(row=4, column=0, padx=2,  pady=2, sticky="nsew")

        ca_atrs = [("X", "init_X"), ("Y", "init_Y"), ("P", "init_P"), ("Q", "init_Q")]

        for index, names in enumerate(ca_atrs):

            txt = ttk.Label(fr_ca, text= names[0], style="Custom1.TLabel")
            txt.grid(row=0, column=index*2, padx=4, pady=2)

            entry = ttk.Entry(fr_ca, width=6)
            entry.grid(row=0, column=index*2+1, padx=4, pady=2)
            entry.insert(0, self.master.params[names[1]])      # Default value

            self.master.entries[names[1]] = entry

        self.master.toggle_widgets["fr_ca"] = fr_ca