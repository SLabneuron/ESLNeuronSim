# -*- coding: utf-8 -*-

"""

Created on: 2024-11-12
Updated on: 2025-12-26

@author: SLab

Contents:

    Phase Plain

"""

class GraphicPhasePlain:

    def __init__(self, params, model, ax):

        # clear plt
        ax.clear()

        # For ODE
        if model in ["forward euler", "rk4", "ode45"]:

            """ setting config of plt """

            # settings
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_xticks([0, 0.25, 0.5, 0.75, 1])
            ax.set_yticks([0, 0.25, 0.5, 0.75, 1])
            ax.set_xlabel(r"$y$")
            ax.set_ylabel(r"$x$")

        # For SynCA or ErCA
        elif model in ["ergodic CA", "synchronous CA", "rotated-LUT CA"]:

            """ setting config of plt """

            N_max = params["N"]

            # settings
            ax.set_xlim(0, N_max)
            ax.set_ylim(0, N_max)
            ax.set_xticks([0, N_max/4, N_max/4*2, N_max/4*3, N_max])
            ax.set_yticks([0, N_max/4, N_max/4*2, N_max/4*3, N_max])
            ax.set_xlabel(r"$Y$")
            ax.set_ylabel(r"$X$")

        self.ax = ax


    def plot(self, X_hist, Y_hist):
        self.ax.scatter(Y_hist, X_hist, marker="o", color="black", s=0.2)


    def plot_nullcline(self, model, params, x2, x1, y2, y1):

        """ plot nullcline """

        if model in ["forward euler", "rk4", "ode45"]:

            self.ax.scatter(x2, x1, marker=".", s=0.1)
            self.ax.scatter(y2, y1, marker=".", s=0.1)

        elif model in ["ergodic CA", "synchronous CA", "rotated-LUT CA"]:

            self.ax.scatter(x2*params["s1"], x1*params["s1"], marker=".", s=0.1)
            self.ax.scatter(y2*params["s2"], y1*params["s2"], marker=".", s=0.1)


    def plot_nodes(self, model, params, eset_x, eset_y, states):

        """ plot nodes (cross point of nullclines) """

        if model in ["forward euler", "rk4", "ode45"]:

            for i, _ in enumerate(eset_x):

                if states[i] == "sink":
                    self.ax.scatter(eset_y[i], eset_x[i], marker="o", c="red", s=20)

                elif states[i] == "source":
                    self.ax.scatter(eset_y[i], eset_x[i], marker="x", c="blue", s=20)

                elif states[i] == "saddle":
                    self.ax.scatter(eset_y[i], eset_x[i], marker="^", c="green", s=20)

        elif model in ["ergodic CA", "synchronous CA", "rotated-LUT CA"]:

            for i, _ in enumerate(eset_x):

                if states[i] == "sink":
                    self.ax.scatter(eset_y[i]*params["s2"], eset_x[i]*params["s1"], marker="o", c="red", s=20)

                elif states[i] == "source":
                    self.ax.scatter(eset_y[i]*params["s2"], eset_x[i]*params["s1"], marker="x", c="blue", s=20)

                elif states[i] == "saddle":
                    self.ax.scatter(eset_y[i]*params["s2"], eset_x[i]*params["s1"], marker="^", c="green", s=20)