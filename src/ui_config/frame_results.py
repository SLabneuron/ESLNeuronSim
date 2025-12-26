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
        fr = ttk.Frame(frame, style="Graphic.TFrame")
        fr.grid(row=1, column=1, padx=2, pady=2)

        # Graph Space
        fig = Figure(figsize=(3, 3), facecolor="white", tight_layout=True)

        # Add plot of phase_portrait
        phase_portrait = fig.add_subplot()

        # Canvas
        canvas = FigureCanvasTkAgg(fig, master=fr)
        canvas.get_tk_widget().grid(row=0, column=0)

        # Store phase portrait
        self.master.axes["phase_portrait"] = phase_portrait


  

    def update_graphics(self):

        """
        Summary:
            Plot results

        """

        # axes
        ax_TW1 = self.master.axes["waveform1"]
        ax_TW2 = self.master.axes["waveform2"]
        ax_pp = self.master.axes["phase_portrait"]

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


        # Graphics
        ax_TW1.figure.canvas.draw()
        ax_TW2.figure.canvas.draw()
        ax_pp.figure.canvas.draw()


