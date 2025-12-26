# -*- coding: utf-8 -*-

"""
Title: method select

@author: shirafujilab

Created: 2024-11-14

Contents:

    ode (fem, rk4, ode45):

        - time waveforms (phase portraits)
        - attraction basin
        - bifurcation
        - return map


    CA (SynCA, ErCA):

        - time waveforms (phase portraits)
        - attraction basin
        - bifurcation
        - return map

Arguments:

    master: top module

        master.combos["model"] or params
            fem, rk4, ode45, SynCA, ErCA

        master.combos["simulation"] or params
            time evolution
            bifurcation
            attraction basin
            Poincare map (return map)
            stability

Note:

    Before Cal, parameter must be liseted up

"""

# import standard library
import numpy as np

import matplotlib.pyplot as plt

import datetime

# import my library
from src.method.euler.ode_basic import calc_time_evolution_ode
from src.method.eca.eca_basic import calc_time_evolution_eca, _make_lut_numba, _make_lut_numpy

from src.method.euler.ode_attraction_basin import ABODE
from src.method.eca.eca_attraction_basin import ABECA

from src.method.euler.ode_bif import BifODE
from src.method.eca.eca_bif import BifECA

from src.method.euler.ode_parameter_rigions import PRODE
from src.method.eca.eca_parameter_regions import PRECA

from src.method.eca.eca_return_map import EcaReMap



