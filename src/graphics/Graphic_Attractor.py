# -*- coding: utf-8 -*-
"""
Created on Sat Oct  7 11:49:26 2023

@author: shirafujilab
"""

# Import necessary libraries
import csv
import numpy as np
import matplotlib.pyplot as plt
from eca_basic import BSwitch

class Graphic_attractor:
    def __init__(self, files):
        ##Get nullcline

        #Initializations
        #Bifurcation parameter
        self.S = 0.545
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

        self.fxx, self.fxy, self.fyx, self.fyy = self.nullcline()

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

        #Normalized
        self.BS1x = self.BS1x
        self.BS1y = self.BS1y
        self.BS2x = self.BS2x
        self.BS2y = self.BS2y



        ##Get attractor
        self.data = {"node0": [], "node1": [], "node2": []}

        # Create a figure and axis
        self.fig, self.ax = plt.subplots(figsize=(10, 10))

        # Load data from the provided CSV files
        for filename in files:
            node_name = filename.split("_")[-1].split(".")[0]
            with open(filename, "r") as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) != 3:
                        continue  # Skip rows that don't have 3 columns
                    x, y, _ = row
                    # Scale the x and y values to be between 0 and 1
                    x_scaled = float(x) / 64
                    y_scaled = float(y) / 64
                    self.data[node_name].append((x_scaled, y_scaled))

        # Generate the heatmap using the loaded data
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
                    null_fxy = np.append(null_fxy, y)

                if check_fy_previous != check_fy_next:
                    null_fyx = np.append(null_fyx, x)
                    null_fyy = np.append(null_fyy, y)

                #update
                check_fx_previous = check_fx_next
                check_fy_previous = check_fy_next

        return null_fxx, null_fxy, null_fyx, null_fyy





    def heatmap(self):
        # Define colors for each attractor
        colors = {"node0": 0, "node1": 1, "node2": 2}
        custom_colors = ["white", "yellow", "lightgreen"]
        color_map = plt.matplotlib.colors.ListedColormap(custom_colors)

        # Create a matrix based on the x, y range
        all_data = sum(self.data.values(), [])
        xs, ys = zip(*all_data)

        matrix_size = 64
        matrix = np.zeros((matrix_size, matrix_size))

        for node, values in self.data.items():
            for x, y in values:
                x_idx = int(x * matrix_size)  # map scaled x to [0, 64)
                y_idx = int(y * matrix_size)  # map scaled y to [0, 64)
                matrix[y_idx, x_idx] = colors[node]

        # Display the heatmap on the provided axis
        self.ax.imshow(matrix, cmap=color_map, origin='lower', extent=[0, 64, 0, 64])

        self.ax.scatter(self.BS1x, self.BS1y, color="red")
        self.ax.scatter(self.BS2x, self.BS2y, color="blue")
        self.ax.scatter(self.fxx, self.fxy, color="orange")
        self.ax.scatter(self.fyx, self.fyy, color="purple")

        self.ax.set_title("Heatmap of Attractors")
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("y")

        # Add grid
        self.ax.grid(True, which='both', color='black', linewidth=0.5)

        plt.show()



if __name__ == "__main__":
    files = [
        "eca_CASE1_Q054_S0545_node0.csv",
        "eca_CASE1_Q054_S0545_node1.csv",
        "eca_CASE1_Q054_S0545_node2.csv"
    ]
    Graphic_attractor(files)
