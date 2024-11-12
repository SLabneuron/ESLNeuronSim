# -*- coding: utf-8 -*-

"""

Created on: 2024-11-11

@author: SLab

Contents:

    Time waveform

"""

class GraphicTimeWaveform:

    def __init__(self, master):

        """ Set arguments """

        # get parameter class
        self.master = master

        # config plot area
        self.config_plot_area()


    def config_plot_area(self):

        mode = self.master.combos["model"].get()

        self.plt1 = self.master.axes["waveform1"]
        self.plt2 = self.master.axes["waveform2"]

        # clear plt
        self.plt1.clear()
        self.plt2.clear()

        # For ODE
        if mode in ["fem", "rk4", "ode45"]:

            """ setting config of plt1 """

            # settings
            self.plt1.set_xlim(self.master.params["sT"], self.master.params["eT"])
            self.plt1.set_ylim(0, 1)
            self.plt1.set_ylabel("x")

            """ setting config of plt2 """

            # settings
            self.plt2.set_xlim(self.master.params["sT"], self.master.params["eT"])
            self.plt2.set_ylim(0, 1)
            self.plt2.set_xlabel("Time t")
            self.plt2.set_ylabel("y")

        # For SynCA or ErCA
        elif mode in ["SynCA", "ErCA"]:

            """ setting config of plt1 """

            # settings
            self.plt1.set_xlim(self.master.params["sT"], self.master.params["eT"])
            self.plt1.set_ylim(0, self.master.params["N"])
            self.plt1.set_ylabel("X")

            """ setting config of plt2 """

            # settings
            self.plt2.set_xlim(self.master.params["sT"], self.master.params["eT"])
            self.plt2.set_ylim(0, self.master.params["N"])
            self.plt2.set_xlabel("Time t")
            self.plt2.set_ylabel("Y")


    def plot(self, T_hist, X_hist, Y_hist):

        self.plt1.scatter(T_hist, X_hist, marker=".", s=0.5)
        self.plt2.scatter(T_hist, Y_hist, marker=".", s=0.5)