class MethodSelects:

    def __init__(self, master):

        self.master = master

        self.file_name = master.file_name

        # get information
        model = master.params["model"]
        sim_type = master.params["simulation"]

        if model in ["fem", "rk4", "ode45"]:
            self.sim_ode(sim_type)
        else:
            self.sim_ca(sim_type)


    def sim_ode(self, sim_type):

        # Local Analyses

        if sim_type == "time evolution":

            """ assign parameters  """

            # get params
            params = self.master.params

            # variables
            init_x, init_y = np.atleast_1d(params["init_x"]), np.atleast_1d(params["init_y"])

            # time
            sT, eT, h = params["sT"], params["eT"], params["h"]

            # params (fx)
            tau1, b1, S, WE11, WE12, WI11, WI12 = params['tau1'], params['b1'], params['S'], params['WE11'], params['WE12'], params['WI11'], params['WI12']

            # params (fy)
            tau2, b2, WE21, WE22, WI21, WI22 = params['tau2'], params['b2'], params['WE21'], params['WE22'], params['WI21'], params['WI22']

            # set calode
            t_hist, x_hist, y_hist = calc_time_evolution_ode(
                                                        init_x, init_y,
                                                        sT, eT, h,
                                                        tau1, b1, S, WE11, WE12, WI11, WI12,
                                                        tau2, b2, WE21, WE22, WI21, WI22
                                                        )

            self.master.results = Results(t_hist, x_hist, y_hist)

            # validation
            #self.state_analyzer()

        elif sim_type == "attraction basin":
            self.master.results_ab = ABODE(self.master, self.file_name)
            self.master.results_ab.run()

        # Global Analyses

        elif sim_type == "bifurcation":
            self.master.results_bif = BifODE(self.master.params, self.file_name)
            self.master.results_bif.run()

        elif sim_type == "parameter region":
            self.master.results_pr = PRODE(self.master.params, self.file_name)
            self.master.results_pr.run()

        elif sim_type == "ReturnMap":
            print("This function is not supported.")


    def sim_ca(self, sim_type):

        # Local Analyses

        if sim_type == "time evolution":

            """ assign parameters  """

            # get params
            params = self.master.params

            # variables
            init_x, init_y = np.atleast_1d(params["init_X"]).astype(np.int32), np.atleast_1d(params["init_Y"]).astype(np.int32)
            init_P, init_Q = np.atleast_1d(params["init_P"]).astype(np.int32), np.atleast_1d(params["init_Q"]).astype(np.int32)
            init_phX, init_phY = np.atleast_1d(params["init_phX"]).astype(np.float64), np.atleast_1d(params["init_phY"]).astype(np.float64)

            # time
            sT, eT = params["sT"], params["eT"]

            # params (fx)
            tau1, b1, S, WE11, WE12, WI11, WI12 = params['tau1'], params['b1'], params['S'], params['WE11'], params['WE12'], params['WI11'], params['WI12']

            # params (fy)
            tau2, b2, WE21, WE22, WI21, WI22 = params['tau2'], params['b2'], params['WE21'], params['WE22'], params['WI21'], params['WI22']

            # ca params
            N, M, s1, s2, gamma_X, gamma_Y, Tc, Tx, Ty = params["N"], params["M"], params["s1"], params["s2"], params["gamma_X"], params["gamma_Y"], params["Tc"], params["Tx"], params["Ty"]

            bench_sT = datetime.datetime.now()
            print("\n start: ", bench_sT)

            Fin, Gin = _make_lut_numba(N, M, s1, s2, gamma_X, gamma_Y, Tc, Tx, Ty,
                                       tau1, b1, S, WE11, WE12, WI11, WI12,
                                       tau2, b2, WE21, WE22, WI21, WI22)

            t_hist, x_hist, y_hist = calc_time_evolution_eca(init_x, init_y, init_P, init_Q, init_phX, init_phY,
                                                             N, M, Tc, Tx, Ty,
                                                             sT, eT, Fin, Gin)


            bench_eT = datetime.datetime.now()
            print("end: ", bench_eT)

            print("bench mark: ", bench_eT - bench_sT)

            self.master.results = Results(t_hist, x_hist, y_hist)
            
            print(f"x: {min(min(x_hist))}--{max(max(x_hist))}, y: {min(min(y_hist))}--{max(max(y_hist))}" )

            # validation
            # self.state_analyzer()

        elif sim_type == "attraction basin":
            self.master.results_ab = ABECA(self.master, self.file_name)
            self.master.results_ab.run()

        elif sim_type == "ReturnMap":
            results_ReMap = EcaReMap(self.master, self.file_name)

        # Global Analyses

        elif sim_type == "bifurcation":
            self.master.results_bif = BifECA(self.master.params, self.file_name)
            self.master.results_bif.run()

        elif sim_type == "parameter region":
            self.master.results_pr = PRECA(self.master.params, self.file_name)
            self.master.results_pr.run()




    def state_analyzer(self):

        # numpy 1-dim array
        t = self.master.results.t_hist
        x = self.master.results.x_hist
        y = self.master.results.y_hist

        # データの形状を確認して一次元配列に変換
        t = np.array(t).flatten()
        x = np.array(x).flatten()
        y = np.array(y).flatten()

        """ 1. np.mean() """
        mean_x = np.mean(x)
        mean_y = np.mean(y)

        """ 2. np.var() """
        variance_x = np.var(x)
        variance_y = np.var(y)

        """ 3. np.fft.fft() """
        # データの平均を引いて直流成分を除去
        x_zero_mean = x - mean_x
        y_zero_mean = y - mean_y

        # サンプリング間隔を計算（データが等間隔であると仮定）
        dt = t[1] - t[0]

        # フーリエ変換を計算
        fft_x = np.fft.fft(x_zero_mean)
        fft_y = np.fft.fft(y_zero_mean)

        # 周波数成分を計算
        freqs = np.fft.fftfreq(len(t), d=dt)

        """ 4. np.histogram """
        # ヒストグラムを計算
        hist_x, bin_edges_x = np.histogram(x, bins=50)
        hist_y, bin_edges_y = np.histogram(y, bins=50)

        """ 5. 自己相関 """
        # 自己相関を計算
        autocorr_x = np.correlate(x_zero_mean, x_zero_mean, mode='full')
        autocorr_y = np.correlate(y_zero_mean, y_zero_mean, mode='full')

        # 正のラグ（遅れ）のみを取得
        autocorr_x = autocorr_x[autocorr_x.size // 2:]
        autocorr_y = autocorr_y[autocorr_y.size // 2:]

        # 正規化（自己相関関数の最大値を1にする）
        autocorr_x /= autocorr_x[0]
        autocorr_y /= autocorr_y[0]

        """ results """
        print("x mean: ", mean_x, "y mean: ", mean_y)
        print("x var: ", variance_x, "y var: ", variance_y)

        # 描画関数の呼び出し
        self.plot_fft(freqs, fft_x, fft_y)
        self.plot_histogram(hist_x, bin_edges_x, hist_y, bin_edges_y)
        self.plot_autocorrelation(t, autocorr_x, autocorr_y)


    def plot_fft(self, freqs, fft_x, fft_y):
        """フーリエ変換結果のプロット"""
        # 周波数が正の部分のみを使用
        positive_freqs = freqs[freqs >= 0]
        amplitude_x = np.abs(fft_x)[freqs >= 0]
        amplitude_y = np.abs(fft_y)[freqs >= 0]

        plt.figure(figsize=(10, 4))
        plt.plot(positive_freqs, amplitude_x, label='x')
        plt.plot(positive_freqs, amplitude_y, label='y')
        plt.xlabel('Frequency [Hz]')
        plt.ylabel('Amplitude')
        plt.title('3. FFT Spectrum')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def plot_histogram(self, hist_x, bin_edges_x, hist_y, bin_edges_y):
        """ヒストグラムのプロット"""
        plt.figure(figsize=(10, 4))

        # xのヒストグラム
        bin_centers_x = (bin_edges_x[:-1] + bin_edges_x[1:]) / 2
        plt.bar(bin_centers_x, hist_x, width=bin_edges_x[1]-bin_edges_x[0], alpha=0.5, label='x')

        # yのヒストグラム
        bin_centers_y = (bin_edges_y[:-1] + bin_edges_y[1:]) / 2
        plt.bar(bin_centers_y, hist_y, width=bin_edges_y[1]-bin_edges_y[0], alpha=0.5, label='y')

        plt.xlabel('Value')
        plt.ylabel('Frequency')
        plt.title('4. Histogram')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()


    def plot_autocorrelation(self, t, autocorr_x, autocorr_y):
        """自己相関関数のプロット"""
        dt = t[1] - t[0]
        lags = np.arange(len(autocorr_x)) * dt

        plt.figure(figsize=(10, 4))
        plt.plot(lags, autocorr_x, label='x')
        plt.plot(lags, autocorr_y, label='y')
        plt.xlabel('Lag Time')
        plt.ylabel('Autocorrelation')
        plt.title('5. Autocorrelation Function')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()



class Results:

    def __init__(self, t, x, y, phx = None, phy = None):

        self.t_hist = t
        self.x_hist = x
        self.y_hist = y