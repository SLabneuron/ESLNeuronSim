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

        # set frame for TW
        self.create_time_waveforms(frame)

        # set frame for PP
        self.create_phase_portrait(frame)


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
        fr = ttk.Frame(frame, style="Graphic.TFrame")
        fr.grid(row=1, column=0, padx=2, pady=2)

        # Graph Space
        fig = Figure(figsize=(3, 3), facecolor="white", tight_layout=True)

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

        """ Set PP results canvas """

        # Label
        title = ttk.Label(frame, text = "Phase Portrait", style="Custom1.TLabel").grid(row=0, column=1, padx=2, pady=2)

        # Frame
        fr = ttk.Frame(frame, style="Graphic.TFrame")
        fr.grid(row=1, column=1, padx=2, pady=2)

        # Graph Space
        fig = Figure(figsize=(3, 3), facecolor="white", tight_layout=True)

        # Add plot of phase_portrait
        ax= fig.add_subplot()

        # Canvas
        canvas = FigureCanvasTkAgg(fig, master=fr)
        canvas.get_tk_widget().grid(row=0, column=0)

        # Store phase portrait
        self.master.axes["phase_portrait"] = ax


    def update_graphics(self):

        """ graphic TW and PP """
        # get master level
        model = self.master.combos["model"].get()
        params = self.master.params
        ax_TW1 = self.master.axes["waveform1"]
        ax_TW2 = self.master.axes["waveform2"]
        ax_pp = self.master.axes["phase_portrait"]

        # Init frames of time waveforms and phase portrait
        TW = GraphicTW(params, model, ax_TW1, ax_TW2)
        PP = GraphicPP(params, model, ax_pp)

        # results
        if self.master.results != None:
            T = self.master.results.t_hist
            X = self.master.results.x_hist
            Y = self.master.results.y_hist

            # Plot results
            TW.plot(T, X, Y)
            PP.plot(X, Y)

        # Graphics
        ax_TW1.figure.canvas.draw()
        ax_TW2.figure.canvas.draw()
        ax_pp.figure.canvas.draw()


