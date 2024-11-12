# -*- coding: utf-8 -*-

"""

Created on: 2024-11-11

@author: SLab

Contents:

    Results Frame: Time Evolution

    (ODE)
        - time waveforms
        - phase plain

    (ECA, RCA)

        - time waveforms
        - phase plain
        - return map for internal phase of switch signals

"""


# import standard libralies
import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import numpy as np


# import my library

from src.analyses.analysis_null_cline import Nullcline

from src.graphics.graphic_time_waveform import GraphicTimeWaveform as GraphicTW
from src.graphics.graphic_phase_plain import GraphicPhasePlain as GraphicPP

class TimeEvol:

    def __init__(self, master):

        # get parent class
        self.master = master



    def set_widget(self):

        # main frame
        fr = ttk.Frame(self.master.root)
        fr.grid(row=1, column=1, sticky = "nw")

        # title
        title = ttk.Label(fr, text="Results: Time Evolution")
        title.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")

        # set frame
        frame = ttk.Frame(fr, style="Custom1.TFrame")
        frame.grid(row=1, column=0, padx=2, pady=2, sticky = "nw")

        """ Results Frame """
        self.sets_results_frame(frame)

        # set graph areas
        self.update_graphics()


    def sets_results_frame(self, frame):

        """
        Summary:
            Create graphic space of phase portraits

        Contents:
            Time waveforms
            Phase portrait
            Internal phase of sw

        """

        self.create_time_waveforms(frame)

        self.create_phase_portrait(frame)

        self.create_internal_phase_of_sw(frame)


    def create_time_waveforms(self, frame):

        """
        Summary:
            Create graphic space of waveforms

        return:
            self.master.axes["waveform1"]
            self.master.axes["waveform2"]

        """

        # Label
        title = ttk.Label(frame, text = "Time Waveforms", style="Custom1.TLabel")
        title.grid(row=0, column=0, padx=2, pady=2)

        # Frame
        fr = ttk.Frame(frame, style="Custom2.TFrame")
        fr.grid(row=1, column=0, padx=2, pady=2)

        # Graph Space
        fig = Figure(figsize=(2.2, 2.1), facecolor="lightgray", tight_layout=True)

        # Add plot of waveform 1, 2
        waveform1 = fig.add_subplot(2, 1, 1)
        waveform2 = fig.add_subplot(2, 1, 2)

        # Canvas
        canvas = FigureCanvasTkAgg(fig, master=fr)
        canvas.get_tk_widget().grid(row=0, column=0)

        # Store self.axes
        self.master.axes["waveform1"] = waveform1
        self.master.axes["waveform2"] = waveform2


    def create_phase_portrait(self, frame):

        """
        Summary:
            Create graphic space of phase portraits

        return:
            self.master.axes["phase_portrait"]

        """

        # Label
        title = ttk.Label(frame, text = "Phase Portrait", style="Custom1.TLabel")
        title.grid(row=0, column=1, padx=2, pady=2)

        # Frame
        fr = ttk.Frame(frame, style="Custom2.TFrame")
        fr.grid(row=1, column=1, padx=2, pady=2)

        # Graph Space
        fig = Figure(figsize=(2.2, 2.1), facecolor="lightgray", tight_layout=True)

        # Add plot of phase_portrait
        phase_portrait = fig.add_subplot()

        # Canvas
        canvas = FigureCanvasTkAgg(fig, master=fr)
        canvas.get_tk_widget().grid(row=0, column=0)

        # Store phase portrait
        self.master.axes["phase_portrait"] = phase_portrait


    def create_internal_phase_of_sw(self, frame):

        """
        Summary:
            Create graphic space of return map for internal phase of sw

        return:
            self.master.radio_button["which_sw"]
            self.master.axes["phase of sw"]

        """

        # Label
        title = ttk.Label(frame, text = "Internal Phase of", style="Custom1.TLabel")
        title.grid(row=0, column=2, padx=2, pady=2, sticky="ne")

        # StringBar of switch signal
        radio_button_var_sw = tk.StringVar(value="Sx")

        radio_sx = ttk.Radiobutton(frame, text="Sx", variable=radio_button_var_sw, value="Sx", style="Custom1.TRadiobutton")
        radio_sx.grid(row=0, column=3, padx=2, pady=2, sticky="ne")

        radio_sy = ttk.Radiobutton(frame, text="Sy", variable=radio_button_var_sw, value="Sy", style="Custom1.TRadiobutton")
        radio_sy.grid(row=0, column=4, padx=2, pady=2, sticky="nw")

        self.master.radio_buttons["which_sw"] = radio_button_var_sw

        # Frame
        fr = ttk.Frame(frame, style="Custom2.TFrame")
        fr.grid(row=1, column=2, columnspan=3, padx=2, pady=2)

        # Graph Space
        fig = Figure(figsize=(2.2, 2.1), facecolor="lightgray", tight_layout=True)

        # Add plot of phase_portrait
        return_map = fig.add_subplot()

        # Canvas
        canvas = FigureCanvasTkAgg(fig, master=fr)
        canvas.get_tk_widget().grid(row=0, column=0)

        # Store self.axes
        self.master.axes["phase of switch"] = return_map


    def update_graphics(self):

        """
        Summary:
            Plot results

        """

        # Time Waveforms
        TW = GraphicTW(self.master)

        # Plot time waveforms
        # TW.plot(T, X, Y)

        # Phase Portrait
        PP = GraphicPP(self.master, self.master.axes["phase_portrait"])

        # Plot time waveforms
        # PP.plot(X, Y)



    def update_display(self):

        # Get the value from the Combobox widget
        mode = self.master.combos["model"].get()

        # Remove both frames initially
        self.fr_ni.grid_forget()
        self.fr_ca.grid_forget()

        # Calculate nullcline
        self.master.parameter_update()
        inst = Nullcline(self.master.params)

        # Set nullcline
        x1_null, x2_null = inst.nullcline_fx_x, inst.nullcline_fx_y
        y1_null, y2_null = inst.nullcline_fy_x, inst.nullcline_fy_y

        """ Graphic Results """

        # Display the appropriate frame based on the mode
        if mode in ["fem", "rk4", "ode45"]:
            self.fr_ni.grid(row=1, column=0, padx=2, pady=2, sticky="nw")

            # graphics of nullcline
            ax= self.master.axes["ax_ni"]
            ax.clear()
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_xlabel("y")
            ax.set_ylabel("x")
            ax.scatter(x2_null, x1_null, marker=".", s=0.5)
            ax.scatter(y2_null, y1_null, marker=".", s=0.5)

            # plot results
            # ax.scatter(marker=".", c="red", s= 20)

        elif mode in ["SynCA", "ErCA"]:
            self.fr_ca.grid(row=1, column=0, padx=2, pady=2, sticky="nw")

            # graphics of nullcline
            ax = self.master.axes["ax_ca"]
            ax.clear()
            ax.set_xlim(0, self.master.params["N"])
            ax.set_ylim(0, self.master.params["N"])
            ax.set_xlabel("Y")
            ax.set_ylabel("X")
            ax.scatter(x2_null*self.master.params["N"], x1_null*self.master.params["N"], marker=".", s=0.1)
            ax.scatter(y2_null*self.master.params["N"], y1_null*self.master.params["N"], marker=".", s=0.1)

            # plot results
            # ax.scatter(marker=".", c="red", s= 20)

        else:
            pass

        ax.figure.canvas.draw()


