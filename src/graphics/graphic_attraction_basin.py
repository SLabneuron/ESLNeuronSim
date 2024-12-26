# -*- coding: utf-8 -*-
"""

Created on: 2024-12-03
Updated on: 2024-12-03

@author: shirafujilab

Contents: graphic following contents

        - heat map
        - nullclines
        - timewaveform

"""


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re

class PhasePlanePlotter:
    def __init__(self, init_x, init_y, state_data):

        # default is heatmap

        self.init_x = init_x
        self.init_y = init_y
        self.state_data = state_data

        # make, fig, add
        self.fig, self.ax = plt.subplots(figsize=(8, 6))

        self.add_heatmap()

        # 座標表示をカスタマイズ
        self.ax.format_coord = self._custom_format_coord

    def _custom_format_coord(self, x, y):

        # setting lower right

        return f"x={y:.3f}, y={x:.3f}"


    def add_heatmap(self, cmap='viridis'):

        #c = self.ax.pcolormesh(self.init_x, self.init_y, np.flipud(self.state_data), shading='auto', cmap=cmap)
        c = self.ax.pcolormesh(self.init_y, self.init_x, self.state_data, shading='auto', cmap=cmap)
        self.fig.colorbar(c, ax=self.ax, label='State')


    def add_nullclines(self, nullcline_x, nullcline_y, color='red'):

        self.ax.scatter(nullcline_y, nullcline_x, color=color, s=1, label='Nullcline')

    def add_result(self, x, y, c="red", l="equ"):

        # plot eq or po (yx axis)
        self.ax.scatter(y, x, color=c, marker='o', s=20, label=l)



    def show(self, title='Phase Space with Nullclines and Equilibrium Points'):

        self.ax.set_xlabel('init_y (x-axis)')
        self.ax.set_ylabel('init_x (y-axis)')
        self.ax.set_title(title)
        self.ax.grid()
        #self.ax.legend()
        plt.show(block=True)





if __name__ == "__main__":

    # filepath
    filename = r"C:\Storage\02_paper\03_2025_TEEE\04_Python\data\results\set 1\ErCA\condition_1\attraction basin\attraction_basin_Q_0.4_S_0.52_time_20241222225819.csv"

    match = re.search(r"set \d+\\([^\\]+)\\", filename)

    if match:
        model = match.group(1)


    if model == "ode":

        df = pd.read_csv(filename)

        x = np.arange(0, 1.01, 0.01)
        y = np.arange(0, 1.01, 0.01)

    elif model == "ErCA":

        df = pd.read_csv(filename)

        x = np.arange(0, 64, 1)
        y = np.arange(0, 64, 1)


    xx, yy = np.meshgrid(x, y)
    states = np.array(df["state"].tolist())

    states = states.reshape(xx.shape)

    #print(xx, yy, states.shape)

    inst = PhasePlanePlotter(xx, yy, states)

    inst.show()