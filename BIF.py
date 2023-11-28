# -*- coding: utf-8 -*-
"""
Created on Thu Oct  5 10:46:51 2023

@author: shirafujilab

Biochemical Switch
"""

import numpy as np
import csv
from ode_basic import BSwitch
#from eca_basic import BSwitch
from lib.graphic_bif import Graphic
#BSwitch(self, init_x, init_y, sTime, eTime, Q1, S)


class BIF:
    def __init__(self):
        
        mode = 0
        
        if mode == 0:#ode
            #観測点
            self.x = np.array([0.2,0.4,0.6])
            self.y = np.array([0.2,0.4,0.6])
            #分岐パラメータ
            self.Q = 0.50                           #分岐図観測用
            self.S_WIDTH =  np.arange(0.5, 0.6, 0.001)  #分岐図観測範囲
        
            #描画用配列
            self.graphic_S = np.array([])
            self.graphic_sink_max = np.array([])
            self.graphic_sink_min = np.array([])
        
        
        
        
        if mode == 1:#eca
            #観測点
            self.x = np.array([12,24,36])
            self.y = np.array([12,24,36])
        
        
            #分岐パラメータ
            self.Q = 0.54                           #分岐図観測用
            self.S_WIDTH =  np.arange(0.5, 0.6, 0.001)  #分岐図観測範囲
            
            #描画用配列
            self.graphic_S = np.array([])
            self.graphic_sink_max = np.array([])
            self.graphic_sink_min = np.array([])
        
        
     
    def get_bif(self):        
        for S in self.S_WIDTH:
            for x in self.x:
                for y in self.y:
                    BSwtich_instance = BSwitch(x, y, 780, 800, self.Q, S)
                    box0, box1, box2 = BSwtich_instance.Run()
                    self.graphic_S = np.append(self.graphic_S, S)
                    self.graphic_sink_max = np.append(self.graphic_sink_max, max(box1))
                    self.graphic_sink_min = np.append(self.graphic_sink_min, min(box1))
        
        return self.graphic_S, self.graphic_sink_max, self.graphic_sink_min
    
    
    def get_bif_eca(self):
        k=6
        SYSPARA ={
            "N":2**k,
            "M":2**(k),
            "s1":2**k,
            "s2":2**k,
            "Tc":0.01,
            "Tx":0.01*(1.713**(1/2)),
            "Ty":0.01*(2.313**(1/2)),
            }
        
        for S in self.S_WIDTH:
            for x in self.x:
                for y in self.y:

                    
                    BSwtich_instance = BSwitch(SYSPARA,x, y, 0, 0, 200, 230, self.Q, S)
                    box0, box1, box2 = BSwtich_instance.Run()
                    self.graphic_S = np.append(self.graphic_S, S)
                    self.graphic_sink_max = np.append(self.graphic_sink_max, max(box1))
                    self.graphic_sink_min = np.append(self.graphic_sink_min, min(box1))
        
        return self.graphic_S, self.graphic_sink_max, self.graphic_sink_min
                    
        
        
        
        

if __name__ == "__main__":
    main = BIF()
    S, sink_max, sink_min = main.get_bif()
    with open("ode_CASE1_Q050.csv", "a", newline="") as f:
        writer = csv.writer(f)
        for i in range(len(S)):
            writer.writerow([S[i], sink_max[i], sink_min[i]]) 
    print(S)
    #Graphic
    G_instance = Graphic(S, [0,0.8], sink_max, sink_min)
    G_instance.graphics()