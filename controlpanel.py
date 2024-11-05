# -*- coding: utf-8 -*-

"""
Title: Ergodic Cellular Automaton biochemical switch

@author: shirafujilab

Created: 2024-10-15

Contents:

"""

# import standard library

import tkinter as tk
from tkinter import ttk
import os
import pandas as pd

# import my library


from src.utils.json_import import json_import
from src.utils.param_resolver import param_resolver
from src.ui_config.main_window import WindowSetup


class ControlPanel:

    def __init__(self):

        # initialize root widget
        self.root = tk.Tk()

        self.root_config()

        self.set_up()


    def root_config(self):

        # title
        self.root.title("ECA Simulator, biochemical switch")

        """ size setting """

        # main size
        self.root.geometry("880x600")

        """ Style Settings """

        # style
        style = ttk.Style()

        # frame style1: "Custom1.TFrame"
        style.configure("Custom1.TFrame",
                        background = "lightgray",
                        borderwidth = 2,
                        relief="solid")

        # frame style2: "Custom2.TFrame"
        style.configure("Custom2.TFrame",
                        background = "lightgray")

        # label style1: "Custom1.TLabel"
        style.configure("Custom1.TLabel",
                        background = "lightgray",
                        foreground = "black")


    def set_up(self):

        """ Set up parameter """

        # Parameter Import
        params = json_import(["bifurcation params",
                                "set 1",
                                "CA set",
                                "CA params",
                                "NI set",
                                "sim params"])

        # str equation make available
        resolve_params = param_resolver(params)

        """ Set up path """

        # Set up window
        WindowSetup(self.root, resolve_params)

        self.root.mainloop()


if __name__ == "__main__":

    # Execute simulator
    sim = ControlPanel()