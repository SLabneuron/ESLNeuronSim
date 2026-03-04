# -*- coding: utf-8 -*-

"""

Created on: 2023-11-30
Updated on: 2026-02-26

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
from src.ui_config.frame_settings import ControlPanel
from src.ui_config.frame_results import ResultPanel

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

        self.string_var = {}            # entry
        self.power_labels = {}          # entry

        self.toggle_widgets = {}  # For store init frame widgets

        self.results = None

        self.set_widget()


    def set_widget(self):

        # set (row, col) = (0, 0) > Left Panel
        self.settings = ControlPanel(self)

        # set (row, col) = (0, 1) > Right Panel
        self.results = ResultPanel(self)

        self.results.event_bindings()


    def run_simulation(self):

        # 1. Update values
        self.parameter_update()

        # 2. File directory
        data_lib = DataLibrarian(self.params)
        self.file_name = data_lib.save_path

        # 3. Run simulation
        MethodSelects(self)

        # 4. Plot
        self.results.update_graphics()


    def parameter_update(self):

        """ Parameter update """

        self.params["model"] = self.combos["model"].get()
        self.params["simulation"] = self.combos["simulation"].get()

        # update entries
        for param in self.entries:

            widget = self.entries[param]

            self.params[param] = float(widget.get())

        for param in self.string_var:

            widget = self.string_var[param]

            self.params[param] = widget

        # calculate Tx, Ty, Tz
        self.params["Tx"] = self.params["Tx_rat"] * self.params["Tx_sqrt"] ** (1/2)
        self.params["Ty"] = self.params["Ty_rat"] * self.params["Ty_sqrt"] ** (1/2)
        self.params["Tz"] = self.params["Tz_rat"] * self.params["Tz_sqrt"] ** (1/2)
        self.params["Wx"] = self.params["Wx_rat"] * self.params["Wx_sqrt"] ** (1/2)
        self.params["Wy"] = self.params["Wy_rat"] * self.params["Wy_sqrt"] ** (1/2)
        self.params["Wz"] = self.params["Wz_rat"] * self.params["Wz_sqrt"] ** (1/2)