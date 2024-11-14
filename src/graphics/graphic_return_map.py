# -*- coding: utf-8 -*-

"""

Created on: 2024-11-12

@author: SLab

Contents:

    Return Map

"""

# import standard library
import numpy as np

class GraphicSwitchPhase:

    def __init__(self, master):

        """ Set arguments """

        # get parameter class
        self.master = master

        # config plot area
        self.config_plot_area()


    def config_plot_area(self):

        self.plt = self.master.axes["phase of switch"]

        # clear plt
        self.plt.clear()

        # settings
        self.plt.set_xlim(0, 1)
        self.plt.set_ylim(0, 1)
        self.plt.set_xlabel("n")
        self.plt.set_ylabel("n+1")

        # plot 45 degree line
        self.plt.plot([0,1], [0,1], c="black", lw=0.5)


    def plot_return_map(self, phase):

        """ plot return map """

        # phase plot
        n_pre = phase[:-1]
        n_next = phase[1:]

        self.plt.scatter(n_pre, n_next, marker=".", s=0.5)

        # transit
        transit_x = np.empty((n_pre.size, n_next.size,), dtype=n_pre.dtype)
        transit_x[0::2] = n_pre
        transit_x[1::2] = n_next

        transit_y  = np.empty_like(transit_x)
        transit_y[0::2] = n_next
        transit_y[1::2] = n_next

        self.plt.plot(transit_x, transit_y, c="gray", lw=0.3)
