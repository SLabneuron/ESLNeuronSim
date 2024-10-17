# -*- coding: utf-8 -*-
"""
Created on Fri Oct  6 09:21:02 2023

@author: shirafujilab
"""


import numpy as np
import csv

from src.method.eca.eca_basic import BSwitch

class Attractor:
    def __init__(self):
        #観測分
        self.x = np.arange(0,64,1)
        self.y = np.arange(0,64,1)
        #分岐パラメータ
        self.Q = 0.55
        self.S = 0.545
        
        #描画用配列
        #1: node1
        self.graphic_x1 = np.array([])
        self.graphic_y1 = np.array([])
        self.graphic_equ1 = np.array([])
        #2: node2
        self.graphic_x2 = np.array([])
        self.graphic_y2 = np.array([])
        self.graphic_equ2 = np.array([])
        #0: error detector
        self.graphic_x0 = np.array([])
        self.graphic_y0 = np.array([])
        self.graphic_equ0 = np.array([])
        
        
    
    def get_attractor_region(self):
        #init
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
        
        #loop (x, y, P, Q)
        for x in range(0,64,1):
            for y in range(0, 64, 1):
                for P in range(0, 48, 16):
                    for Q in range(0, 48,16):
                        BSwitch_instance = BSwitch(SYSPARA, x, y, P, Q, 200, 230, self.Q, self.S)
                        box0,  box1, box2 = BSwitch_instance.Run()
                        if box1[-1] == 63:#error
                            self.graphic_x0 = np.append(self.graphic_x0, x)
                            self.graphic_y0 = np.append(self.graphic_y0, y)
                            self.graphic_equ0 = np.append(self.graphic_equ0, box1[-1])
                        elif box1[-1] <= 20:#node1
                            self.graphic_x1 = np.append(self.graphic_x1, x)
                            self.graphic_y1 = np.append(self.graphic_y1, y)
                            self.graphic_equ1 = np.append(self.graphic_equ1, box1[-1])
                        else:#node2
                            self.graphic_x2 = np.append(self.graphic_x2, x)
                            self.graphic_y2 = np.append(self.graphic_y2, y)
                            self.graphic_equ2 = np.append(self.graphic_equ2, box1[-1])
                        
                print("process:",int((x*64+y)/(64*64)*100), "%")
        
        with open("eca_CASE1_Q055_S0545_node0.csv", "a") as f:
            writer = csv.writer(f)
            for i in range(len(self.graphic_x0)):
                writer.writerow([self.graphic_x0[i], 
                                 self.graphic_y0[i],
                                 self.graphic_equ0[i]])
        
        with open("eca_CASE1_Q055_S0545_node1.csv", "a") as f:
            writer = csv.writer(f)
            for i in range(len(self.graphic_x1)):
                writer.writerow([self.graphic_x1[i], 
                                 self.graphic_y1[i],
                                 self.graphic_equ1[i]])
        
        with open("eca_CASE1_Q055_S0545_node2.csv", "a") as f:
            writer = csv.writer(f)
            for i in range(len(self.graphic_x2)):
                writer.writerow([self.graphic_x2[i], 
                                 self.graphic_y2[i],
                                 self.graphic_equ2[i]])
                
        print("error:",len(self.graphic_x0), ",node1:", len(self.graphic_x1), ",node2:", len(self.graphic_x2))
                        
    
    

if __name__ == "__main__":
    #instance の作成
    main = Attractor()
    main.get_attractor_region()
    