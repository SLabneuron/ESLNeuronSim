# -*- coding: utf-8 -*-
"""
Created on: 2024-10-22
Updated on: 2024-10-22

@author: shirafujilab

Contents: 

"""

# import my library
import numpy as np


class CalODE:

    def __init__(self, params, init, bifp=None):

        # get params
        self.params = params

        # state variables
        self.x_previous = self.x_next = np.asarray(init["x"])
        self.y_previous = self.y_next = np.asarray(init["y"])

        if isinstance(bifp, None):
            self.Q = self.params["Q"]
            self.S = self.params["S"]
        else:
            self.Q = np.asarray(bifp["Q1"])
            self.S = np.asarray(bifp["S"])

        # time
        self.T = 0

        # registers
        self.t_hist = np.array([])
        self.x_hist = np.array([])
        self.y_hist = np.array([])


    def fx(self):
        return self.params["h"]*(1/self.params["tau1"])*((self.params["b1"]*self.params["S"]+self.params["WE11"]*self.x_previous**2+self.params["WE12"]*self.y_previous**2)*(1-self.x_previous)-(1+self.params["WI11"]*self.x_previous**2+self.params["WI12"]*self.y_previous**2)*self.x_previous)


    def fy(self):
        return self.params["h"]*(1/self.params["tau2"])*((self.params["b2"]*self.params["S"]+self.params["WE21"]*self.x_previous**2+self.params["WE22"]*self.y_previous**2)*(1-self.y_previous)-(1+self.params["WI21"]*self.x_previous**2+self.params["WI22"]*self.y_previous**2)*self.y_previous)


    def run(self):

        while self.T <= self.params["eT"]:

            # calculate
            self.x_next = self.x_previous + self.fx()
            self.y_next = self.y_previous + self.fy()

            # update variables and time
            self.x_previous = self.x_next
            self.y_previous = self.y_next
            self.T += self.params["h"]

            # store registers
            if self.T >= self.params["sT"]:
                self.t_hist = np.append(self.t_hist, self.T)
                self.x_hist = np.append(self.x_hist, self.x_previous)
                self.y_hist = np.append(self.y_hist, self.y_previous)

        return self.t_hist, self.x_hist, self.y_hist
