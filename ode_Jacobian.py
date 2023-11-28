# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 15:30:25 2023

@author: shirafujilab
"""


import math
import numpy as np
from lib.graphic_basic import Graphic


class BSwitch:
    def __init__(self, init_x, init_y, sTime, eTime, Q1, S):
        #state variables
        self.x_previous = self.x_next = init_x
        self.y_previous = self.y_next = init_y
        
        #Time evolution
        self.T = 0
        self.sT = sTime
        self.eT = eTime
        self.h = 0.01
        
        #bifurcation paramters
        self.Q1 = Q1
        self.S = S
        
        #noise
        #self.sigma1 = 0
        #self.sigma2 = 0
        
        #Paramter Sets
        #if WEij != 0 WIij=0 reciprocally
        #pattern 2(a)
        PARAMETERS_2A = {
            "tau1":1, 
            "tau2":1,
            "b1":0.13*(1+self.Q1), 
            "b2":0,
            "WE11":3.9,
            "WE12":0,
            "WE21":3.0,
            "WE22":3.0,
            "WI11":0,
            "WI12":0.5*self.Q1,
            "WI21":0,
            "WI22":0,
            }
        
        PARAMETERS_2B = {
            "tau1":1, 
            "tau2":10,
            "b1":0.13*(1+self.Q1), 
            "b2":0,
            "WE11":3.9,
            "WE12":0,
            "WE21":3.0,
            "WE22":3.0,
            "WI11":0,
            "WI12":0.5*self.Q1,
            "WI21":0,
            "WI22":0,
            }
        
        for i, key in enumerate(PARAMETERS_2A):
            globals()[key] = PARAMETERS_2A[key]
        
        self.t_hist = np.array([])
        self.x_hist = np.array([])
        self.y_hist = np.array([])
        
        
           
    def fx(self, x, y):
        return (1/tau1)*((b1*self.S+WE11*x**2+WE12*y**2)*(1-x)\
            -(1+WI11*x**2+WI12*y**2)*x)

       
    def fy(self, x, y):
        return (1/tau2)*((b2*self.S+WE21*x**2+WE22*y**2)*(1-y)\
            -(1+WI21*x**2+WI22*y**2)*y)
    


    def Run(self):
        #time evolutions
        while self.T <= self.eT:
            #print(self.T, self.x_previous, self.y_previous)
            self.T += self.h
            self.x_next = self.x_previous + self.fx(self.x_previous, self.y_previous)
            self.y_next = self.y_previous + self.fy(self.x_previous, self.y_previous)
            
            
            #update
            self.x_previous = self.x_next
            self.y_previous = self.y_next
            
            if self.T >= self.sT:
                self.t_hist = np.append(self.t_hist, self.T)
                self.x_hist = np.append(self.x_hist, self.x_previous)
                self.y_hist = np.append(self.y_hist, self.y_previous)
                
        return np.average(self.x_hist), np.average(self.y_hist)
            
    
    def points(self):
        i=0
        points_hist_x = []
        points_hist_y = []
        for x in range(2000, 4000, 1):
            for y in range(4000, 6000, 1):
                x_in = x/10000
                y_in = y/10000
                if ((abs(self.fx(x_in, y_in) - self.fy(x_in, y_in))<=0.000001)):
                    points_hist_x.append(x/1000)
                    points_hist_y.append(y/1000)
                
                i+=1 
                print("process: ",i/2000/2000*100, "%")
        return points_hist_x, points_hist_y
    
    
if __name__ == "__main__":
    #sim
    main = BSwitch(0.17,0.4, 150,200, 0.54, 0.545)
    
    x_equ, y_equ = main.Run()    
    print(x_equ, y_equ)
    
    p_x, p_y = main.points()
    print(p_x, p_y)
    print(len(p_x), len(p_y))
    
    #graphic
    #figure = Graphic(t_hist, [0,0.8], x_hist, y_hist)
    #figure.graphics()
    
        