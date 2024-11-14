# -*- coding: utf-8 -*-

"""


Created on: 2024-10-18

@author: SLab

Contents:

    Controller

        - Model
        - Simulation
        - Execute

    Init variables

        - for ODE (x, y, h)
        - for CA (X, Y, P, Q)

    Parameters

        - Bifurcation Parameters (Q, S)
        - CA Parameters (N, M, s1, s2, Tc, Tx, Ty)
        - Simulation Parameter (sT, eT)

"""

# import standard libraries
from tkinter import ttk

# import my libraries
from src.ui_config.module_settings.frame_controller import FrControl
from src.ui_config.module_settings.frame_init_frame import FrInit
from src.ui_config.module_settings.frame_param_config import FrParamConfig

class SimSettings:

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
        row_frame0.columnconfigure(0, minsize=300)
        row_frame1.columnconfigure(0, minsize=300)
        row_frame2.columnconfigure(0, minsize=300)

        """ Setting Frames """

        # For simulation condition [0, 0]
        FrControl(self.master, row_frame0)

        # initial state and time step (neumerical integration) [0, 1]
        FrInit(self.master, row_frame1)

        # For parameter setting [0, 2]
        FrParamConfig(self.master, row_frame2)

