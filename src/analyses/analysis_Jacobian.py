# -*- coding: utf-8 -*-
"""

Created: 2024-11-06

@author: shirafujilab

Contents:

    - Jacobian matrix
        - solve partial equation
        - Finite Difference Method: DFM
        - Automatic Differentiation: AD
        - scipy, symbolic calculation

    - eigenvalue
    - lyapunov exponents

"""


# import standard library

import numpy as np
from scipy.linalg import eigvals



class SolveNonlinear:

    def __init__(self, eset_x, eset_y, params):

        # Get Conditions
        self.eset_x = eset_x
        self.eset_y = eset_y
        self.params = params

        # Store results (jacobian matrix, eigenvalue, lyapunov exponents)
        self.jacobians = []
        self.eigenvalues = []
        self.ls = []

        self._compute_all()


    def _compute_all(self):

        # Generate jacobian matrix
        self.cal_jacobian_matrix()

        # Analyze cross points (sink, source, saddle)
        self.analyze_cross_points()


    def cal_jacobian_matrix(self):

        # parameter sets
        x = self.eset_x
        y = self.eset_y
        params = self.params

        # calculate value of jabobian matrix
        j11 = self.pfpx(x, y, params)
        j12 = self.pfpy(x, y, params)
        j21 = self.pgpx(x, y, params)
        j22 = self.pgpy(x, y, params)

        # transpose to each jacobian matrix
        self.jacobians = np.array([[j11, j12], [j21, j22]]).transpose(2, 0, 1)

        # calculate eigenvalues
        self.eigenvalues = np.array([eigvals(jac) for jac in self.jacobians])


    def analyze_cross_points(self):

        # get real part
        self.ls = np.real(self.eigenvalues)

        # get sign
        self.sig_ls = np.sign(self.ls)

        # store results
        self.classifications = []

        for idx, real_parts in enumerate(self.ls):

            if np.all(real_parts < 0):
                self.classifications.append("sink")
            elif np.all(real_parts > 0):
                self.classifications.append("source")
            elif np.any(real_parts > 0) and np.any(real_parts < 0):
                self.classifications.append("saddle")
            else:
                self.classifications(real_parts)


    @staticmethod
    def pfpx(x, y, params):
        return (1/params["tau1"])*(-3*(params["WE11"]+params["WI11"])*x**2 + 2*params["WE11"]*x
                                   - (params["b1"]*params["S"] + 1 + (params["WE12"] + params["WI12"])*y**2))


    @staticmethod
    def pfpy(x, y, params):
        return (1/params["tau1"])*(2*params["WE12"]*y*(1-x) - 2*params["WI12"]*y*x)


    @staticmethod
    def pgpx(x, y, params):
        return (1/params["tau2"])*(2*params["WE21"]*x*(1-y) - 2*params["WI21"]*x*y)


    @staticmethod
    def pgpy(x, y, params):
        return (1/params["tau2"])*(-3*(params["WE22"]+params["WI22"])*y**2 + 2*params["WE22"]*y
                                   - (params["b2"]*params["S"] + 1 + (params["WE21"] + params["WI21"])*x**2))


    def equations(vars, params):
        x, y = vars
        tau1, tau2, b1, b2, WE11, WE12, WE21, WE22, WI11, WI12, WI21, WI22, S = params.values()
        fx = (1/tau1)*((b1*S+WE11*x**2+WE12*y**2)*(1-x)-(1+WI11*x**2+WI12*y**2)*x)
        fy = (1/tau2)*((b2*S+WE21*x**2+WE22*y**2)*(1-y)-(1+WI21*x**2+WI22*y**2)*y)
        return [fx, fy]

