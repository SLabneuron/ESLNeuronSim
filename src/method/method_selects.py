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

Note:

    Before Cal, parameter must be liseted up

"""

# import standard library
import numpy as np

import matplotlib.pyplot as plt

import datetime, time

# import ode library
from src.method.euler.ode_basic import TimeEvolOdeSingle
from src.method.euler.ode_net import TimeEvolOdeNetwork
from src.method.euler.ode_bif import BifODE

# import eca library
from src.method.eca.eca_basic import TimeEvolEcaSingle, _make_lut_numba
from src.method.eca.eca_net import TimeEvolEcaNetwork
from src.method.eca.eca_bif import BifECA



from src.method.eca.eca_lut import make_lut_for_verilog



class MethodSelects:

    def __init__(self, master):

        # get master and filename
        self.master = master
        self.file_name = master.file_name

        # get information
        model, sim_type = master.params["model"], master.params["simulation"]

        if model in ["ode"]:
            self.sim_ode(sim_type)
        elif model in ["esl"]:
            self.sim_esl(sim_type)


    def sim_ode(self, sim_type):
        
        inst = self.master.results

        if sim_type == "time evolution (single)":
            time_evol = TimeEvolOdeSingle(self.master.params, self.file_name)
            inst.t_hist, _, inst.x_hist, inst.y_hist, inst.z_hist = time_evol.run()

        elif sim_type == "time evolution (network)":
            time_evol = TimeEvolOdeNetwork(self.master.params, self.file_name)
            inst.t_hist, inst.x_hist = time_evol.run()

        #elif sim_type == "bifurcation (single)":
        #    self.master.results_bif = BifODE(self.master.params, self.file_name)
        #    self.master.results_bif.run()

        #elif sim_type == "bifurcation (network)":
        #    self.master.results_bif = BifODE(self.master.params, self.file_name)
        #    self.master.results_bif.run()

        else:
            print("not implemented")


    def sim_esl(self, sim_type):

        inst = self.master.results

        if sim_type == "time evolution (single)":
            time_evol = TimeEvolEcaSingle(self.master.params, self.file_name)
            inst.t_hist, _, inst.x_hist, inst.y_hist, inst.z_hist = time_evol.run()

        elif sim_type == "time evolution (network)":
            time_evol = TimeEvolEcaNetwork(self.master.params, self.file_name)
            inst.t_hist, inst.x_hist = time_evol.run()

        #elif sim_type == "bifurcation (single)":
        #   self.master.results_bif = BifECA(self.master.params, self.file_name)
        #    self.master.results_bif.run()

        #elif sim_type == "bifurcation (network)":
        #    self.master.results_bif = BifECA(self.master.params, self.file_name)
        #    self.master.results_bif.run()

        #elif sim_type == "Output LUT":

        #    make_lut_for_verilog(self.master.params, self.file_name, "normal")

        else:
            print("not implemented")

