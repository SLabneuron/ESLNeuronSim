"""
coding: utf-8

Created on Thu Nov 30 13:52

@author: SLab

BCSwitch controller
"""

#Libralies
import tkinter as tk
from tkinter import ttk
import pandas as pd
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
        #self.generate_file()
        self.create_directory()


    def create_directory(self):
        """Organize file for storage"""
        # Database path
        DATABASE_path = os.path.join("DATABASE","LIST1.csv")

        # Read database
        df = pd.read_csv(DATABASE_path)

        # Preperation for determining directories
        base_dir = os.getcwd() #current directory path

        # Model-specific directory
        model_dir = self.generate_model_directory(base_dir, self.model)

        # Iterate over DataFrame rows and create directions
        if df.empty:
            # generate row
            new_row = self.create_row_from_dicts([self.mp, self.cap, self.bifp], ["mp", "cap", "bifp"])
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            
            # generate dir_name
            hash_dir = self.generate_hash_directory(model_dir, df.iloc[-1])
            os.makedirs(hash_dir, exist_ok = True)
            
            # append row
            print(type(df))
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index = True)
        else:
            for index, row in df.iterrows():
                print("Hi")
                if all([self.row_matches(row, self.mp, "mp"),
                    self.row_matches(row, self.cap, "cap"),
                    self.row_matches(row, self.bifp, "bifp")
                    ]):
                    # Update directory or perform other actions
                    nested_dir = self.create_nested_directory(model_dir, row)
                else:
                    # Generate hash and create directory if not exist
                    hash_dir = self.generate_hash_directory(model_dir, row)
                    os.makedirs(hash_dir, exist_ok = True)


    def generate_model_directory(self, base_dir, model):
        model_dir = os.path.join(base_dir, "DATABASE","eca" if model == 1 else "ode")
        os.makedirs(model_dir, exist_ok = True)
        return model_dir


    def row_matches(self, row, param_dict, prefix):
        for key,value in param_dict.items():
            # Lambda 式の場合，適切に評価する
            if callable(value):
                value = str(value)
            column_name = f"{prefix}_{key}"
            if column_name not in row or str(row[column_name]) != value:
                print("False")
                return False
        print("True")
        return True


    def create_nested_directory(self, base_dir, row):
        # Create nested directory  structure based on row data
        dir_parts = [row[col] for col in row if col.startswith(("mp_","bifp_", "cap_"))]
        nested_dir = os.path.join(base_dir, *dir_parts)
        os.makedirs(nested_dir, exist_ok = True)
        return nested_dir


    def generate_hash_directory(self, base_dir,row):
        
        print(row)
        print(row.index)
        # Create directory name using hash
        hash_string = "".join(str(row[col]) for col in row.index if col.startswith(("mp_","bifp_","cap_")))
        hash_value = hashlib.md5(hash_string.encode()).hexdigest()
        hash_dir = os.path.join(base_dir, hash_value)
        return hash_dir


    def add_prefix_to_dict_keys(self, d, prefix):
        return {f"{prefix}_{key}": value for key, value in d.items()}


    def create_row_from_dicts(self, dicts, prefixes):
        new_row = {}
        for d, prefix in zip(dicts, prefixes):
            new_row.update(self.add_prefix_to_dict_keys(d, prefix))
        return new_row


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

