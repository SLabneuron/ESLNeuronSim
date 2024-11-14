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
import csv
import numpy as np
import sys


# import local libralies
from src.ui_config.frame_settings import SimSettings
from src.ui_config.frame_sys_overview import SysOverview
from src.ui_config.frame_results import TimeEvol

from src.method.euler.ode_basic import CalODE


class WindowSetup:

    def __init__(self, root, params):

        self.root = root
        self.params = params
        self.entries = {}
        self.combos = {}
        self.radio_buttons = {}
        self.labels = {}
        self.figs = {}
        self.axes = {}
        self.tables = {}

        self.toggle_widgets = {}  # For store init frame widgets

        self.set_widget()


    def set_widget(self):

        # set (row, col) = (0:1, 0)
        self.sim_settings = SimSettings(self)

        ###
        # Calculate Numerical Integration
        self.results = CalODE(self.params)
        self.results.run()
        ###

        # set (row, col) = (0, 1)
        self.sys_overview = SysOverview(self)
        self.sys_overview.set_widget()

        # set (row, col) = (1, 1)
        self.time_evol =TimeEvol(self)
        self.time_evol.set_widget()


    def parameter_update(self):

        """ Parameter update """

        # update entries
        for param in self.entries:

            widget = float(self.entries[param].get())

            self.params[param] = widget

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

        """ Execute Simulation """

        # Calculate Numerical Integration
        self.results = CalODE(self.params)
        self.results.run()


        # Plot: Results time evolution
        self.time_evol.update_graphics()




