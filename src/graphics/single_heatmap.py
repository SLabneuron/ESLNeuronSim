# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 15:52:57 2023

@author: shirafujilab
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from eca_basic import BSwitch

class HeatmapGenerator:
    def __init__(self, filenames):
        
        
        """Nullcline"""
        
        #Initializations
        #Bifurcation parameter
        self.S = 0.544
        self.Q1 = 0.5
        
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
        
        self.fxx, self.fxy, self.fyx, self.fyy = self.nullcline()
        
        
        
        """Fixed Points"""
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
        
        
        
        """For Graphic"""
        self.dfs = [pd.read_csv(filename, header=None) for filename in filenames]
        for df in self.dfs:
            df.columns = ['A', 'B', 'C']
        self.cmaps = {
            "Node 0": ListedColormap(['white', 'lightpink']),
            "Node 1": ListedColormap(['white', 'red']),
            "Node 2": ListedColormap(['white', 'blue']),
            "Overlap": ListedColormap(['white', 'purple'])
        }

    def plot_combined_heatmaps(self, titles):
        max_A = max(df['A'].max() for df in self.dfs)
        max_B = max(df['B'].max() for df in self.dfs)
        
        individual_data = []
        for df in self.dfs:
            data = np.zeros((int(max_B) + 1, int(max_A) + 1))
            for index, row in df.iterrows():
                data[int(row['B']), int(row['A'])] = 1
            individual_data.append(data)
        
        # Identify overlapping areas among all nodes
        overlap_mask = np.logical_and.reduce(individual_data)
        
        fig, ax = plt.subplots(figsize=(12, 10))

        # Plot individual heatmaps
        for data, title in zip(individual_data, titles):
            ax.imshow(data, origin='lower', cmap=self.cmaps[title], aspect='auto', alpha=0.7)
        
        # Plot overlap heatmap
        ax.imshow(overlap_mask, origin='lower', cmap=self.cmaps["Overlap"], aspect='auto', alpha=0.7)
        ax.scatter(self.BS1x, self.BS1y, color="red")
        ax.scatter(self.BS2x, self.BS2y, color="blue")
        ax.scatter(self.fxx, self.fxy, color="orange")
        ax.scatter(self.fyx, self.fyy, color="purple")
        ax.set_title('Combined Heatmaps')
        ax.set_xlim(0, 63)
        ax.set_ylim(0, 63)

        plt.tight_layout()
        
        # Add grid
        ax.grid(True, which='both', color='black', linewidth=0.5)
        
        plt.show()
        
    
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
                    null_fxy = np.append(null_fxy, y)
                
                if check_fy_previous != check_fy_next:
                    null_fyx = np.append(null_fyx, x)
                    null_fyy = np.append(null_fyy, y)
        
                #update
                check_fx_previous = check_fx_next
                check_fy_previous = check_fy_next
                
        return null_fxx, null_fxy, null_fyx, null_fyy
    
    


if __name__ == "__main__":
    # Instantiate and plot combined heatmaps
    heatmap_gen = HeatmapGenerator([
        "eca_CASE1_Q050_S0544_node0.csv", 
        "eca_CASE1_Q050_S0544_node1.csv", 
        "eca_CASE1_Q050_S0544_node2.csv"
    ])
    heatmap_gen.plot_combined_heatmaps(["Node 0", "Node 1", "Node 2"])
