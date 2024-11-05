# -*- coding: utf-8 -*-
"""
Created on: 2024-10-24
Updated on: 2024-11-05

@author: shirafujilab

Contents:
    - calculate nullcline (Optimized)
    - calculate cross point
"""

import numpy as np
from scipy.optimize import root
from scipy.spatial import cKDTree

class Nullcline:

    def __init__(self, params):
        # Initialize parameters
        self.params = params

        # Generate x and y grids
        x = np.linspace(0, 1, 2000)
        y = np.linspace(0, 1, 2000)
        self.x, self.y = np.meshgrid(x, y, indexing='ij')

        # Calculate nullclines
        self.cal_nullcline()
        
        # Calculate cross points
        self.cal_cross_points()

        # Cakcykate equiribrium point
        self.cal_equilibrium_points()

    def cal_nullcline(self):
        # Calculate Fx and Fy using vectorized operations
        self.Fx = self.fx(self.x, self.y, self.params)
        self.Fy = self.fy(self.x, self.y, self.params)

        # Detect nullclines
        self.nullcline_fx_x, self.nullcline_fx_y = self.find_zero_crossings(self.Fx, self.x, self.y)
        self.nullcline_fy_x, self.nullcline_fy_y = self.find_zero_crossings(self.Fy, self.x, self.y)

    @staticmethod
    def fx(x, y, params):
        tau1 = params['tau1']
        b1 = params['b1']
        S = params['S']
        WE11 = params['WE11']
        WE12 = params['WE12']
        WI11 = params['WI11']
        WI12 = params['WI12']

        term1 = (b1 * S + WE11 * x**2 + WE12 * y**2) * (1 - x)
        term2 = (1 + WI11 * x**2 + WI12 * y**2) * x
        Fx = (1 / tau1) * (term1 - term2)

        return Fx

    @staticmethod
    def fy(x, y, params):
        tau2 = params['tau2']
        b2 = params['b2']
        S = params['S']
        WE21 = params['WE21']
        WE22 = params['WE22']
        WI21 = params['WI21']
        WI22 = params['WI22']

        term1 = (b2 * S + WE21 * x**2 + WE22 * y**2) * (1 - y)
        term2 = (1 + WI21 * x**2 + WI22 * y**2) * y
        Fy = (1 / tau2) * (term1 - term2)

        return Fy

    @staticmethod
    def find_zero_crossings(F, X, Y):

        # Find sign changes along the y-axis
        F_sign = np.sign(F)
        sign_change_y = F_sign[:, :-1] * F_sign[:, 1:] < 0

        # Get indices where sign changes occur along y-axis
        i_y, j_y = np.where(sign_change_y)

        # Linear interpolation to find zero crossings along y-axis
        Fi_y = F[i_y, j_y]
        Fj1_y = F[i_y, j_y + 1]
        yi = Y[i_y, j_y]
        yj1 = Y[i_y, j_y + 1]
        y_zero_y = yi - Fi_y * (yj1 - yi) / (Fj1_y - Fi_y)
        x_zero_y = X[i_y, j_y]

        # Find sign changes along the x-axis
        sign_change_x = F_sign[:-1, :] * F_sign[1:, :] < 0

        # Get indices where sign changes occur along x-axis
        i_x, j_x = np.where(sign_change_x)

        # Linear interpolation to find zero crossings along x-axis
        Fi_x = F[i_x, j_x]
        Fi1_x = F[i_x + 1, j_x]
        xi = X[i_x, j_x]
        xi1 = X[i_x + 1, j_x]
        x_zero_x = xi - Fi_x * (xi1 - xi) / (Fi1_x - Fi_x)
        y_zero_x = Y[i_x, j_x]

        # Combine zero crossings from both directions
        x_zero = np.concatenate((x_zero_y, x_zero_x))
        y_zero = np.concatenate((y_zero_y, y_zero_x))

        return x_zero, y_zero

    def cal_cross_points(self):

        # Stack the nullcline points
        fx_points = np.column_stack((self.nullcline_fx_x, self.nullcline_fx_y))
        fy_points = np.column_stack((self.nullcline_fy_x, self.nullcline_fy_y))

        # Build KD-trees
        tree_fx = cKDTree(fx_points)
        tree_fy = cKDTree(fy_points)

        # Set esilon (torelance for considering points as close)
        epsilon = 1e-2

        # Find pairs of points that are close
        indices = tree_fx.query_ball_tree(tree_fy, r=epsilon)

        # Collect cross points
        cross_points = []
        for idx_fx, idx_fy_list in enumerate(indices):
            for idx_fy in idx_fy_list:
                x_fx, y_fx = fx_points[idx_fx]
                x_fy, y_fy = fy_points[idx_fy]
                # Average the positions as an initial guess
                x0 = (x_fx + x_fy) / 2
                y0 = (y_fx + y_fy) / 2
                cross_points.append((x0, y0))

        # return tentative equilibirum (cross points)
        self.cross_points = np.array(cross_points)


    def cal_equilibrium_points(self):

        # Function o compute Fx and Fy
        def F(z):
            x, y = z
            Fx = self.fx(x, y, self.params)
            Fy = self.fy(x, y, self.params)
            return np.array([Fx, Fy])

        # Collect roots
        roots = []
        for z0 in self.cross_points:
            sol = root(F, z0, method="hybr", tol=1e-8)
            if sol.success and 0 <= sol.x[0] <= 1 and 0 <= sol.x[1] <= 1:
                roots.append(sol.x)

        # Convert roots to numpy array and ensure it's 2D
        roots = np.array(roots)

        # Remove duplicates
        if len(roots) > 0:
            roots = np.atleast_2d(roots)
            roots = self.unique_rows(roots, tol=1e-6)
            self.equilibrium_points = roots
        else:
            self.equilibrium_points = np.empty((0, 2))


    @staticmethod
    def unique_rows(a, tol=1e-6):

        # return
        if a.size == 0 or a.shape[1] < 2:
            return a
        if len(a) == 1:
            return a

        # Remove duplicate rows within a tolerance
        a = a[np.lexsort((a[:, 1], a[:, 0]))]
        diff = np.diff(a, axis=0)
        dist = np.linalg.norm(diff, axis=1)
        mask = np.ones(len(a), dtype=bool)
        mask[1:] = dist > tol
        return a[mask]