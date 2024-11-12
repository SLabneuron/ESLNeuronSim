# -*- coding: utf-8 -*-

"""

Created on: 2024-10-18

@author: SLab

Contents:

    main windown[col=0]: simulation setting

"""

# import standard libraries
import tkinter as tk
from tkinter import ttk

# import my libraries
from src.utils.json_import import json_import
from src.utils.param_resolver import param_resolver

class SimSettings:

    def __init__(self, master):

        # get parent class
        self.master = master


    def set_widget(self):

        # main frame
        fr = ttk.Frame(self.master.root)
        fr.grid(row=0, rowspan=2, column=0, sticky = "nw")

        # control of size of column width
        size=300

        # For simulation condition [0, 0]

        row_frame0 = ttk.Frame(fr)
        row_frame0.grid(row=0, column=0, padx=2, pady=2)

        row_frame0.columnconfigure(0, minsize=size)

        self.main_frame(row_frame0)

        # initial state and time step (neumerical integration) [0, 1]

        row_frame1 = ttk.Frame(fr)
        row_frame1.grid(row=1, column=0, padx=2, pady=2)

        row_frame1.columnconfigure(0, minsize=size)

        self.init_frame(row_frame1)

        # For parameter setting [0, 2]

        row_frame2 = ttk.Frame(fr)
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
        self.master.combos["model"] = combo0

        # simulation select
        text1 = ttk.Label(fr, text="Simulation:", style="Custom1.TLabel")
        text1.grid(row=1, column=0, padx=2, pady=2, sticky=tk.W)

        combo1_value = ["time evolution", "bifurcation", "attraction basin", "Poincare Map", "Stability"]
        combo1 = ttk.Combobox(fr, values=combo1_value, width=15)
        combo1.grid(row=1, column=1, padx=2, pady=2)
        combo1.set("time evolution")  # Default value
        self.master.combos["simulation"] = combo1

        # execute button
        text2 = ttk.Label(fr, text="Execute: ", style="Custom1.TLabel")
        text2.grid(row=2, column=0, padx=2, pady=2, sticky=tk.W)

        button1 = ttk.Button(fr, text="Start", command=self.master.run_simulation)
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
            entry.insert(0, self.master.params[names[1]])      # Default value

            self.master.entries[names[1]] = entry

        self.master.init_widgets["fr_ni"] = fr_ni

        """ for cellular automaton """

        # master frame
        fr_ca = ttk.Frame(row_fr, style="Custom1.TFrame")
        fr_ca.grid(row=4, column=0, padx=2,  pady=2, sticky="nsew")

        ca_atrs = [("X", "init_X"), ("Y", "init_Y"), ("P", "init_P"), ("Q", "init_Q")]

        for index, names in enumerate(ca_atrs):

            txt = ttk.Label(fr_ca, text= names[0], style="Custom1.TLabel")
            txt.grid(row=0, column=index*2, padx=4, pady=2)

            entry = ttk.Entry(fr_ca, width=6)
            entry.grid(row=0, column=index*2+1, padx=4, pady=2)
            entry.insert(0, self.master.params[names[1]])      # Default value

            self.master.entries[names[1]] = entry

        self.master.init_widgets["fr_ca"] = fr_ca

        self.toggle_widgets("fr_ca")


    def toggle_widgets(self, show):

        for key, widget in self.master.init_widgets.items():
            # all hidden
            widget.grid_remove()
        
        # "show" widget appear
        self.master.init_widgets[show].grid()


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
        self.set_sim_param_frame(fr, 4)


    def set_bif_param_frame(self, widget, r):

        """ Setting: Bifurcation Parameters """

        # Title
        title = ttk.Label(widget, text="Bifurcation Parameter", style = "Custom1.TLabel")
        title.grid(row=r, column=0, columnspan=2, padx=2,  pady=2, sticky=tk.W)

        # widget
        fr = ttk.Frame(widget, style = "Custom2.TFrame")
        fr.grid(row=r+1, column=0, padx=2,  pady=2,sticky=tk.W)

        """ Set widgets"""

        atrs = ["Q", "S"]

        for index, n in enumerate(atrs):

            txt = ttk.Label(fr, text= n, style="Custom1.TLabel")
            txt.grid(row=0, column=index*2, padx=4, pady=2)

            entry = ttk.Entry(fr, width = 6)
            entry.grid(row=0, column=index*2+1, padx=4, pady=2)
            entry.insert(0, self.master.params[n])      # Default value

            self.master.entries[n] = entry

        """ Parameter set select """

        # model select
        tex = ttk.Label(fr, text="Param Set", style="Custom1.TLabel")
        tex.grid(row=0, column=4, padx=2, pady=2, sticky=tk.W)

        def on_combobox_select(event):

            select = combo.get()

            """ Set up parameter """

            # Parameter Import
            params = json_import(["bifurcation params",
                                        select,
                                        "CA set",
                                        "CA params",
                                        "NI set",
                                        "sim params"])

            # str equation make available
            self.master.params = param_resolver(params)

            # parameter update
            self.master.parameter_update()
            


        combo_value = ["set 1", "set 2", "set 3", "set 4"]
        combo = ttk.Combobox(fr, values=combo_value, width=10)
        combo.grid(row=0, column=5, padx=2, pady=2)
        combo.set("set 1")  # Default value
        combo.bind("<<ComboboxSelected>>", on_combobox_select)
        self.master.combos["param set"] = combo


    def set_ca_param_frame(self, widget, r):
        """ Setting: CA parameters """

        # Title
        text = ttk.Label(widget, text="CA parameters", style="Custom1.TLabel")
        text.grid(row=r, column=0, columnspan=3, padx=2, pady=2, sticky=tk.W)

        # widget
        fr = ttk.Frame(widget, style="Custom2.TFrame")
        fr.grid(row=r+1, column=0, padx=2,  pady=2, sticky=tk.W)

        fr_col_config = [30, 30, 30, 30]

        for i, width in enumerate(fr_col_config):
            fr.columnconfigure(i, minsize=width)

        """ Set widgets: CA parameters columns = [0, 1]"""

        atrs1 = [("N: 2 **", "Ns"), ("M: 2 **", "Ms"),
                ("s1: 2 **", "s1_s"), ("s2: 2 **", "s2_s"),
                ("Tc:", "Tc"),
                ("Tx:", "Tx_rat"), ("Ty:", "Ty_rat")]

        for index, n in enumerate(atrs1):

            txt = ttk.Label(fr, text= n[0], style="Custom1.TLabel")
            txt.grid(row=index, column=0, padx=6, pady=2, sticky=tk.W)

            sv = tk.StringVar(value=self.master.params[n[1]])
            entry = ttk.Entry(fr, width = 6, textvariable=sv)
            entry.grid(row=index, column=1, padx=4, pady=2)

            self.master.entries[n[1]] = sv

            if n[1] in ["Ns", "Ms", "s1_s", "s2_s"]:
                sv.trace_add("write", lambda name, idx, op, sv=sv, key=n[1]: self.update_power_label(sv, key))


        """ Set widgets: CA parameters columns = [2, 3] """

        atrs2 = [(0, "Ns"), (1, "Ms"), (2, "s1_s"), (3, "s2_s"), (5, "Tx_sqrt"), (6, "Ty_sqrt")]

        self.master.power_labels = {}

        for index, n in enumerate(atrs2):

            if n[0] in [0, 1, 2, 3]:

                string = "= " + str(2 ** int(self.master.entries[n[1]].get()))

                txt = ttk.Label(fr, text= string, style="Custom1.TLabel")
                txt.grid(row=n[0], column=2, columnspan=2, padx=4, pady=2, sticky=tk.W)
                self.master.power_labels[n[1]] = txt

            elif n[0] in [5, 6]:

                txt = ttk.Label(fr, text= "*√", style="Custom1.TLabel")
                txt.grid(row=n[0], column=2, padx=4, pady=2, sticky=tk.E)

                entry = ttk.Entry(fr, width = 6)
                entry.grid(row=n[0], column=3, padx=4, pady=2)
                entry.insert(0, self.master.params[n[1]])      # Default value

                self.master.entries[n[1]] = entry


    def update_power_label(self, sv, key):

        value = sv.get()

        lut = {"Ns": "N", "Ms": "M", "s1_s": "s1", "s2_s": "s2"}

        try:
            result = 2 ** int(value)
            self.master.power_labels[key].config(text=f"= {result}")

            # update self.master.params[N, M]
            self.master.params[lut[key]] = result
        except ValueError:
            self.master.power_labels[key].config(text="= ...")


    def set_sim_param_frame(self, row_fr, r):

        """ Preset """

        # Title
        title = ttk.Label(row_fr, text="Simulation Parameter", style="Custom1.TLabel")
        title.grid(row=r, column=0, columnspan=3, padx=2, pady=2, sticky=tk.W)

        # master frame
        fr =ttk.Frame(row_fr, style="Custom2.TFrame")
        fr.grid(row=r+1, column=0, padx=2, pady=2, sticky="nsew")

        fr_column_setting = [30, 30, 30, 30]

        for index, span in enumerate(fr_column_setting):
            fr.columnconfigure(index, minsize=span)

        """ Setting: Simulation Condition """

        atrs = ["sT", "eT"]

        for index, name in enumerate(atrs):

            txt = ttk.Label(fr, text = name, style = "Custom1.TLabel")
            txt.grid(row=0, column=index*2, padx=4, pady=2, sticky="nsew")

            entry = ttk.Entry(fr, width=6)
            entry.grid(row=0, column=index*2+1, padx=4, pady=2)
            entry.insert(0, self.master.params[name])      # Default value

            self.master.entries[name] = entry

