"""
coding: utf-8

Created on Thu Nov 30 13:52

@author: SLab

BCSwitch controller
"""

#Libralies
import tkinter as tk
from tkinter import ttk
import csv
import numpy as np
import sys


#Local Libralies
#from src.ui_config.SLabBCSwitch import BCSwitch as control
#from src.method.euler.ode_basic import BCSwitch as ode
#from src.method.eca.eca_basic import BSwitch as eca
#from src.analyses.analysis_bif import Bif
#from src.graphics.graphic_basic import Graphic

# BCSwitch Controller GUI

class WindowSetup:

    def __init__(self, root, params):

        self.root = root
        self.params = params
        self.entries = {}
        self.combos = {}
        self.labels = {}
        
        self.init_widgets = {}  # For store init frame widgets

        self.set_widget()


    def set_widget(self):
        
        # contorol of size of column width
        size=300

        # For simulation condition [0, 0]

        row_frame0 = ttk.Frame(self.root)
        row_frame0.grid(row=0, column=0, padx=2, pady=2)

        row_frame0.columnconfigure(0, minsize=size)

        self.main_frame(row_frame0)

        # initial state and time step (neumerical integration) [0, 1]

        row_frame1 = ttk.Frame(self.root)
        row_frame1.grid(row=1, column=0, padx=2, pady=2)

        row_frame1.columnconfigure(0, minsize=size)

        self.init_frame(row_frame1)

        # For parameter setting [0, 2]

        row_frame2 = ttk.Frame(self.root)
        row_frame2.grid(row=2, column=0, padx=2, pady=2, sticky=tk.W)

        row_frame2.columnconfigure(0, minsize=size)

        self.param_config(row_frame2)


    def main_frame(self, row_fr):

        """ Preset """

        # Title
        title = ttk.Label(row_fr, text="Controller")
        title.grid(row=0, column=0, padx=2,  pady=2, sticky="nsew")

        # master frame
        fr = ttk.Frame(row_fr, style="Custom1.TFrame")
        fr.grid(row=1, column=0, padx=2,  pady=2, sticky="nsew")

        fr_column_setting = [80, 100]

        for index, span in enumerate(fr_column_setting):
            fr.columnconfigure(index, minsize=span)

        """ Setting: Model, Target"""

        # model select
        text0 = ttk.Label(fr, text="Model:", style="Custom1.TLabel")
        text0.grid(row=0, column=0, padx=2, pady=2, sticky=tk.W)

        def on_combobox_select(event):

            selected_value = combo0.get()


            if selected_value in ["fem", "rk4", "ode45"]:
                self.toggle_widgets("fr_ni")

            else:
                self.toggle_widgets("fr_ca")


        combo0_value = ["fem", "rk4", "ode45", "SynCA", "ErCA"]
        combo0 = ttk.Combobox(fr, values=combo0_value, width=15)
        combo0.grid(row=0, column=1, padx=2, pady=2)
        combo0.set("ErCA")  # Default value
        combo0.bind("<<ComboboxSelected>>", on_combobox_select)
        self.combos["model"] = combo0

        # simulation select
        text1 = ttk.Label(fr, text="Simulation:", style="Custom1.TLabel")
        text1.grid(row=1, column=0, padx=2, pady=2, sticky=tk.W)

        combo1_value = ["time evolution", "bifurcation", "attraction basin", "Poincare Map", "Stability"]
        combo1 = ttk.Combobox(fr, values=combo1_value, width=15)
        combo1.grid(row=1, column=1, padx=2, pady=2)
        combo1.set("time evolution")  # Default value
        self.combos["simulation"] = combo1

        # execute button
        text2 = ttk.Label(fr, text="Execute: ", style="Custom1.TLabel")
        text2.grid(row=2, column=0, padx=2, pady=2, sticky=tk.W)

        button1 = ttk.Button(fr, text="Start", command=self.run_simulation)
        button1.grid(row=2, column=1, padx=2, pady=2)


    def init_frame(self, row_fr):

        """
        model =

        ni  :   forward euler method (fem),
                rouge kutta 4-th order (rk4),
                scipy ode45 solver (ode45)

        ca  :   ergodic cellular automaton (eca)
                regular cellular automaton (rca)

        """

        # Title
        title = ttk.Label(row_fr, text="Init variables, and time step h (ni only)")
        title.grid(row=3, column=0, padx=2,  pady=2, sticky="nsew")

        """ for neumerical integration """

        # master frame
        fr_ni = ttk.Frame(row_fr, style="Custom1.TFrame")
        fr_ni.grid(row=4, column=0, padx=2,  pady=2, sticky="nsew")

        ni_atrs = [("x", "init_x"), ("y", "init_y"), ("h", "h")]

        for index, names in enumerate(ni_atrs):

            txt = ttk.Label(fr_ni, text= names[0], style="Custom1.TLabel")
            txt.grid(row=0, column=index*2, padx=4, pady=2)

            entry = ttk.Entry(fr_ni, width = 6)
            entry.grid(row=0, column=index*2+1, padx=4, pady=2)
            entry.insert(0, self.params[names[1]])      # Default value

            self.entries[names[1]] = entry

        self.init_widgets["fr_ni"] = fr_ni

        """ for neumerical integration """

        # master frame
        fr_ca = ttk.Frame(row_fr, style="Custom1.TFrame")
        fr_ca.grid(row=4, column=0, padx=2,  pady=2, sticky="nsew")

        ca_atrs = [("X", "init_X"), ("Y", "init_Y"), ("P", "init_P"), ("Q", "init_Q")]

        for index, names in enumerate(ca_atrs):

            txt = ttk.Label(fr_ca, text= names[0], style="Custom1.TLabel")
            txt.grid(row=0, column=index*2, padx=4, pady=2)

            entry = ttk.Entry(fr_ca, width=6)
            entry.grid(row=0, column=index*2+1, padx=4, pady=2)
            entry.insert(0, self.params[names[1]])      # Default value

            self.entries[names[1]] = entry

        self.init_widgets["fr_ca"] = fr_ca

        self.toggle_widgets("fr_ca")


    def toggle_widgets(self, show):

        for key, widget in self.init_widgets.items():
            # all hidden
            widget.grid_remove()
        
        # "show" widget appear
        self.init_widgets[show].grid()



    def param_config(self, row_fr):

        """ Preset """

        # Title
        title = ttk.Label(row_fr, text="Parameters")
        title.grid(row=5, column=0, padx=2,  pady=2, sticky="nsew")

        # master frame
        fr = ttk.Frame(row_fr, style="Custom1.TFrame")
        fr.grid(row=6, column=0, padx=2,  pady=2, sticky="nsew")


        # row 0
        self.set_bif_param_frame(fr, 0)

        # row 1
        self.set_ca_param_frame(fr, 2)

        # row 2
        #self.set_sim_param_frame(fr, 4)


    def set_bif_param_frame(self, widget, r):

        """ Setting: Bifurcation Parameters """

        # Title
        title = ttk.Label(widget, text="Bifurcation Parameter", style = "Custom1.TLabel")
        title.grid(row=r, column=0, columnspan=2, padx=2,  pady=2, sticky=tk.W)

        # widget
        fr = ttk.Frame(widget, style = "Custom2.TFrame")
        fr.grid(row=r+1, column=0, padx=2,  pady=2,sticky=tk.W)

        """ Set widgets"""

        atrs = ["Q1", "S"]

        for index, n in enumerate(atrs):

            txt = ttk.Label(fr, text= n, style="Custom1.TLabel")
            txt.grid(row=0, column=index*2, padx=4, pady=2)

            entry = ttk.Entry(fr, width = 6)
            entry.grid(row=0, column=index*2+1, padx=4, pady=2)
            entry.insert(0, self.params[n])      # Default value

            self.entries[n] = entry



    def set_ca_param_frame(self, widget, r):
        """ Setting: CA parameters """

        # Title
        text = ttk.Label(widget, text="CA parameters", style="Custom1.TLabel")
        text.grid(row=r, column=0, columnspan=3, sticky=tk.W)

        # widget
        fr = ttk.Frame(widget, style="Custom2.TFrame")
        fr.grid(row=r+1, column=0, padx=2,  pady=2, sticky=tk.W)
        
        fr_col_config = [30, 30, 30, 30]
        
        for i, width in enumerate(fr_col_config):
            fr.columnconfigure(i, minsize=width)

        """ Set widgets: CA parameters columns = [0, 1]"""

        atrs1 = [("N: 2 **", "Ns"), ("M: 2 **", "Ms"),
                ("s1: 2 **", "s1"), ("s2: 2 **", "s2"),
                ("Tc:", "Tc"),
                ("Tx:", "Tx_rat"), ("Ty:", "Ty_rat")]

        for index, n in enumerate(atrs1):

            txt = ttk.Label(fr, text= n[0], style="Custom1.TLabel")
            txt.grid(row=index, column=0, padx=4, pady=2, sticky=tk.W)

            sv = tk.StringVar(value=self.params[n[1]])
            entry = ttk.Entry(fr, width = 6, textvariable=sv)
            entry.grid(row=index, column=1, padx=4, pady=2)

            self.entries[n[1]] = sv
            
            if n[1] in ["Ns", "Ms"]:
                sv.trace_add("write", lambda name, idx, op, sv=sv, key=n[1]: self.update_power_label(sv, key))



        """ Set widgets: CA parameters columns = [2, 3] """

        atrs2 = [(0, "Ns"), (1, "Ms"), (5, "Tx_sqrt"), (6, "Ty_sqrt")]
        
        self.power_labels = {}

        for index, n in enumerate(atrs2):

            if n[0] in [0, 1]:

                string = "= " + str(2 ** int(self.entries[n[1]].get()))

                txt = ttk.Label(fr, text= string, style="Custom1.TLabel")
                txt.grid(row=n[0], column=2, columnspan=2, padx=4, pady=2, sticky=tk.W)
                self.power_labels[n[1]] = txt

            elif n[0] in [5, 6]:

                txt = ttk.Label(fr, text= "*√", style="Custom1.TLabel")
                txt.grid(row=n[0], column=2, padx=4, pady=2, sticky=tk.E)

                entry = ttk.Entry(fr, width = 6)
                entry.grid(row=n[0], column=3, padx=4, pady=2)
                entry.insert(0, self.params[n[1]])      # Default value

                self.entries[n[1]] = entry

    def update_power_label(self, sv, key):
        value = sv.get()
        try:
            result = 2 ** int(value)
            self.power_labels[key].config(text=f"= {result}")
            
            # update self.params[N, M]
            self.params[key[0]] = result
        except ValueError:
            self.power_labels[key].config(text="= ...")



    def set_sim_param_frame(self, fr):

        """ Setting: Simulation Condition [11:??]"""

        # Title
        title11 = ttk.Label(fr, text="Simulation Parameter")
        title11.grid(row=0, column=0, columnspan=3)

        text11 = ttk.Label(fr, text="sT:")
        text11.grid(row=1, column=0)
        self.simp_sT = tk.Entry(fr)
        self.simp_sT.grid(row=1, column=1)
        self.simp_sT.insert(0, "0")  # Default value

        text12=ttk.Label(fr, text="eT:")
        text12.grid(row=1, column=2)
        self.simp_eT = tk.Entry(fr)
        self.simp_eT.grid(row=1, column=3)
        self.simp_eT.insert(0, "10")  # Default value


    def run_simulation(self):

        for param in self.entries:

            widget = float(self.entries[param].get())

            self.params[param] = widget
        
        # calculate Tx, Ty
        self.params["Tx"] = self.params["Tx_rat"] * self.params["Tx_sqrt"] ** (1/2)
        self.params["Ty"] = self.params["Ty_rat"] * self.params["Ty_sqrt"] ** (1/2)
        
        self.params["b1"] = eval(self.params["b1_equ"])()
        self.params["WI12"] = eval(self.params["WI12_equ"])()
        
        print(self.params)

        # BCSwitchインスタンスの作成（call for SLabBCSwitch.py）
        #bcs = control(model, target, graphic, bifp, mp, cap, simp, val_init)
        #bcs.select()  # 選択した操作の実行



