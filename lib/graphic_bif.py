# -*- coding: utf-8 -*-
"""
Created on Thur July 13 13:26:03 2023

@author: shirafujilab
"""

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

import datetime


class Graphic:
    def __init__(self, horizontal, vertical, max_hist, min_hist):
        #config
        self.horizontal = horizontal
        self.vertical = vertical
        
        #graphic_array
        self.max_hist = max_hist
        self.min_hist = min_hist
        
        
        

    def graphics(self):
        
        plt.figure(figsize=(8,5))
        
        plt.plot(self.horizontal, self.max_hist, "o", markersize = 0.8, color = "black")
        plt.plot(self.horizontal, self.min_hist, "o", markersize = 0.8, color = "black")
        plt.xlim(self.horizontal[0],self.horizontal[-1])
        plt.ylim(0, 0.8)

        plt.show()
        


