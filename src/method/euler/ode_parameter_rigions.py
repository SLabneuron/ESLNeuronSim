# -*- coding: utf-8 -*-
"""
Created on: 2024-10-22
Updated on: 2024-11-12

@author: shirafujilab

Contents: Parameter region analysis for bifurcation diagram with two parameters (S and Q)

"""

# import standard library
import numpy as np
import pandas as pd
import os

import datetime

# import my library
from src.method.euler.ode_basic import CalODE


class PRODE:

    def __init__(self, params, filename):

        # get params
        self.params = params

        self.filename = filename
        print(self.filename)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)

        self.make_xx_yy()

    def make_xx_yy(self):

        self.x = np.arange(0, 0.81, 0.02)
        self.y = np.arange(0, 0.81, 0.02)

        xx, yy = np.meshgrid(self.x, self.y)

        xx = xx.flatten()
        yy = yy.flatten()

        self.params["init_x"] = xx
        self.params["init_y"] = yy

        self.num_initial_conditions = xx.size

    def run(self):

        # Conditions of S
        bif_S = np.arange(0, 0.81, 0.05)
        num_S = len(bif_S)

        # Conditions of Q
        bif_Q = np.arange(0, 0.81, 0.05)
        num_Q = len(bif_Q)

        # Number of initial conditions of state vector
        num_IC = self.num_initial_conditions

        # Initialize lists to store results
        results_list = []

        print("start: ", datetime.datetime.now())

        for Q_idx, Q in enumerate(bif_Q):

            self.params["Q"] = Q

            # resolve lambda equ
            self.params["b1"] = eval(self.params["b1_equ"])()
            self.params["b2"] = eval(self.params["b2_equ"])()
            self.params["WI12"] = eval(self.params["WI12_equ"])()

            print("process --->", round(Q_idx/len(bif_Q)*100, 2), "% < ---")

            for S_idx, S in enumerate(bif_S):

                self.params["S"] = S

                """ Analysis """

                inst = CalODE(self.params)
                inst.run()

                x_hist = inst.x_hist  # shape (num_time_steps, num_IC)

                # 各初期条件に対して最大値と最小値を取得
                x_max = np.max(x_hist, axis=0)  # shape (num_IC,)
                x_min = np.min(x_hist, axis=0)  # shape (num_IC,)

                # x_max と x_min を小数点以下3桁に丸める
                x_max_rounded = np.round(x_max, 3)
                x_min_rounded = np.round(x_min, 3)

                x_max_min = np.column_stack((x_max_rounded, x_min_rounded))

                x_max_min_sort = np.unique(x_max_min, axis=0)

                required = 3
                current = x_max_min_sort.shape[0]

                if current < required:
                    padding = np.array([[None, None]] * (required - current), dtype=object)
                    x_max_min_sort = np.vstack((x_max_min_sort, padding))
                else:
                    x_max_min_sort = x_max_min_sort[:required]

                # 有効なペアのみを抽出（Noneを除外）
                valid_pairs = x_max_min_sort[~np.any(x_max_min_sort == None, axis=1)]

                # 平衡点と周期軌道の判定
                eq_pairs = []
                po_pairs = []

                for pair in valid_pairs:
                    if pair[0] - pair[1] < 0.005:
                        # 平衡点
                        eq_pairs.append(pair)
                    else:
                        # 周期軌道
                        po_pairs.append(pair)

                # 平衡点の重複チェック（距離 >= 0.005）
                unique_eq = []
                for eq in eq_pairs:
                    if all(np.linalg.norm(eq - existing_eq) >= 0.015 for existing_eq in unique_eq):
                        unique_eq.append(eq)

                num_eq = len(unique_eq)
                num_po = len(po_pairs)

                # 状態の分類
                if num_eq == 1 and num_po == 0:
                    state = 1  # 平衡点1つだけ
                elif num_eq == 2 and num_po == 0:
                    state = 2  # 平衡点2つだけ
                elif num_eq == 0 and num_po == 1:
                    state = 3  # 周期軌道1つだけ
                elif num_eq == 1 and num_po == 1:
                    state = 4  # 平衡点1つと周期軌道1つ
                else:
                    state = 5  # その他

                # 結果をまとめる
                result = {
                    "Q": Q,
                    "S": S,
                    "max_1": x_max_min_sort[0][0],
                    "max_2": x_max_min_sort[1][0],
                    "max_3": x_max_min_sort[2][0],
                    "min_1": x_max_min_sort[0][1],
                    "min_2": x_max_min_sort[1][1],
                    "min_3": x_max_min_sort[2][1],
                    "state": state
                }
                results_list.append(result)

        # データフレームの作成
        df = pd.DataFrame(results_list)

        # 列の順序を指定
        df = df[["Q", "S", "max_1", "max_2", "max_3",
                 "min_1", "min_2", "min_3", "state"]]

        # CSVファイルに保存
        try:
            df.to_csv(self.filename, index=False)
            print(f"Results saved to {self.filename}")
        except Exception as e:
            print(f"Error saving results to {self.filename}: {e}")

        print("end: ", datetime.datetime.now())
