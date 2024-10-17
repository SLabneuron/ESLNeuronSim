# -*- coding: utf-8 -*-
"""
Created on Thu Oct  5 10:46:51 2023

@author: shirafujilab

Biochemical Switch
"""

#Libralies
import numpy as np
import csv

#Inputs
from ode_basic import BSwitch as ode
from eca_basic import BSwitch as eca

#Outputs
from lib.graphic_bif import Graphic


class BIF:
    def __init__(self, mode):
        #mode = 0 ->ode
        if mode == 0:
            #観測点
            self.x = np.array([0.2,0.4,0.6])
            self.y = np.array([0.2,0.4,0.6])
            #分岐パラメータ
            self.Q = 0.50
            self.S_WIDTH =  np.arange(0.5, 0.51, 0.001)

            #描画用配列
            self.S_hist = np.array([])
            self.max_hist = np.array([])
            self.min_hist = np.array([])

        #mode = 1 ->eca
        if mode == 1:
            #set parameter
            k=6
            self.SYSPARA ={
                "N":2**k,
                "M":2**(k),
                "s1":2**k,
                "s2":2**k,
                "Tc":0.01,
                "Tx":0.01*(1.713**(1/2)),
                "Ty":0.01*(2.313**(1/2)),
                }

            #観測点
            self.x = np.array([12,24,36])
            self.y = np.array([12,24,36])
            #分岐パラメータ
            self.Q = 0.54
            self.S_WIDTH =  np.arange(0.5, 0.6, 0.001)

            #描画用配列
            self.S_hist = np.array([])
            self.max_hist = np.array([])
            self.min_hist = np.array([])


    def bif_ode(self):
        """This function gets ode bifurcation diagram."""
        for S in self.S_WIDTH:
            for x in self.x:
                for y in self.y:
                    #execute a basic
                    ode_instance = ode(x, y, 780, 800, self.Q, S)
                    box0, box1, box2 = ode_instance.Run()
                    #received box0 = time, box1 = x, and box2 = y
                    self.S_hist = np.append(self.S_hist, S)
                    self.max_hist = np.append(self.max_hist, max(box1))
                    self.min_hist = np.append(self.min_hist, min(box1))

        return self.S_hist, self.max_hist, self.min_hist


    def bif_eca(self):
        """This function gets eca bifurcation diagram."""
        for S in self.S_WIDTH:
            for x in self.x:
                for y in self.y:
                    #execute a basic
                    eca_instance = eca(self.SYSPARA,x, y, 0, 0, 200, 230, self.Q, S)
                    box0, box1, box2 = eca_instance.Run()
                    #received box0 = time, box1 = x, and box2 = y
                    self.S_hist = np.append(self.S_hist, S)
                    self.max_hist = np.append(self.max_hist, max(box1))
                    self.min_hist = np.append(self.min_hist, min(box1))

        return self.S_hist, self.max_hist, self.min_hist



if __name__ == "__main__":

    """test1"""
    # 0 = ode, 1 = eca
    main = BIF(0)


    #S: bifurcation parameter, max: max ox x., min: min of x
    S, valmax, valmin = main.bif_ode()

    #Writing
    with open("test1.csv", "a", newline="") as f:
        writer = csv.writer(f)
        for i in range(len(S)):
            writer.writerow([S[i], valmax[i], valmin[i]])

    """test2"""
    # 0 = ode, 1 = eca
    main = BIF(1)


    #S: bifurcation parameter, max: max ox x., min: min of x
    S, valmax, valmin = main.bif_eca()

    #Writing
    with open("test2.csv", "a", newline="") as f:
        writer = csv.writer(f)
        for i in range(len(S)):
            writer.writerow([S[i], valmax[i], valmin[i]])


    #Graphic
    #G_instance = Graphic(S, [0,0.8], valmax, valmin)
    #G_instance.graphics()