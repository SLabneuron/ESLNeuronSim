# -*- coding: utf-8 -*-

"""

Created on: 2023-11-30
Updated on: 2024-10-22

@author: SLab

Contents:


"""

# import standard libralies
import tkinter as tk
from tkinter import ttk
import datetime
import csv
import numpy as np
import sys


# import local libralies
from src.ui_config.frame_settings import SimSettings
from src.ui_config.frame_sys_overview import SysOverview
from src.ui_config.frame_results import TimeEvol

from src.method.method_selects import MethodSelects

from src.utils.data_librarian import DataLibrarian


class WindowSetup:

    def __init__(self, root, params):

        self.root = root

        self.params = params
        self.entries = {}
        self.combos = {}
        self.radio_buttons = {}
        self.axes = {}
        self.tables = {}

        self.string_var = {}
        self.toggle_widgets = {}  # For store init frame widgets

        self.results = None
        self.results_ab = None
        self.results_bif = None
        self.results_pr = None

        self.set_widget()


    def set_widget(self):

        # set (row, col) = (0:1, 0)
        self.sim_settings = SimSettings(self)

        # set (row, col) = (0, 1)
        self.sys_overview = SysOverview(self)

        # set (row, col) = (1, 1)
        self.time_evol =TimeEvol(self)

        self.event_bindings()

        # calculate and plot initial conditions
        #self.time_evol.update_graphics()


    def event_bindings(self):

        def update():

            # update parameter
            self.parameter_update()

            # update graphics
            self.sys_overview.update_display()
            self.time_evol.update_graphics()

            # Plot: Results time evolution
            self.run_simulation



        self.combos["model"].bind("<<ComboboxSelected>>", lambda e: update(), add="+")
        self.combos["param set"].bind("<<ComboboxSelected>>", lambda e: update(), add="+")

        for key, item in self.entries.items():

            if isinstance(item, ttk.Entry):

                self.entries[key].bind("<Return>", lambda e: update(), add="+")


        # Init graphics
        update()



    def parameter_update(self):

        """ Parameter update """

        # update entries
        for param in self.entries:

            widget = self.entries[param]

            self.params[param] = float(widget.get())

        for param in self.string_var:

            widget = self.string_var[param]

            self.params[param]

        # update combos
        for param in self.combos:

            widget = self.combos[param].get()

            self.params[param] = widget

        # calculate Tx, Ty
        self.params["Tx"] = self.params["Tx_rat"] * self.params["Tx_sqrt"] ** (1/2)
        self.params["Ty"] = self.params["Ty_rat"] * self.params["Ty_sqrt"] ** (1/2)

        # resolve lambda equ
        self.params["b1"] = eval(self.params["b1_equ"])()
        self.params["b2"] = eval(self.params["b2_equ"])()
        self.params["WI12"] = eval(self.params["WI12_equ"])()


    def run_simulation(self):

        # update values
        self.parameter_update()
        
        #print(self.params)
        
        # file directory
        data_lib = DataLibrarian(self.params)
        self.file_name = data_lib.save_path

        """ Execute Simulation """

        # Run simulation
        MethodSelects(self)

        # Plot: Results time evolution
        self.time_evol.update_graphics()
        
        print("Complete Simulation", datetime.datetime.now())
        
        print("\n\n")