# -*- coding: utf-8 -*-

"""
Title: frame_settings > param configure

@author: shirafujilab

Created: 2024-11-14

Contents:

    Neumerical Integration (ni)
        - forward euler method (fem),
        - rouge kutta 4-th order (rk4),
        - scipy ode45 solver (ode45)


    Cellular Automaton (CA)
        - ergodic cellular automaton (eca)
        - regular cellular automaton (rca)


Return:

    - master.params

        N, M, s1, s2


    - master.entries (dict)

        Q, S
        Ns, Ms, s1_s, s2_s, Tc, Tx_rat, Tx_sqrt, Ty_rat, Ty_sqrt
        sT, eT

    - master.combos["param set"]

        set 1, set 2, set 3, set 4


    - master.power_labels

        N, M, s1, s2


"""

# import standard library
import tkinter as tk
from tkinter import ttk

# import my libraries
from src.utils.json_import import json_import
from src.utils.param_resolver import param_resolver


class FrParamConfig:

    def  __init__(self, master, fr):

        # get master
        self.master = master

        # set up
        self.set_param_config(fr)


    def set_param_config(self, row_fr):

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
                ("deg:", "deg"),
                ("Tc:", "Tc"),
                ("Tx:", "Tx_rat"), ("Ty:", "Ty_rat")]

        for index, n in enumerate(atrs1):

            txt = ttk.Label(fr, text= n[0], style="Custom1.TLabel")
            txt.grid(row=index, column=0, padx=6, pady=2, sticky=tk.W)

            if n[1] in ["Ns", "Ms", "s1_s", "s2_s"]:

                sv = tk.StringVar(value=self.master.params[n[1]])
                entry = ttk.Entry(fr, width = 6, textvariable=sv)
                entry.grid(row=index, column=1, padx=4, pady=2)

                sv.trace_add("write", lambda name, idx, op, sv=sv, key=n[1]: self.update_power_label(sv, key))

                self.master.string_var[n[1]]= sv

            else:

                entry = ttk.Entry(fr, width = 6)
                entry.grid(row=index, column=1, padx=4, pady=2)
                
                entry.insert(0, self.master.params[n[1]])

                self.master.entries[n[1]] = entry


        """ Set widgets: CA parameters columns = [2, 3] """

        atrs2 = [(0, "Ns"), (1, "Ms"), (2, "s1_s"), (3, "s2_s"), (6, "Tx_sqrt"), (7, "Ty_sqrt")]

        self.master.power_labels = {}

        for index, n in enumerate(atrs2):

            if n[0] in [0, 1, 2, 3]:

                string = "= " + str(2 ** int(self.master.string_var[n[1]].get()))

                txt = ttk.Label(fr, text= string, style="Custom1.TLabel")
                txt.grid(row=n[0], column=2, columnspan=2, padx=4, pady=2, sticky=tk.W)
                self.master.power_labels[n[1]] = txt

            elif n[0] in [6, 7]:

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