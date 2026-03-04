# -*- coding: utf-8 -*-

"""
Title: frame_settings > controller setting

@author: shirafujilab

Created on: 2024-11-14
Updated on: 2026-02-26


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
        self.master.toggle_widgets["fr_esl"].grid()


    def set_init_window(self, row_fr):

        # Title
        title = ttk.Label(row_fr, text="Init variables")
        title.grid(row=3, column=0, padx=2,  pady=2, sticky="nsew")

        """ for neumerical integration """

        # master frame
        fr_ode = ttk.Frame(row_fr, style="Custom1.TFrame")
        fr_ode.grid(row=4, column=0, padx=2,  pady=2, sticky="nsew")

        ni_atrs = [("x", "init_x"), ("y", "init_y"), ("z", "init_z")]

        for idx, names in enumerate(ni_atrs):

            txt = ttk.Label(fr_ode, text= names[0], style="Custom1.TLabel")
            txt.grid(row=idx, column=0, padx=4, pady=2)

            entry = ttk.Entry(fr_ode, width = 6)
            entry.grid(row=idx, column=1, padx=4, pady=2)
            entry.insert(0, self.master.params[names[1]])      # Default value

            self.master.entries[names[1]] = entry

        self.master.toggle_widgets["fr_ode"] = fr_ode

        """ for cellular automaton """

        # master frame
        fr_esl = ttk.Frame(row_fr, style="Custom1.TFrame")
        fr_esl.grid(row=4, column=0, padx=2,  pady=2, sticky="nsew")

        ca_atrs = [("X", "init_X"), ("P", "init_P"),
                   ("Y", "init_Y"), ("Q", "init_Q"),
                   ("Z", "init_Z"), ("R", "init_R")]


        for idx, names in enumerate(ca_atrs):

            txt = ttk.Label(fr_esl, text= names[0], style="Custom1.TLabel")
            txt.grid(row=idx//2, column=(idx%2)*2, padx=4, pady=2)

            entry = ttk.Entry(fr_esl, width=6)
            entry.grid(row=idx//2, column=(idx%2)*2+1, padx=4, pady=2)
            entry.insert(0, self.master.params[names[1]])      # Default value

            self.master.entries[names[1]] = entry

        self.master.toggle_widgets["fr_esl"] = fr_esl