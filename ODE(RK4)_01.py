# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 20:24:45 2023

@author: shirafujilab
"""

import math
import numpy as np
from lib.graphic_basic import Graphic


class BSwitch:
    def __init__(self, init_x, init_y, sTime, eTime):
        #state variables
        self.x_previous = self.x_next = init_x
        self.y_previous = self.y_next = init_x
        
        #Time evolution
        self.T = 0
        self.sT = sTime
        self.eT = eTime
        self.h = 0.01
        
        #bifurcation paramters
        self.Q1 = 0.75
        self.S = 0.45
        
        #noise
        #self.sigma1 = 0
        #self.sigma2 = 0
        
        #Paramter Sets
        #if WEij != 0 WIij=0 reciprocally
        #pattern 2(a)
        PARAMETERS_2A = {
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
    
    def k1(self):
        return self.fx(), self.fy()
    
    def k2(self, k1x, k1y):
        self.x_previous += self.h/2 * k1x
        self.y_previous += self.h/2 * k1y
        return self.fx(), self.fy()
    
    def k3(self, k2x, k2y):
        self.x_previous += self.h/2 * k2x
        self.y_previous += self.h/2 * k2y
        return self.fx(), self.fy()
    
    def k4(self, k3x, k3y):
        self.x_previous += self.h * k3x
        self.y_previous += self.h * k3y
        return self.fx(), self.fy()

    def Run(self):
        #time evolutions
        while self.T <= self.eT:
            print(self.T, self.x_previous, self.y_previous)
            self.T += self.h
            
            x_temp, y_temp = self.x_previous, self.y_previous
            
            k1x, k1y = self.k1()
            k2x, k2y = self.k2(k1x, k1y)
            k3x, k3y = self.k3(k2x, k2y)
            k4x, k4y = self.k4(k3x, k3y)
            
            self.x_next = x_temp + self.h/6 * (k1x + 2*k2x + 2*k3x + k4x)
            self.y_next = y_temp + self.h/6 * (k1y + 2*k2y + 2*k3y + k4y)
            
            
            #update
            self.x_previous = self.x_next
            self.y_previous = self.y_next
            
            if self.T >= self.eT*(4/5):
                self.t_hist = np.append(self.t_hist, self.T)
                self.x_hist = np.append(self.x_hist, self.x_previous)
                self.y_hist = np.append(self.y_hist, self.y_previous)
                
        return self.t_hist, self.x_hist, self.y_hist
            
            
    
    
if __name__ == "__main__":
    #sim
    main = BSwitch(0.3,0.6, 500,1000)
    t_hist, x_hist, y_hist = main.Run()
    #graphic
    figure = Graphic(t_hist, [0,1], x_hist, y_hist)
    figure.graphics()
    
        
        
        