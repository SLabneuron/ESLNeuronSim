# -*- coding: utf-8 -*-

"""

Created on: 2024-11-12

@author: SLab

Contents:

    Phase Plain

"""

class GraphicPhasePlain:

    def __init__(self, master, axes):

        """ Set arguments """

        # get parameter class
        self.master = master

        # config plot area
        self.config_plot_area(axes)


    def config_plot_area(self, axes):

        mode = self.master.combos["model"].get()

        self.plt = axes

        # clear plt
        self.plt.clear()

        # For ODE
        if mode in ["fem", "rk4", "ode45"]:

            """ setting config of plt """

            # settings
            self.plt.set_xlim(0, 1)
            self.plt.set_ylim(0, 1)
            self.plt.set_xticks([0, 0.25, 0.5, 0.75, 1])
            self.plt.set_yticks([0, 0.25, 0.5, 0.75, 1])
            self.plt.set_xlabel(r"$y$")
            self.plt.set_ylabel(r"$x$")

        # For SynCA or ErCA
        elif mode in ["SynCA", "ErCA"]:

            """ setting config of plt """

            N_max = self.master.params["N"]

            # settings
            self.plt.set_xlim(0, N_max)
            self.plt.set_ylim(0, N_max)
            self.plt.set_xticks([0, N_max/4, N_max/4*2, N_max/4*3, N_max])
            self.plt.set_yticks([0, N_max/4, N_max/4*2, N_max/4*3, N_max])
            self.plt.set_xlabel(r"$Y$")
            self.plt.set_ylabel(r"$X$")


    def plot_result(self, X_hist, Y_hist):

        """ plot results (phase portrait) """

        self.plt.scatter(Y_hist, X_hist, marker="o", color="black", s=0.2)


    def plot_nullcline(self, x2, x1, y2, y1):

        """
        Summary:
            plot nullcline

        Arguments
            x2: fy
            x1: fx
            y2: gy
            y1: gx

        Note:
            f = dx/dt
            g = dy/dt

        """

        mode = self.master.combos["model"].get()

        # ode
        if mode in ["fem", "rk4", "ode45"]:

            # plot nullcline
            self.plt.scatter(x2, x1, marker=".", s=0.2)
            self.plt.scatter(y2, y1, marker=".", s=0.2)

        # SynCA, ErCA
        elif mode in ["SynCA", "ErCA"]:

            # plot nullcline
            self.plt.scatter(x2*self.master.params["s1"], x1*self.master.params["s1"], marker=".", s=0.2)
            self.plt.scatter(y2*self.master.params["s2"], y1*self.master.params["s2"], marker=".", s=0.2)


    def plot_nodes(self, eset_x, eset_y, states):
        """
        Summary:
            plot nodes (cross point of nullclines)
        
        """

        mode = self.master.combos["model"].get()

        # ode
        if mode in ["fem", "rk4", "ode45"]:

            for i, _ in enumerate(eset_x):

                # sink
                if states[i] == "sink":
                    self.plt.scatter(eset_y[i], eset_x[i], marker="o", c="red", s=20)

                # source
                elif states[i] == "source":
                    self.plt.scatter(eset_y[i], eset_x[i], marker="x", c="blue", s=20)

                # sink
                elif states[i] == "saddle":
                    self.plt.scatter(eset_y[i], eset_x[i], marker="^", c="green", s=20)

        # SynCA, ErCA
        elif mode in ["SynCA", "ErCA"]:

            for i, _ in enumerate(eset_x):

                # sink
                if states[i] == "sink":
                    self.plt.scatter(eset_y[i]*self.master.params["s2"], eset_x[i]*self.master.params["s1"], marker="o", c="red", s=20)

                # source
                elif states[i] == "source":
                    self.plt.scatter(eset_y[i]*self.master.params["s2"], eset_x[i]*self.master.params["s1"], marker="x", c="blue", s=20)

                # sink
                elif states[i] == "saddle":
                    self.plt.scatter(eset_y[i]*self.master.params["s2"], eset_x[i]*self.master.params["s1"], marker="^", c="green", s=20)

