# -*- coding: utf-8 -*-
"""
Created on: 2024-10-22
Updated on: 2024-11-12

@author: shirafujilab

Contents: bifurcation for S
    X: 0, 2, 4, ..., 63
    Y: 0, 2, 4, ..., 63

    Fixed: Q, P, Q, phX, phY


Benchmark:

    size of X, Y = 64*64 -> 14 minutes
    size of X, Y = 32*64 -> 3.5 minutes

"""

# import standard library
import numpy as np
import pandas as pd
import os

import datetime

# import my library
from src.method.eca.eca_basic import  CalCA


class BifECA:

    def __init__(self, params, filename):

        # get params
        self.params = params.copy()

        self.filename = filename
        print(self.filename)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)

        self.make_xx_yy()


    def make_xx_yy(self):

        self.x = np.arange(0, self.params["N"]-1, 2)
        self.y = np.arange(0, self.params["N"]-1, 2)

        xx, yy = np.meshgrid(self.x, self.y)

        xx = xx.flatten()
        yy = yy.flatten()

        self.params["init_X"] = xx
        self.params["init_Y"] = yy

        # Expand other parameters to match the size of xx and yy
        self.params["init_P"] = np.full_like(xx, self.params["init_P"], dtype=np.int32)
        self.params["init_Q"] = np.full_like(xx, self.params["init_Q"], dtype=np.int32)
        self.params["init_phX"] = np.full_like(xx, self.params["init_phX"], dtype=np.float64)
        self.params["init_phY"] = np.full_like(xx, self.params["init_phY"], dtype=np.float64)

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

            inst = CalCA(self.params)
            inst.run()

            x_hist = inst.x_hist            # shape (num_time_steps, num_IC)

            x_max = np.max(x_hist, axis=0)  # shape (num_IC, )
            x_min = np.min(x_hist, axis=0)

            self.max_values[idx, :] = x_max
            self.min_values[idx, :] = x_min

        """ Store results as a DataFrame """

        num_points = len(self.x)
        total_data_points = num_S * num_points ** 2

        Q_array = np.full(total_data_points, self.params["Q"], dtype=np.int32)


        """ Confirm data shape """
        # 各カラムデータの長さを揃える
        Q_array = np.full(total_data_points, self.params["Q"], dtype=np.int32).flatten()
        S_array = np.repeat(bif_S, num_points ** 2).flatten()
        X_array = np.tile(self.params["init_X"], num_S).flatten()
        Y_array = np.tile(self.params["init_Y"], num_S).flatten()
        max_val_array = self.max_values.flatten()
        min_val_array = self.min_values.flatten()

        print("\n--- Debugging Data Consistency ---")

        for col_name, col_data in zip(
            ["Q", "S", "x", "y", "max_val", "min_val"],
            [
                np.full(total_data_points, self.params["Q"], dtype=np.int32),
                np.repeat(bif_S, num_points ** 2),
                np.tile(self.params["init_X"], num_S),
                np.tile(self.params["init_Y"], num_S),
                self.max_values.flatten(),
                self.min_values.flatten(),
            ],
        ):
            print(f"{col_name}: Shape={col_data.shape}, Dtype={col_data.dtype}, Sample={col_data[:5]}")





        df = pd.DataFrame({
            "Q": Q_array,                           # fixed. 他とおなじshape にして
            "S": S_array,  # Repeat S for each grid point
            "x": X_array,
            "y": Y_array,
            "max_val": max_val_array,
            "min_val": min_val_array
        })


        # Save to CSV
        try:
            df.to_csv(self.filename, index=False)
            print(f"Results saved to {self.filename}")
        except Exception as e:
            print(f"Error saving results to {self.filename}: {e}")


        print("end: ", datetime.datetime.now())