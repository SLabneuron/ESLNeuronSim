# -*- coding: utf-8 -*-

"""

Created on: 2024-11-11
Updated on: 2025-12-26

@author: SLab

Contents:

    Time waveform

"""

class GraphicTimeWaveform:

    def __init__(self, params, model, ax1, ax2):

        # clear plt
        ax1.clear(); ax2.clear()

        # For ODE
        if model in ["forward euler", "rk4", "ode45"]:

            """ setting config of plt1 """
            # settings
            ax1.set_xlim(params["sT"], params["eT"])
            ax1.set_ylim(0, 1)
            ax1.set_yticks([0, 0.25, 0.5, 0.75, 1])
            ax1.set_ylabel(r"$x$")

            """ setting config of plt2 """

            # settings
            ax2.set_xlim(params["sT"], params["eT"])
            ax2.set_ylim(0, 1)
            ax2.set_yticks([0, 0.25, 0.5, 0.75, 1])
            ax2.set_xlabel(r"$\mathrm{Time} \;\; t$")
            ax2.set_ylabel(r"$y$")

        # For SynCA or ErCA
        elif model in ["ergodic CA", "synchronous CA", "rotated-LUT CA"]:

            """ setting config of plt1 """

            N_max = params["N"]

            # settings
            ax1.set_xlim(params["sT"], params["eT"])
            ax1.set_ylim(0, N_max)
            ax1.set_yticks([0, N_max/4, N_max/4*2, N_max/4*3, N_max])
            ax1.set_ylabel(r"$X$")

            """ setting config of plt2 """

            # settings
            ax2.set_xlim(params["sT"], params["eT"])
            ax2.set_ylim(0, N_max)
            ax2.set_yticks([0, N_max/4, N_max/4*2, N_max/4*3, N_max])
            ax2.set_xlabel(r"$\mathrm{Time} \;\; t$")
            ax2.set_ylabel(r"$Y$")

        self.ax1 = ax1
        self.ax2 = ax2


    def plot(self, T_hist, X_hist, Y_hist):

        self.ax1.scatter(T_hist, X_hist, marker="o", color="black" ,s=0.2)
        self.ax2.scatter(T_hist, Y_hist, marker="o", color="black" ,s=0.2)

