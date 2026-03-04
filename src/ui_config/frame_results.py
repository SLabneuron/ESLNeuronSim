# -*- coding: utf-8 -*-

"""

Created on: 2024-11-11
Updated on: 2026-02-26

@author: SLab



"""


# import standard libralies
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

# import my library
from src.graphics.graphic_time_waveform import GraphicTimeWaveform as GraphicTW



class ResultPanel:

    def __init__(self, master):

        # get parent class
        self.master = master

        # init graphic array
        self._init_graphic(master.params)

        # Right panel
        fr = ttk.Frame(self.master.root)
        fr.grid(row=0, column=1, sticky = "nw")

        # set widget
        self.set_widget(fr)

    def _init_graphic(self, params):

        # time
        sT, eT, h = params["sT"], params["eT"], np.float32(params["h"])

        # store step
        total_step = int(eT/h)+1
        index_start = int(sT/h)
        store_step = (total_step - index_start) // 100 + 1 if total_step > index_start else 0

        self.t_hist = np.zeros(store_step)
        self.x_hist = np.zeros(store_step)
        self.y_hist = np.zeros(store_step)
        self.z_hist = np.zeros(store_step)


    def set_widget(self, fr):

        # title
        title = ttk.Label(fr, text=f"Results: {self.master.params['model']}")
        title.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")

        # set frame
        frame = ttk.Frame(fr, style="Custom1.TFrame")
        frame.grid(row=1, column=0, padx=2, pady=2, sticky = "nw")

        # set frame for TW
        self.create_time_waveforms(frame)


    def create_time_waveforms(self, frame):

        # Label
        title = ttk.Label(frame, text = "Time Waveforms", style="Custom1.TLabel")
        title.grid(row=0, column=0, padx=2, pady=2, sticky=tk.W)

        # Frame
        fr = ttk.Frame(frame, style="Graphic.TFrame")
        fr.grid(row=1, column=0, padx=2, pady=2, sticky=tk.W)

        # Graph Space
        fig = Figure(figsize=(4.5, 5), facecolor="white", tight_layout=True)

        # Add plot of waveform 1, 2, 3
        self.ax1 = fig.add_subplot(3, 1, 1)
        self.ax2 = fig.add_subplot(3, 1, 2, sharex=self.ax1)
        self.ax3 = fig.add_subplot(3, 1, 3, sharex=self.ax1)

        # Canvas
        canvas = FigureCanvasTkAgg(fig, master=fr)
        canvas.get_tk_widget().pack()

        toolbar = NavigationToolbar2Tk(canvas, fr)
        toolbar.update()
        toolbar.pack()


    def update_graphics(self):

        """ graphic TW and PP """
        # get master level
        model = self.master.combos["model"].get()
        params = self.master.params

        # graphic result
        result = GraphicTW(params, model, self.ax1, self.ax2, self.ax3)
        result.plot(self.t_hist, self.x_hist, self.y_hist, self.z_hist)

        # Graphics
        self.ax1.figure.canvas.draw()
        self.ax2.figure.canvas.draw()
        self.ax3.figure.canvas.draw()


    def event_bindings(self):

        def update():

            self.master.parameter_update()

            # update graphics
            self.update_graphics()

        self.master.combos["model"].bind("<<ComboboxSelected>>", lambda e: update(), add="+")

        for key, item in self.master.entries.items():

            if isinstance(item, ttk.Entry):

                self.master.entries[key].bind("<Return>", lambda e: update(), add="+")

        # Init graphics
        update()