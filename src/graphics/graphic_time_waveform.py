# -*- coding: utf-8 -*-

"""

Created on: 2024-11-11
Updated on: 2025-12-26

@author: SLab

Contents:

    Time waveform

"""

class GraphicTimeWaveform:

    def __init__(self, params, model, ax1, ax2, ax3):

        # clear plt
        ax1.clear(); ax2.clear(); ax3.clear()

        # For ODE
        if model in ["ode"]:

            """ setting config of plt1 """
            # settings
            ax1.set_xlim(params["sT"], params["eT"])
            ax1.set_ylabel(r"$x$")

            """ setting config of plt2 """

            # settings
            ax2.set_xlim(params["sT"], params["eT"])
            ax2.set_xlabel(r"$\mathrm{Time} \;\; t$")
            ax2.set_ylabel(r"$y$")

            """ setting config of plt3 """

            # settings
            ax2.set_xlim(params["sT"], params["eT"])
            ax2.set_xlabel(r"$\mathrm{Time} \;\; t$")
            ax2.set_ylabel(r"$z$")

        # For SynCA or ErCA
        elif model in ["esl"]:

            """ setting config of plt1 """

            N1 = params["N1"]
            N2 = params["N2"]
            N3 = params["N3"]

            # settings
            ax1.set_xlim(params["sT"], params["eT"])
            ax1.set_ylim(0, N1+2)
            ax1.set_yticks([0, N1/4, N1/4*2, N1/4*3, N1])
            ax1.set_ylabel(r"$X$")

            """ setting config of plt2 """

            # settings
            ax2.set_xlim(params["sT"], params["eT"])
            ax2.set_ylim(0, N2+2)
            ax2.set_yticks([0, N2/4, N2/4*2, N2/4*3, N2])
            ax2.set_xlabel(r"$\mathrm{Time} \;\; t$")
            ax2.set_ylabel(r"$Y$")

            """ setting config of plt3 """

            # settings
            ax3.set_xlim(params["sT"], params["eT"])
            ax3.set_ylim(0, N3+2)
            ax3.set_yticks([0, N3/4, N3/4*2, N3/4*3, N3])
            ax3.set_xlabel(r"$\mathrm{Time} \;\; t$")
            ax3.set_ylabel(r"$Z$")

        self.ax1 = ax1
        self.ax2 = ax2
        self.ax3 = ax3


    def plot(self, T_hist, X_hist, Y_hist, Z_hist):

        self.ax1.plot(T_hist, X_hist, 'k', linewidth = 0.5)
        self.ax2.plot(T_hist, Y_hist, 'k', linewidth = 0.5)
        self.ax3.plot(T_hist, Z_hist, 'k', linewidth = 0.5)

