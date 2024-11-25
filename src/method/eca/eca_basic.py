# -*- coding: utf-8 -*-
"""
Created on: 2023-7-23
Updated on: 2024-11-15

@author: shirafujilab
"""


import numpy as np

from numba import njit

class CalCA:
    def __init__(self, params):

        # get params
        self.params = {k: np.int32(v) if isinstance(v, int) else v for k, v in params.items()}

        # state variables
        self.init_X = np.atleast_1d(params["init_X"]).astype(np.int32)
        self.init_Y = np.atleast_1d(params["init_Y"]).astype(np.int32)
        self.init_P = np.atleast_1d(params["init_P"]).astype(np.int32)
        self.init_Q = np.atleast_1d(params["init_Q"]).astype(np.int32)
        self.init_phX = np.atleast_1d(params["init_phX"]).astype(np.float64)
        self.init_phY = np.atleast_1d(params["init_phY"]).astype(np.float64)

        # registers
        self.t_hist = None
        self.x_hist = None
        self.y_hist = None
        self.phx_hist = None
        self.phy_hist = None


    def run(self):

        # time
        sT = self.params["sT"]
        eT = self.params["eT"]
        h = self.params["h"]

        # params (fx)
        tau1 = self.params['tau1']
        b1 = self.params['b1']
        S = self.params['S']
        WE11 = self.params['WE11']
        WE12 = self.params['WE12']
        WI11 = self.params['WI11']
        WI12 = self.params['WI12']

        # params (fy)
        tau2 = self.params['tau2']
        b2 = self.params['b2']
        WE21 = self.params['WE21']
        WE22 = self.params['WE22']
        WI21 = self.params['WI21']
        WI22 = self.params['WI22']

        # cellular automaton parameters
        N = self.params["N"]
        M = self.params["M"]
        s1 = self.params["s1"]
        s2 = self.params["s2"]
        gamma_X = self.params["gamma_X"]
        gamma_Y = self.params["gamma_Y"]
        Tc = self.params["Tc"]
        Tx = self.params["Tx"]
        Ty = self.params["Ty"]

        self.t_hist, self.x_hist, self.y_hist, self.phx_hist, self.phy_hist = self.run_simulation(
                                                                    self.init_X, self.init_Y, self.init_P, self.init_Y, self.init_phX, self.init_phY,
                                                                    N, M, s1, s2, gamma_X, gamma_Y, Tc, Tx, Ty,
                                                                    sT, eT,
                                                                    tau1, b1, S, WE11, WE12, WI11, WI12,
                                                                    tau2, b2, WE21, WE22, WI21, WI22)


    @staticmethod
    @njit
    def run_simulation(init_X, init_Y, init_P, init_Q, init_phX, init_phY,
                        N, M, s1, s2, gamma_X, gamma_Y, Tc, Tx, Ty,
                        sT, eT,
                        tau1, b1, S, WE11, WE12, WI11, WI12,
                        tau2, b2, WE21, WE22, WI21, WI22):

        # Variables
        x_next = x_previous = init_X
        y_next = y_previous = init_Y
        p_next = p_previous = init_P
        q_next = q_previous = init_Q
        phx_next = phx_previous = init_phX
        phy_next = phy_previous = init_phY
        Cx = np.zeros_like(init_phX)
        Cy = np.zeros_like(init_phY)


        # Time
        T = 0

        # Calculate total step for storing
        total_step = int(eT/Tc)+1
        index_start = int(sT/Tc)
        store_step = total_step - index_start if total_step > index_start else 0

        # Get size of x, y
        n = init_X.size if init_X.ndim>0 else 1

        # store return arrays
        t_hist = np.zeros(store_step)
        x_hist = np.zeros((store_step, n))
        y_hist = np.zeros((store_step, n))
        phx_hist = np.zeros(store_step)         # enough 1-dim
        phy_hist = np.zeros(store_step)         # enough 1-dim

        idx = 0

        def dde_X():

            Fin = (1/tau1)*((b1*S+WE11*(x_previous/s1)**2+WE12*(y_previous/s2)**2)*(1-x_previous/s1)
                                -(1+WI11*(x_previous/s1)**2+WI12*(y_previous/s2)**2)*x_previous/s1)

            # First: if Fin == 0, result = M-1
            Fin = np.where(Fin == 0, M-1, Fin)

            Fin = gamma_X/Fin*(Tc/Tx)

            # Second: if Fin > 0
            positive_condition = np.floor(Fin) >= M - 1
            Fin = np.where(positive_condition, M - 1, Fin)

            # Third: if Fin < 0
            negative_condition = np.ceil(Fin) <= -(M - 1)
            Fin = np.where(negative_condition, -(M - 1), Fin)

            Fin = np.where(Fin >= 0, np.ceil(Fin), np.floor(Fin))

            return Fin

        def dde_Y():

            Gin = (1/tau2)*((b2*S+WE21*(x_previous/s1)**2+WE22*(y_previous/s2)**2)*(1-y_previous/s2)
                                -(1+WI21*(x_previous/s1)**2+WI22*(y_previous/s2)**2)*y_previous/s2)

            # First: if Gin == 0, result = M-1
            Gin = np.where(Gin == 0, M-1, Gin)

            Gin = gamma_Y/Gin*(Tc/Ty)

            # Second: if Gin > 0
            positive_condition = np.floor(Gin) >= M - 1
            Gin = np.where(positive_condition, M - 1, Gin)

            # Third: if Gin < 0
            negative_condition = np.ceil(Gin) <= -(M - 1)
            Gin = np.where(negative_condition, -(M - 1), Gin)
            
            Gin = np.where(Gin >= 0, np.ceil(Gin), np.floor(Gin))

            return Gin

        def time_evolution(T, phx_previous, phy_previous, Cx, Cy):

            T = T + Tc

            phx_next = phx_previous + Tc/Tx
            phy_next = phy_previous + Tc/Ty

            phx_next = np.where(phx_next >= 1, phx_next - 1, phx_next)
            phy_next = np.where(phy_next >= 1, phy_next - 1, phy_next)

            Cx = np.where(phx_next >= (1-Tc/Tx), 1, 0)
            Cy = np.where(phy_next >= (1-Tc/Ty), 1, 0)
            
            return T, phx_next, phy_next, Cx, Cy


        for i in range(total_step):

            # time evolution
            T, phx_next, phy_next, Cx, Cy = time_evolution(T, phx_previous, phy_previous, Cx, Cy)

            # calculate
            Fx = dde_X()
            Fy = dde_Y()
            
            absFx = np.abs(Fx)
            absFy = np.abs(Fy)

            # cal auxiliary variables
            p_next = np.where(Cx==1,
                              np.where((p_previous < absFx) & (p_previous < M - 1), p_previous + 1, 0), p_previous).astype(np.int32)

            q_next = np.where(Cy==1,
                              np.where((q_previous < absFy) & (q_previous < M - 1), q_previous + 1, 0), q_previous).astype(np.int32)

            x_next = np.where(Cx==1,
                                np.where((p_previous >= absFx) | (p_previous >= M -1),
                                    np.where((Fx >=0) & (x_previous < N-1), x_previous + 1,
                                        np.where((Fx < 0) & (x_previous > 0), x_previous - 1, x_previous)),
                                    x_previous),
                                x_previous).astype(np.int32)

            y_next = np.where(Cy==1,
                                np.where((q_previous >= absFy) | (q_previous >= M -1),
                                    np.where((Fy >=0) & (y_previous < N-1), y_previous + 1,
                                        np.where((Fy < 0) & (y_previous > 0), y_previous - 1, y_previous)),
                                    y_previous),
                                y_previous).astype(np.int32)

            # store registers
            if i >= index_start:

                t_hist[idx] = T
                x_hist[idx,:] = x_previous
                y_hist[idx,:] = y_previous
                phx_hist[idx] = phx_previous[0]
                phy_hist[idx] = phy_previous[0]

                idx += 1

            # update variables
            x_previous = x_next
            y_previous = y_next
            p_previous = p_next
            q_previous = q_next
            phx_previous = phx_next
            phy_previous = phy_next


        return t_hist, x_hist, y_hist, phx_hist, phy_hist


