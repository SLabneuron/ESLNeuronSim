# -*- coding: utf-8 -*-
"""
Created on: 2024-10-22
Updated on: 2024-11-12

@author: shirafujilab

Contents: bifurcation for S

"""

# import standard library
import numpy as np
import pandas as pd
import os

import datetime

# import my library
from src.method.euler.ode_basic import  CalODE


class BifODE:

    def __init__(self, params, filename):

        # get params
        self.params = params

        self.filename = filename
        print(self.filename)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)

        self.make_xx_yy()


    def make_xx_yy(self):

        self.x = np.arange(0, 0.81, 0.02)
        self.y = np.arange(0, 0.81, 0.02)

        xx, yy = np.meshgrid(self.x, self.y)

        xx = xx.flatten()
        yy = yy.flatten()

        self.params["init_x"] = xx
        self.params["init_y"] = yy

        self.num_initial_conditions = xx.size


    def run(self):

        bif_S = np.arange(0, 0.81, 0.01)
        num_S = len(bif_S)
        num_IC = self.num_initial_conditions

        self.S_value = bif_S
        self.max_values = np.zeros((num_S, num_IC))
        self.min_values = np.zeros((num_S, num_IC))

        print("start: ", datetime.datetime.now())

        for idx, S in enumerate(bif_S):

            self.params["S"] = S

            inst = CalODE(self.params)
            inst.run()

            x_hist = inst.x_hist            # shape (num_time_steps, num_IC)

            x_max = np.max(x_hist, axis=0)  # shape (num_IC, )
            x_min = np.min(x_hist, axis=0)

            self.max_values[idx, :] = x_max
            self.min_values[idx, :] = x_min

        """ Store results as a DataFrame """

        num_points = len(self.x)
        df = pd.DataFrame({
            "Q": self.params["Q"],                           # fixed. 他とおなじshape にして
            "S": np.repeat(bif_S, num_points ** 2),  # Repeat S for each grid point
            "x": np.tile(self.params["init_x"], num_S),
            "y": np.tile(self.params["init_y"], num_S),
            "max_val": self.max_values.flatten(),
            "min_val": self.min_values.flatten()
        })

        # Save to CSV
        try:
            df.to_csv(self.filename, index=False)
            print(f"Results saved to {self.filename}")
        except Exception as e:
            print(f"Error saving results to {self.filename}: {e}")

        print("end: ", datetime.datetime.now())