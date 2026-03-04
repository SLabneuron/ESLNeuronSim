# -*- coding: utf-8 -*-

"""

Created on: 2024-10-18
Updated on: 2026-02-26

@author: SLab

Contents:



"""

# import standard libraries
from tkinter import ttk

# import my libraries
from src.ui_config.module_settings.frame_controller import FrControl
from src.ui_config.module_settings.frame_init_frame import FrInit
from src.ui_config.module_settings.frame_param_config import FrParamConfig

class ControlPanel:

    def __init__(self, master):

        # Get parent class
        self.master = master

        # Set up widgets
        self.set_widget()

        # parameter update
        self.master.parameter_update()


    def set_widget(self):

        """ Set up frames """

        # set up main frame
        fr = ttk.Frame(self.master.root)
        fr.grid(row=0, rowspan=2, column=0, sticky = "nw")

        # Set up frames
        row_frame0 = ttk.Frame(fr)
        row_frame0.grid(row=0, column=0, padx=2, pady=2)

        row_frame1 = ttk.Frame(fr)
        row_frame1.grid(row=1, column=0, padx=2, pady=2)

        row_frame2 = ttk.Frame(fr)
        row_frame2.grid(row=2, column=0, padx=2, pady=2)

        # ColumnConfig
        row_frame0.columnconfigure(0, minsize=350)
        row_frame1.columnconfigure(0, minsize=350)
        row_frame2.columnconfigure(0, minsize=350)

        """ Setting Frames """

        # For simulation condition [0, 0]
        FrControl(self.master, row_frame0)

        # initial state and time step (neumerical integration) [0, 1]
        FrInit(self.master, row_frame1)

        # For parameter setting [0, 2]
        FrParamConfig(self.master, row_frame2)

