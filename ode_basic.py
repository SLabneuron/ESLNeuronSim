# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 10:02:00 2023

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
        
        
           
    def fx(self):
        return self.h*(1/tau1)*((b1*self.S+WE11*self.x_previous**2+WE12*self.y_previous**2)*(1-self.x_previous)\
            -(1+WI11*self.x_previous**2+WI12*self.y_previous**2)*self.x_previous)        

       
    def fy(self):
        return self.h*(1/tau2)*((b2*self.S+WE21*self.x_previous**2+WE22*self.y_previous**2)*(1-self.y_previous)\
            -(1+WI21*self.x_previous**2+WI22*self.y_previous**2)*self.y_previous)
    


    def Run(self):
        #time evolutions
        while self.T <= self.eT:
            #print(self.T, self.x_previous, self.y_previous)
            self.T += self.h
            self.x_next = self.x_previous + self.fx()
            self.y_next = self.y_previous + self.fy()
            
            
            #update
            self.x_previous = self.x_next
            self.y_previous = self.y_next
            
            if self.T >= self.sT:
                self.t_hist = np.append(self.t_hist, self.T)
                self.x_hist = np.append(self.x_hist, self.x_previous)
                self.y_hist = np.append(self.y_hist, self.y_previous)
                
        return self.t_hist, self.x_hist, self.y_hist
            
            
    
    
if __name__ == "__main__":
    #sim
    main = BSwitch(0.3,0.6, 0,100, 0.5, 0.51)
    t_hist, x_hist, y_hist = main.Run()
    #graphic
    figure = Graphic(t_hist, [0,0.8], x_hist, y_hist)
    figure.graphics()
    
        
        
        