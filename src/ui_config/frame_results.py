# -*- coding: utf-8 -*-

"""

Created on: 2024-11-11

@author: SLab

Contents:

    Results Frame: Time Evolution

    (ODE)
        - time waveforms
        - phase plain (master.axes["phase_portrait"])

    (ECA, RCA)

        - time waveforms
        - phase plain
        - return map for internal phase of switch signals

Return:

    - master.axes["waveform1"]
    - master.axes["waveform2"]
    - master.axes["phase_portrait"]
    - master.axes["phase of sw"]

    - master.radio_button["which_sw"]

"""


# import standard libralies
import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import numpy as np


# import my library
from src.graphics.graphic_time_waveform import GraphicTimeWaveform as GraphicTW
from src.graphics.graphic_phase_plain import GraphicPhasePlain as GraphicPP
from src.graphics.graphic_return_map import GraphicSwitchPhase as GraphicSP

class TimeEvol:

    def __init__(self, master):

        # get parent class
        self.master = master

        # set widget
        self.set_widget()


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

        self.sets_results_frame(frame)


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

        # axes
        ax_TW1 = self.master.axes["waveform1"]
        ax_TW2 = self.master.axes["waveform2"]
        ax_pp = self.master.axes["phase_portrait"]
        ax_sp = self.master.axes["phase of switch"]

        # results
        if self.master.results != None:
            T = self.master.results.t_hist
            X = self.master.results.x_hist
            Y = self.master.results.y_hist

        # Time Waveforms
        TW = GraphicTW(self.master)

        # Plot time waveforms
        if self.master.results != None: TW.plot(T, X, Y)

        # Phase Portrait
        PP = GraphicPP(self.master, ax_pp)

        # Plot phase portrait
        if self.master.results != None: PP.plot_result(X, Y)

        # Internal Phase of Sw (SP)
        SP = GraphicSP(self.master)

        # Plot return map
        # Phase = Phase_X if self.master.radio_button["which_sw"] == "Sx" else Phase_Y
        # if self.master.results != None: SP.plot(Phase)

        # Graphics
        ax_TW1.figure.canvas.draw()
        ax_TW2.figure.canvas.draw()
        ax_pp.figure.canvas.draw()
        ax_sp.figure.canvas.draw()

