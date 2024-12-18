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
import matplotlib.pyplot as plt

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
        self.ax.legend()
        plt.show()
