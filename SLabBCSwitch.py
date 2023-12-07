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
import os
import hashlib

#Local Libralies
from ode_basic import BCSwitch as ode
from eca_basic import BSwitch as eca # Unchainged Object
from analysis_bif import Bif
from lib.graphic_basic import Graphic



class BCSwitch:
    """
    ** model
    0: ode, 1: eca

    ** target:
    0: time waveform, 1:bif diagram, 2:parameter region
    3: phase portrait, 4: Theoretical Analysis(plan)

    ** graphic:
    0: off, 1: on

    ** bifp (bifurcation parameters)
    They represent bifurcation parameter
    bifp = [[Q1,...], [S,...]]


    ** mp (model parameters)
    They represent target model parameter
        {
        "tau1":,
        "tau2":,
        "b1":,
        "b2":,
        "WE11":,
        "WE12":,
        "WE21":,
        "WE22":,
        "WI11":,
        "WI12":,
        "WI21":,
        "WI22":,
        }

    ** cap (ca parameter)
    They represent CA parameter
        s = ?? # unit of scaling
        {
        "N":,
        "M":,
        "s1":,
        "s2":,
        "Tc":,
        "Tx":,
        "Ty":,
        }

    ** simp (simulation parameter)
        {
        "sT":,
        "eT":,
        }

    ** val_init
        {
        "x":,
        "y":,
        }

    """
    def __init__(self, model, target, graphic, bifp, mp, cap, simp, val_init):
        self.model = model
        self.target = target
        self.graphic = graphic
        self.bifp = bifp
        self.mp = mp
        self.cap = cap
        self.simp = simp
        self.val_init = val_init

        #graphical array
        self.t_hist = np.array([])
        self.x_hist = np.array([])
        self.y_hist = np.array([])
        
        #make file
        self.generate_file()


    def generate_hash(self):
        self.model_name = {"model":self.model,}
        self.target_name = {"target": self.target,}
        hash_base = {**self.model_name, **self.target_name, **self.bifp, **self.mp, **self.cap}
        hash_string = "_".join(f"{key}{value}" for key, value in hash_base.items())
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    def generate_file(self, data_dir="DATABASE"):
        base_hash = self.generate_hash()
        file_name = f"{base_hash}.csv"
        file_path = os.path.join(data_dir, file_name)
        
        count = 1
        while self.file_exists_in_dir(file_name, data_dir):
            file_name = f"{base_hash}_{count}.csv"
            file_path = os.path.join(data_dir, file_name)
            count += 1
        
        return file_name
    
    def file_exists_in_dir(self, file_name, directory):
        # Search for directory, and subdirectory, and subsubdir...
        for dirpath, dirname, filenames in os.walk(directory):
            if file_name in filenames:
                return True
        return False
        

    def select(self):
        if (self.model == 0 and self.target == 0):
            self.ode_time_waveform()
        elif (self.model == 0 and self.target == 1):
            self.ode_bif_diagram()
        elif (self.model == 0 and self.target == 2):
            self.ode_parameter_region()
        elif (self.model == 0 and self.target == 3):
            self.ode_phase_portrait
        elif (self.model == 0 and self.target == 4):
            self.ode_theoretical_analysis()
        elif (self.model == 1 and self.target == 0):
            self.eca_time_waveform()
        elif (self.model == 1 and self.target == 1):
            self.eca_bif_diagram()
        elif (self.model == 1 and self.target == 2):
            self.eca_parameter_region()
        elif (self.model == 1 and self.target == 3):
            self.eca_phase_portrait()
        elif (self.model == 1 and self.target == 4):
            self.eca_theoretical_analysis()
        else:
            print("error")


    def ode_time_waveform(self):
        print("ode time waveform")
        self.master = ode(self.bifp, self.mp, self.simp, self.val_init)
        t_hist, x_hist, y_hist = self.master.Run()

        if self.graphic == 1:
            self.figure = Graphic(t_hist, [0,0.8], x_hist, y_hist)
            self.figure.graphics()

    def ode_bif_diagram(self):
        print("ode bif diagram")
        self.master = bif(self.model, self.bifp, self.mp, self.cap, self.simp, self.val_init)
        S_hist, Q1_hist, max_hist, min_hist = self.master.bif_ode()

    def ode_parameter_region(self):
        print("ode parameter region")

    def ode_phase_portrait(self):
        print("ode phase portrait")

    def ode_theoretical_analysis(self):
        print("ode theoretical analysis")

    def eca_time_waveform(self):
        print("eca time waveform")

    def eca_bif_diagram(self):
        print("eca bif diagram")

    def eca_parameter_region(self):
        print("eca parameter region")

    def eca_phase_portrait(self):
        print("eca phase portrait")

    def eca_theoretical_analysis(self):
        print("eca theoretical analysis")


def main_ConPane():
    #initialization
    mode = 1
    
    Q1_hist = 0.5
    S_hist = np.arange(0.5, 0.55, 0.001)
    bifp ={
        "Q1": Q1_hist,
        "S":S_hist,
    }
    
    mp = {
        "tau1":1,
        "tau2":1,
        "b1":lambda Q1 = bifp[Q1]: 0.13*(1+Q1),
        "b2":0,
        "WE11":3.9,
        "WE12":0,
        "WE21":3.0,
        "WE22":3.0,
        "WI11":0,
        "WI12":lambda Q1 = bifp[Q1]: 0.5*Q1,
        "WI21":0,
        "WI22":0,
    }

    s=6
    cap = {
        "N":2**s,
        "M":2**(s),
        "s1":2**s,
        "s2":2**s,
        "Tc":0.01,
        "Tx":0.01*(1.713**(1/2)),
        "Ty":0.01*(2.313**(1/2)),
    }

    simp = {
        "sT":0,
        "eT":10,
    }

    val_init ={
        "x":19,
        "y":30,
        "p":0,
        "q":0,
    }

    main = BCSwitch(1, 0, 0, bifp, mp, cap, simp, val_init)
    main.select()



if __name__ == "__main__":
    main_ConPane()

