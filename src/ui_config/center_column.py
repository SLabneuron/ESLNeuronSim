# -*- coding: utf-8 -*-

"""

Created on: 2024-10-18

@author: SLab

Contents:

    main windown[col=1]: Graphic Space

"""


# import standard libralies
import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import numpy as np

# import my library

from src.analyses.null_cline import Nullcline


class CenterColumn:

    def __init__(self, master):

        # get parent class
        self.master = master

        # waveform
        self.fr_ni0 = None
        self.fr_ca0 = None

        # phase portrait
        self.fr_ni1 = None
        self.fr_ca1 = None


    def set_widget(self):

        # main frame
        fr = ttk.Frame(self.master.root)
        fr.grid(row=0, column=1, sticky = "nw")

        """ row 0: waveform """

        # set frame 0
        cframe0 = ttk.Frame(fr)
        cframe0.grid(row=0, column=0, padx=2, pady=2, sticky = "nw")

        cframe0.columnconfigure(0, minsize = 300)

        self.waveform_frame(cframe0)

        """ row 1: phase portrait """

        # set frame 1
        cframe1 = ttk.Frame(fr)
        cframe1.grid(row=1, column=0, padx=2, pady=2, sticky = "nw")

        cframe1.columnconfigure(0, minsize=300)

        self.phase_portrait(cframe1)

        """ Event binding """

        # Set entry bind update
        self.master.combos["model"].bind("<<ComboboxSelected>>", lambda event: self.update_display())
        self.master.combos["param set"].bind("<<ComboboxSelected>>", lambda event: self.update_display(), add="+")
        
        self.master.entries["Q"].bind("<Return>", lambda event: self.update_display())
        self.master.entries["S"].bind("<Return>", lambda event: self.update_display())
        

        # show display
        self.update_display()


    def waveform_frame(self, cfr0):

        # title
        title = ttk.Label(cfr0, text="Waveform")
        title.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")

        """ for neumerical integration """

        # master frame
        fr_ni = ttk.Frame(cfr0, style="Custom1.TFrame")

        # make plot space
        fig_ni = Figure(figsize=(3, 1.8), facecolor="lightgray", tight_layout=True)
        plt.rcParams.update({'font.size':8})

        # make canvas including fig
        canvas = FigureCanvasTkAgg(fig_ni, master = fr_ni)
        canvas.get_tk_widget().grid(row=0, column=0, padx=2, pady=2)

        ax = fig_ni.add_subplot()
        ax.set_xlim(self.master.params["sT"], self.master.params["eT"])
        ax.set_ylim(0, 1)
        ax.set_xlabel("Time")
        ax.set_ylabel("x, y")

        self.master.figs["fig_ni0"] = fr_ni

        """ for cellular automaton """

        # master frame
        fr_ca = ttk.Frame(cfr0, style="Custom1.TFrame")

        # make plot space
        fig_ca = Figure(figsize=(3, 1.8), facecolor="lightgray", tight_layout=True)
        plt.rcParams.update({'font.size':8})

        # make canvas including fig
        canvas = FigureCanvasTkAgg(fig_ca, master = fr_ca)
        canvas.get_tk_widget().grid(row=0, column=0, padx=2, pady=2)

        ax = fig_ca.add_subplot()
        ax.set_xlim(self.master.params["sT"], self.master.params["eT"])
        ax.set_ylim(0, self.master.params["N"])
        ax.set_xlabel("Time")
        ax.set_ylabel("X, Y")

        self.master.figs["fig_ca0"] = fr_ca

        # store frames for later access
        self.fr_ni0 = fr_ni
        self.fr_ca0 = fr_ca


    def phase_portrait(self, cfr1):

        # title
        title = ttk.Label(cfr1, text="PhasePortrait")
        title.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")

        """ for neumerical integration """

        # master frame
        fr_ni = ttk.Frame(cfr1, style="Custom1.TFrame")

        # make plot space
        fig_ni = Figure(figsize=(3, 2.8), facecolor="lightgray", tight_layout=True)
        plt.rcParams.update({'font.size':8})

        # make canvas including fig
        canvas = FigureCanvasTkAgg(fig_ni, master = fr_ni)
        canvas.get_tk_widget().grid(row=0, column=0, padx=2, pady=2)

        ax = fig_ni.add_subplot()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xlabel("Y")
        ax.set_ylabel("X")

        self.master.figs["fig_ni1"] = fr_ni
        self.master.axes["ax_ni1"] = ax

        """ for cellular automaton """

        # master frame
        fr_ca = ttk.Frame(cfr1, style="Custom1.TFrame")

        # make plot space
        fig_ca = Figure(figsize=(3, 2.8), facecolor="lightgray", tight_layout=True)
        plt.rcParams.update({'font.size':8})

        # make canvas including fig
        canvas = FigureCanvasTkAgg(fig_ca, master = fr_ca)
        canvas.get_tk_widget().grid(row=0, column=0, padx=2, pady=2)

        ax = fig_ca.add_subplot()
        ax.set_xlim(0, self.master.params["N"])
        ax.set_ylim(0, self.master.params["N"])
        ax.set_xlabel("Y")
        ax.set_ylabel("X")

        self.master.figs["fig_ca1"] = fr_ca
        self.master.axes["ax_ca1"] = ax

        # store frames for later access
        self.fr_ni1 = fr_ni
        self.fr_ca1 = fr_ca


    def update_display(self):

        # Get the value from the Combobox widget
        mode = self.master.combos["model"].get()

        # Remove both frames initially
        self.fr_ni0.grid_forget()
        self.fr_ca0.grid_forget()
        self.fr_ni1.grid_forget()
        self.fr_ca1.grid_forget()

        # Calculate nullcline
        self.master.parameter_update()
        inst = Nullcline(self.master.params)
        x1_null, x2_null = inst.nullcline_fx_x, inst.nullcline_fx_y
        y1_null, y2_null = inst.nullcline_fy_x, inst.nullcline_fy_y

        print(inst.equilibrium_points)

        # Display the appropriate frame based on the mode
        if mode in ["fem", "rk4", "ode45"]:
            self.fr_ni0.grid(row=1, column=0, padx=2, pady=2, sticky="nsew")
            self.fr_ni1.grid(row=1, column=0, padx=2, pady=2, sticky="nsew")

            # graphics of nullcline
            ax= self.master.axes["ax_ni1"]
            ax.clear()
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_xlabel("y")
            ax.set_ylabel("x")
            ax.scatter(x2_null, x1_null, marker=".", s=0.5)
            ax.scatter(y2_null, y1_null, marker=".", s=0.5)

            # set equilibrium
            ax.scatter(inst.equilibrium_points[:, 1], inst.equilibrium_points[:, 0], marker="x", c="red", s= 20)
            ax.figure.canvas.draw()

        elif mode in ["SynCA", "ErCA"]:
            self.fr_ca0.grid(row=1, column=0, padx=2, pady=2, sticky="nsew")
            self.fr_ca1.grid(row=1, column=0, padx=2, pady=2, sticky="nsew")

            # graphics of nullcline
            ax = self.master.axes["ax_ca1"]
            ax.clear()
            ax.set_xlim(0, self.master.params["N"])
            ax.set_ylim(0, self.master.params["N"])
            ax.set_xlabel("Y")
            ax.set_ylabel("X")
            ax.scatter(x2_null*self.master.params["N"], x1_null*self.master.params["N"], marker=".", s=0.1)
            ax.scatter(y2_null*self.master.params["N"], y1_null*self.master.params["N"], marker=".", s=0.1)

            # set equilibrium
            ax.scatter(inst.equilibrium_points[:, 1]*self.master.params["s1"], inst.equilibrium_points[:, 0]*self.master.params["s2"], marker="x", c="red", s= 20)
            ax.figure.canvas.draw()

        else:
            pass

