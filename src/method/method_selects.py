# -*- coding: utf-8 -*-

"""
Title: method select

@author: shirafujilab

Created: 2024-11-14

Contents:

    ode (fem, rk4, ode45):

        - time waveforms (phase portraits)
        - attraction basin
        - bifurcation
        - return map


    CA (SynCA, ErCA):

        - time waveforms (phase portraits)
        - attraction basin
        - bifurcation
        - return map

Arguments:

    master: top module

        master.combos["model"] or params
            fem, rk4, ode45, SynCA, ErCA

        master.combos["simulation"] or params
            time evolution
            bifurcation
            attraction basin
            Poincare map (return map)
            stability

"""


# import my library
from src.method.euler.ode_basic import CalODE
from src.method.eca.eca_basic import CalCA
from src.method.euler.ode_bif import BifODE
from src.method.eca.eca_bif import BifECA




class MethodSelects:

    def __init__(self, master):

        self.master = master

        self.file_name = master.file_name

        # get information
        model = master.params["model"]
        sim_type = master.params["simulation"]

        if model in ["fem", "rk4", "ode45"]:
            self.sim_ode(sim_type)
        else:
            self.sim_ca(sim_type)


    def sim_ode(self, sim_type):

        if sim_type == "time evolution":
            self.master.results = CalODE(self.master.params)
            self.master.results.run()
        elif sim_type == "bifurcation":
            self.master.results_bif = BifODE(self.master.params, self.file_name)
            self.master.results_bif.run()


    def sim_ca(self, sim_type):

        if sim_type == "time evolution":
            self.master.results = CalCA(self.master.params)
            self.master.results.run()
        if sim_type == "bifurcation":
            self.master.results_bif = BifECA(self.master.params, self.file_name)
            self.master.results_bif.run()