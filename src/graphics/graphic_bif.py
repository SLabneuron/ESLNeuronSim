# -*- coding: utf-8 -*-
"""
Created on Thur July 13 13:26:03 2023

@author: shirafujilab
"""

import matplotlib.pyplot as plt
import pandas as pd



class Graphic:
    def __init__(self, horizontal, vertical, max_hist, min_hist):
        #config
        self.horizontal = horizontal
        self.vertical = vertical

        #graphic_array
        self.max_hist = max_hist
        self.min_hist = min_hist


    def graphics(self):

        plt.figure(figsize=(8,5))

        plt.plot(self.horizontal, self.max_hist, "o", markersize = 0.8, color = "black")
        plt.plot(self.horizontal, self.min_hist, "o", markersize = 0.8, color = "black")
        plt.xlim(self.horizontal[0],self.horizontal[-1])
        plt.ylim(0, 0.8)

        plt.show()






if __name__ == "__main__":

    # CSV 読み込み

    # ode 1
    #filename = r"c:\Storage\02_paper\04_2025_Nolta journal\04_Python\data\results\set 1\forward euler\results\bifurcation\20260108104158.csv"   # ← 適宜変更

    # ode 2
    #filename = r"c:\Storage\02_paper\04_2025_Nolta journal\04_Python\data\results\set 2\forward euler\results\bifurcation\20260108133406.csv"

    # normal eca 1
    #filename = r"c:\Storage\02_paper\04_2025_Nolta journal\04_Python\data\results\set 1\ergodic CA\results\bifurcation\20260108181459.csv"

    # normal eca 2
    #filename = r"c:\Storage\02_paper\04_2025_Nolta journal\04_Python\data\results\set 2\ergodic CA\results\bifurcation\20260108181716.csv"

    # rotated eca 1
    #filename = r"c:\Storage\02_paper\04_2025_Nolta journal\04_Python\data\results\set 1\rotated-LUT CA\results\bifurcation\20260108183242.csv"

    # rotated eca 2
    #filename = r"c:\Storage\02_paper\04_2025_Nolta journal\04_Python\data\results\set 2\rotated-LUT CA\results\bifurcation\20260108183406.csv"

    # rotated eca 2026-02-09
    filename = r"c:\Storage\02_paper\04_2025_Nolta journal\04_Python\data\results\set 1\rotated-LUT CA\results\bifurcation\20260209150333.csv"


    df = pd.read_csv(filename)

    # 分岐図プロット
    plt.figure(figsize=(6, 4))

    plt.scatter(df["S"], df["max_val"], s=1, c="black", label="max")
    plt.scatter(df["S"], df["min_val"], s=1, c="black", label="min")

    plt.xlabel("S")
    plt.ylabel("Value")
    plt.title("Bifurcation Diagram")
    plt.tight_layout()
    plt.show()
