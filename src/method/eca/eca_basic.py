# -*- coding: utf-8 -*-
"""
Created on Sun Jul 23 16:03:28 2023

@author: shirafujilab
"""

import math
import numpy as np
from lib.graphic_basic import Graphic


class BSwitch:
    def __init__(self, SYSPARA, init_x, init_y, init_P, init_Q, sTime, eTime, Q1, S):
        #state variables
        self.x_previous = self.x_next = init_x
        self.y_previous = self.y_next = init_y
        self.P_previous = self.P_next = init_P
        self.Q_previous = self.Q_next = init_Q
        self.phx_previous = self.phx_next = 0
        self.phy_previous = self.phy_next = 0
        
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
        
        for i, key in enumerate(SYSPARA):
            globals()[key] = SYSPARA[key]
            
        self.alpha=0.05
        self.beta=0.05
        
        self.t_hist = np.array([])
        self.x_hist = np.array([])
        self.y_hist = np.array([])
        
        #print(1/Tx, 1/Ty)
        
        
           
    def fx(self):
        return (1/tau1)*((b1*self.S+WE11*(self.x_previous/s1)**2+WE12*(self.y_previous/s2)**2)*(1-self.x_previous/s1)\
            -(1+WI11*(self.x_previous/s1)**2+WI12*(self.y_previous/s2)**2)*self.x_previous/s1)        

    def dde_X(self):
        #The calculation of internal f
        Fin = self.fx()
        
        #Return Internal function dde_F
        #Exceptional proceeder (1/0)
        if Fin ==0: return (M-1)
        #Return positive threthold value
        elif math.floor(self.alpha/Fin*(Tc/Tx))>=M-1: return (M-1)
        #Return negetive threthold value
        elif math.ceil(self.alpha/Fin*(Tc/Tx))<=-(M-1): return -(M-1)
        #Return value
        else: return int(self.alpha/Fin*(Tc/Tx))
    
    def fy(self):
        return (1/tau2)*((b2*self.S+WE21*(self.x_previous/s1)**2+WE22*(self.y_previous/s2)**2)*(1-self.y_previous/s2)\
            -(1+WI21*(self.x_previous/s1)**2+WI22*(self.y_previous/s2)**2)*self.y_previous/s2)
    
    def dde_Y(self):
        #The calculation of internal f
        Fin = self.fy()
        
        #Return Internal function dde_F
        #Exceptional proceeder (1/0)
        if Fin ==0: return (M-1)
        #Return positive threthold value
        elif math.floor(self.beta/Fin*(Tc/Ty))>=M-1: return (M-1)
        #Return negetive threthold value
        elif math.ceil(self.beta/Fin*(Tc/Ty))<=-(M-1): return -(M-1)
        #Return value
        else: return int(self.beta/Fin*(Tc/Ty))
    
    def time_evolution(self):
        #time evolution
        self.T += Tc
        
        #calculation of switch signals phx, phy
        self.phx_next += Tc/Tx
        self.phy_next += Tc/Ty
        
        #recalculation of switch signals phx, phy
        if self.phx_next >= 1: self.phx_next -= 1
        if self.phy_next >= 1: self.phy_next -= 1    
        
        #judge for switch signals phx, phy
        self.Cx = 1 if self.phx_next >= (1-Tc/Tx) else 0
        self.Cy = 1 if self.phy_next >= (1-Tc/Ty) else 0


    def Run(self):
        #time evolutions
        while self.T <= self.eT:
            #print(self.T, self.x_previous, self.y_previous)
            self.time_evolution()
            #judge for switch signal swx
            if (self.Cx):
                
                #caluculation
                Fx = self.dde_X()
                #print(Fx)
                
                #transition of P
                self.P_next = self.P_previous + 1 if self.P_previous < abs(Fx) else 0
                #transition of X
                if self.P_previous >= abs(Fx):
                    if Fx >=0 and self.x_previous < N-1: self.x_next = self.x_previous + 1
                    elif Fx <0 and self.x_previous > 0: self.x_next = self.x_previous - 1
            
            #judge for switch signal swy
            if (self.Cy):
                #caluculation
                Fy = self.dde_Y()
                #print(Fy)
                
                #transition of Q
                self.Q_next = self.Q_previous + 1 if self.Q_previous < abs(Fy) else 0
                #transition of Y
                if self.Q_previous >= abs(Fy):
                    if Fy >=0 and self.y_previous < N-1: self.y_next = self.y_previous + 1
                    elif Fy <0 and self.y_previous > 0: self.y_next = self.y_previous - 1
            
            
            #update
            self.x_previous = self.x_next
            self.y_previous = self.y_next
            self.P_previous = self.P_next
            self.Q_previous = self.Q_next
            
            if self.T >= self.sT:
                self.t_hist = np.append(self.t_hist, self.T)
                self.x_hist = np.append(self.x_hist, self.x_previous)
                self.y_hist = np.append(self.y_hist, self.y_previous)
            
            #ERROR
            if (self.x_next == 63 or self.y_next == 63):
                self.x_hist = [63]
                self.y_hist = [63]
                break
                
                
        return self.t_hist, self.x_hist, self.y_hist
            
            
    
    
if __name__ == "__main__":
    s=6
    SYSPARA ={
        "N":2**s,
        "M":2**(s),
        "s1":2**s,
        "s2":2**s,
        "Tc":0.01,
        "Tx":0.01*(1.713**(1/2)),
        "Ty":0.01*(2.313**(1/2)),
        }
    
    #sim
    main = BSwitch(SYSPARA, 19, 30, 32, 0, 0, 10, 0.50, 0.544)
    t_hist, x_hist, y_hist = main.Run()
    #graphic
    figure = Graphic(t_hist, [10,40], x_hist, y_hist)
    figure.graphics()
    
        
        
        