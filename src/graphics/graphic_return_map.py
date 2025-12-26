# -*- coding: utf-8 -*-

"""

Created on: 2024-11-12

@author: SLab

Contents:

    Return Map

"""

# import standard library
import numpy as np
import matplotlib.pyplot as plt

class GraphicReMap:

    def __init__(self):

        """ Set arguments """

        self.fig, self.axs= plt.subplots(2, 2, figsize=(8, 8))

        # config plot area
        self._config_plot_area()


    def _config_plot_area(self):
        
        # settings (0)

        self.axs[0][0].set_xlabel("n")
        self.axs[0][0].set_ylabel("n+1")
        self.axs[0][0].set_xticks(range(0, 64))
        self.axs[0][0].set_yticks(range(0, 64))
        self.axs[0][0].grid()

        # plot 45 degree line
        self.axs[0][0].plot([0,63], [0,63], c="black", lw=0.5)

        # settings (1)

        self.axs[0][1].set_xlabel("n")
        self.axs[0][1].set_ylabel("n+1")
        self.axs[0][1].set_xticks(range(0, 64))
        self.axs[0][1].set_yticks(range(0, 64))
        self.axs[0][1].grid()

        # plot 45 degree line
        self.axs[0][1].plot([0,63], [0,63], c="black", lw=0.5)
        
        # settings (2)

        self.axs[1][0].set_xlabel("y_n")
        self.axs[1][0].set_ylabel("x_n")
        self.axs[1][0].set_xticks(range(0, 64))
        self.axs[1][0].set_yticks(range(0, 64))
        self.axs[1][0].grid()

        # settings (3)

        self.axs[1][1].set_xlabel("y_n+1")
        self.axs[1][1].set_ylabel("x_n+1")
        self.axs[1][1].set_xticks(range(0, 64))
        self.axs[1][1].set_yticks(range(0, 64))
        self.axs[1][1].grid()


    def plot(self, x1, x2, y1, y2):
        
        x_min, x_max = min(min(x1), min(y1))-2, max(max(x1), max(y1))+2
        y_min, y_max = min(min(x2), min(y2))-2, max(max(x2), max(y2))+2
        
        
        # return map of x
        self.axs[0][0].set_xlim(x_min, x_max)
        self.axs[0][0].set_ylim(x_min, x_max)

        self.axs[0][0].scatter(x1, y1)
        
        # return map of y
        self.axs[0][1].set_xlim(y_min, y_max)
        self.axs[0][1].set_ylim(y_min, y_max)

        self.axs[0][1].scatter(x2, y2)

        # 2d retrun map of (x_n, y_n)
        self.axs[1][0].set_xlim(x_min, x_max)
        self.axs[1][0].set_ylim(y_min, y_max)

        self.axs[1][0].scatter(x1, x2)

        # 2d retrun map of (x_n+1, y_n+1)
        self.axs[1][1].set_xlim(x_min, x_max)
        self.axs[1][1].set_ylim(y_min, y_max)

        self.axs[1][1].scatter(y1, y2)

        plt.show()