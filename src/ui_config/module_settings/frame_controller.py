# -*- coding: utf-8 -*-

"""
Title: frame_settings > controller setting

@author: shirafujilab

Created: 2024-11-14

Contents:

    - Model select

    - Simulation

    - Execute

Return:

    - master.combos["model"]

        fem, SynCA, ErCA

    - master.combos["simulation"]

        time evolution
        bifurcation
        parameter region
        attraction basin
        Poincare map (return map)

"""

# import standard library
import tkinter as tk
from tkinter import ttk


class FrControl:

    def  __init__(self, master, fr):

        self.master = master

        self.set_control_window(fr)


    def set_control_window(self, row_fr):

        # Title
        title = ttk.Label(row_fr, text="Controller")
        title.grid(row=0, column=0, padx=2,  pady=2, sticky="nsew")

        # master frame
        fr = ttk.Frame(row_fr, style="Custom1.TFrame")
        fr.grid(row=1, column=0, padx=2,  pady=2, sticky="nsew")

        # column setting
        fr.columnconfigure(0, minsize= 80)
        fr.columnconfigure(1, minsize=100)

        """ Setting: Model, Target"""

        # model select
        text0 = ttk.Label(fr, text="Model:", style="Custom1.TLabel")
        text0.grid(row=0, column=0, padx=2, pady=2, sticky=tk.W)

        # make combobox
        def on_combobox_select(event):

            selected_value = combo0.get()

            if selected_value in ["fem"]:
                self.toggle_widgets("fr_ni")
            else:
                self.toggle_widgets("fr_ca")

        combo0_value = ["fem", "SynCA", "ErCA"]
        combo0 = ttk.Combobox(fr, values=combo0_value, width=15)
        combo0.grid(row=0, column=1, padx=2, pady=2)
        combo0.set("ErCA")  # Default value
        combo0.bind("<<ComboboxSelected>>", on_combobox_select)
        self.master.combos["model"] = combo0

        """ Setting: Simulation """

        # simulation select
        text1 = ttk.Label(fr, text="Simulation:", style="Custom1.TLabel")
        text1.grid(row=1, column=0, padx=2, pady=2, sticky=tk.W)

        combo1_value = ["time evolution", "bifurcation", "parameter region", "attraction basin", "ReturnMap"]
        combo1 = ttk.Combobox(fr, values=combo1_value, width=15)
        combo1.grid(row=1, column=1, padx=2, pady=2)
        combo1.set("time evolution")  # Default value
        self.master.combos["simulation"] = combo1

        # execute button
        text2 = ttk.Label(fr, text="Execute: ", style="Custom1.TLabel")
        text2.grid(row=2, column=0, padx=2, pady=2, sticky=tk.W)

        button1 = ttk.Button(fr, text="Start", command=self.master.run_simulation)
        button1.grid(row=2, column=1, padx=2, pady=2)


    def toggle_widgets(self, show):

        # all hidden
        for _, widget in self.master.toggle_widgets.items():
            widget.grid_remove()

        # select "show" widget appear
        self.master.toggle_widgets[show].grid()