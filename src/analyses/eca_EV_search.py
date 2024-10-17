# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 14:21:15 2023

@author: shirafujilab
"""

# Import necessary libraries
import csv
import numpy as np
import matplotlib.pyplot as plt
from src.method.eca.eca_basic import BSwitch

class EVSearch:
    def __init__(self):
        ##Get nullcline
        
        #Initializations
        #Bifurcation parameter
        self.S = 0.544
        self.Q1 = 0.54
        
        #parameter
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
            "s1":64,
            "s2":64,
            }
        
        for i, key in enumerate(PARAMETERS_2A):
            globals()[key] = PARAMETERS_2A[key]
        
        #self.fxx, self.fxy, self.fyx, self.fyy = self.nullcline()
        
        ##Get attractor
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
        BS1 = BSwitch(SYSPARA, 12, 12, 0, 0, 200,230, self.Q1, self.S)
        BS2 = BSwitch(SYSPARA, 24, 12, 0, 0, 200,230, self.Q1, self.S)
        
        _, self.BS1x, self.BS1y = BS1.Run() 
        _, self.BS2x, self.BS2y = BS2.Run()
        
        # Create a figure and axis
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        
        self.fxx, self.fxy, self.fyx, self.fyy = self.nullcline()
        self.heatmap()
        
    
    
    #離散version
    def fx(self, x, y):
        sgn = (1/tau1)*((b1*self.S+WE11*(x/s1)**2+WE12*(y/s2)**2)*(1-x/s1)\
            -(1+WI11*(x/s1)**2+WI12*(y/s2)**2)*x/s1)
        
        return np.sign(sgn)
    
    def fy(self, x, y):
        sgn = (1/tau2)*((b2*self.S+WE21*(x/s1)**2+WE22*(y/s2)**2)*(1-y/s2)\
            -(1+WI21*(x/s1)**2+WI22*(y/s2)**2)*y/s2)
        
        return np.sign(sgn)
    


       
    def nullcline(self):
        #Making Discrete  nullcline
        
        null_fxx = np.array([])
        null_fxy = np.array([])
        null_fyx = np.array([])
        null_fyy = np.array([])
        
        #loops
        for x in range(0,64,1):
            #initialize
            y=0
            check_fx_previous = check_fx_next = self.fx(x,y)
            check_fy_previous = check_fy_next = self.fy(x,y)
            
            #Start to determine nullcline
            for y in range(0,64,1):
                #calculation
                check_fx_next = self.fx(x, y)
                check_fy_next = self.fy(x, y)
                
                #Detection of varying sign(+, -)
                if check_fx_previous != check_fx_next:
                    null_fxx = np.append(null_fxx, x)
                    null_fxy = np.append(null_fxy, y-0.5)
                
                if check_fy_previous != check_fy_next:
                    null_fyx = np.append(null_fyx, x)
                    null_fyy = np.append(null_fyy, y-0.5)
        
                #update
                check_fx_previous = check_fx_next
                check_fy_previous = check_fy_next
                
        return null_fxx, null_fxy, null_fyx, null_fyy
                
                
        
        

    def heatmap(self):
        
        self.ax.scatter(self.fxx, self.fxy)
        self.ax.scatter(self.fyx, self.fyy)
        self.ax.scatter(self.BS1x, self.BS1y)
        self.ax.scatter(self.BS2x, self.BS2y)
        self.ax.set_title("Heatmap of Attractors")
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("y")
        
        # Add grid
        self.ax.grid(True, which='both', color='black', linewidth=0.5)
        
        plt.show()



if __name__ == "__main__":
    
    EVSearch()
    
    