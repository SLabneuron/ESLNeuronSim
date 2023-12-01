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

#Local Libralies
from ode_basic import BSwitch as ode
from eca_basic import BSwitch as eca
from analysis_bif import BIF



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
        self.sp = simp
        self.val_init = val_init

        
        

    def select(self):
        if (self.model == 0 and self.target == 0):
            print("cae time waveform")
        elif (self.model == 0 and self.target == 1):
            print("eca bif diagram")
        elif (self.model == 0 and self.target == 2):
            print("eca parameter region")
        elif (self.model == 0 and self.target == 3):
            print("eca phase portrait")
        elif (self.model == 0 and self.target == 4):
            print("eca theoretical analysis")
        elif (self.model == 1 and self.target == 0):
            print("eca time waveform")
        elif (self.model == 1 and self.target == 1):
            print("eca bif diagram")
        elif (self.model == 1 and self.target == 2):
            print("eca parameter region")
        elif (self.model == 1 and self.target == 3):
            print("eca phase portrait")
        elif (self.model == 1 and self.target == 4):
            print("eca theoretical analysis")
        else:
            print("error")
        
    
    

if __name__ == "__main__":
    """Test"""
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
        "b1":"0.13*(1+self.Q1)",
        "b2":0,
        "WE11":3.9,
        "WE12":0,
        "WE21":3.0,
        "WE22":3.0,
        "WI11":0,
        "WI12":"0.5*self.Q1",
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
    



