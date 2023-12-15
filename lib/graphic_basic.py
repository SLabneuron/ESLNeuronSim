# -*- coding: utf-8 -*-
"""
Created on Thur July 13 13:26:03 2023

@author: shirafujilab
"""

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

import datetime


class Graphic:
    def __init__(self, horizontal, vertical, x_hist, y_hist):
        #Declare Array
        self.h = horizontal
        self.v = vertical
        self.x_hist = x_hist
        self.y_hist = y_hist
        
        #print(self.h)
        
        
        
        

    def graphics(self):
        
        plt.figure(figsize=(8,5))
        gs=gridspec.GridSpec(2,2)   
        
        
        plt.subplot(gs[0,0])
        plt.plot(self.h, self.x_hist, "o", markersize=0.8, color="black")
        plt.xlim(int(self.h[0]), int(self.h[-1]))
        plt.ylim(self.v[0], self.v[-1])
        
        plt.subplot(gs[1,0])
        plt.plot(self.h, self.y_hist, "o", markersize=0.8, color="black")
        plt.xlim(int(self.h[0]), int(self.h[-1]))
        plt.ylim(self.v[0], self.v[-1])
        
        plt.subplot(gs[:,1])
        plt.plot(self.x_hist, self.y_hist, "o", markersize=0.8, color="black")
        plt.xlim(self.v[0], self.v[-1])
        plt.ylim(self.v[0], self.v[-1])
        
        plt.suptitle(str(datetime.datetime.now()))
        
        plt.show()
        
        
if __name__ == "__main__":
    #Graphic(T_hist, )
    main = Graphic([0, 1, 2, 3, 4], [3, 4, 3, 4, 3], [7, 8, 9, 8, 7], 11, [0, 10])
    main.graphic()
    
    

    