# -*- coding: utf-8 -*-
"""

Created on: 2024-10-22
Updated on: 2024-11-12

@author: shirafujilab

Contents: parameter region analysis for bifurcation diagram with two parameters (S and Q)

    X: 0, 2, 4, ..., 63
    Y: 0, 2, 4, ..., 63

    Fixed: P, Q, phX, phY


## Benchmark

### Case1
    Parameter space: 80x80
    State space    : 32x32
    Total #sim     : 37 min
    
    parameters: 100*100
    8 min 36 sec



"""



# import standard library
import numpy as np
import pandas as pd
import os

import numba
numba.set_num_threads(15)
from numba import njit, prange

import datetime, time
import matplotlib.pyplot as plt

# import my library

from src.method.eca.eca_basic import  calc_time_evolution_eca, _make_lut_numba, _make_rotated_lut_numba
from src.graphics.graphic_lut import _make_rotated_coordinate
from src.graphics.graphic_param_region import match_rate_get_df


class SweepLineGraph:

    def __init__(self, params, filename):

        # get params
        self.params = params

        self.filename = filename
        print(self.filename)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)


    def run(self):

        """ Initialization """

        # get params
        params = self.params

        # variables
        x = np.arange(0, self.params["N"], 8, dtype=np.int16)
        y = np.arange(0, self.params["N"], 8, dtype=np.int16)

        xx_mesh, yy_mesh = np.meshgrid(x, y)
        xx, yy = xx_mesh.flatten(), yy_mesh.flatten()
        conds_size = xx.size        # initial conditions

        # parameters
        sT, eT = 500, 800
        tau1, b1, WE11, WE12, WI11, WI12 = params['tau1'], params['b1'], params['WE11'], params['WE12'], params['WI11'], params['WI12']
        tau2, b2, WE21, WE22, WI21, WI22 = params['tau2'], params['b2'], params['WE21'], params['WE22'], params['WI21'], params['WI22']
        N, M, s1, s2, Tc, Tx, Wx, Ty, Wy = params["N"], params["M"], params["s1"], params["s2"], params["Tc"], params["Tx"], params["Wx"], params["Ty"], params["Wy"]
        deg = params["deg"]

        # store step
        total_step = int(eT/Tc)+1
        index_start = int(sT/Tc)
        store_step = (total_step - index_start) // 100 + 1 if total_step > index_start else 0

        """ bifurcation """

        # Conditions of S, Q
        bif_S = np.arange(0.20, 0.70, 0.01)
        bif_Q = np.arange(0.20, 0.70, 0.01)

        num_S = bif_S.size
        num_Q = bif_Q.size

        # for store results
        S_hist = np.zeros((num_S, num_Q, conds_size))
        Q_hist = np.zeros((num_S, num_Q, conds_size))
        xmax_hist = np.zeros((num_S, num_Q, conds_size))
        xmin_hist = np.zeros((num_S, num_Q, conds_size))


        """ run simulation """
        bench_sT = datetime.datetime.now()
        print("\n start: ", bench_sT)

        if params["param set"] == "set 1":
            ode_file_path = r"c:\Storage\02_paper\04_2025_Nolta journal\04_Python\data\results\set 1\forward euler\results\parameter region\20260216000243.csv"
        elif params["param set"] == "set 2":
            ode_file_path = r"c:\Storage\02_paper\04_2025_Nolta journal\04_Python\data\results\set 2\forward euler\results\parameter region\20260216000431.csv"


        """ store TxTy result """
        result_txty = []

        # config
        sitr = 0
        eitr = 2

        for _deg in range(sitr, eitr, 1):

            deg = _deg
            rotated_x, rotated_y =_make_rotated_coordinate(N, deg) # (size, degree)

            for delta_x in range(1, 10, 1):

                for delta_y in range(1, 10, 1):
                    
                    Wx = Tx * 0.1*delta_x
                    Wy = Ty * 0.1*delta_y

                    result_list=[]

                    for idx_s in range(num_S):

                        for idx_q in range(num_Q):

                            Q = bif_Q[idx_q]

                            # update relative values
                            if params["param set"] in ["set 1", "set 2", "set 3"]:
                                b1, b2, WI12 = 0.13 * (1 + Q), 0, 0.5*Q

                            else:
                                b1, b2, WI12 = 0.13*(1-Q), 0.26*Q, 0

                            Fin, Gin = _make_rotated_lut_numba(N, M, s1, s2, Tx, Wx, Ty, Wy,
                                                    tau1, b1, bif_S[idx_s], WE11, WE12, WI11, WI12,
                                                    tau2, b2, WE21, WE22, WI21, WI22,
                                                    rotated_x, rotated_y, deg)

                            x_max, x_min = self.calc_parameter_region(xx, yy, 0, 0, 0, 0,
                                                                    N, M, Tc, Tx, Wx, Ty, Wy,
                                                                    total_step, index_start, store_step, Fin, Gin)

                            S_hist[idx_s, idx_q, :] = bif_S[idx_s]
                            Q_hist[idx_s, idx_q, :] = Q
                            xmax_hist[idx_s, idx_q, :] = x_max
                            xmin_hist[idx_s, idx_q, :] = x_min
                            
                            result = self.analyze_results(bif_Q[idx_q], bif_S[idx_s], xmax_hist[idx_s, idx_q, :], xmin_hist[idx_s, idx_q, :])
                            result_list.append(result)

                    df = pd.DataFrame(result_list)

                    df = df[["Q", "S", "max_1", "max_2", "max_3",
                    "min_1", "min_2", "min_3", "state"]]

                    rate = match_rate_get_df(ode_file_path, df)
                    print("theta=", deg, "delta_X=", delta_x, ", delta_Y=", delta_y, ", rate: ", f"{rate*100:.6f}")
                    result_txty.append([deg, delta_x, delta_y, rate*100, max(rate*100-90,0)])


        bench_eT = datetime.datetime.now()

        print("end: ", bench_eT)
        print("bench mark: ", bench_eT - bench_sT)

        ddf = pd.DataFrame(result_txty, columns=["deg", "delta_X", "delta_Y", "res1", "res2"])

        save_path = os.path.join(os.path.dirname(self.filename), f"results_{sitr}--{eitr-1}.csv")
        ddf.to_csv(save_path, index=False, encoding='utf-8')
        print(f"Results saved to: {save_path}")



    @staticmethod
    @njit(parallel=True)
    def calc_parameter_region(xx, yy, pp, qq, phxx, phyy,
                              N, M, Tc, Tx, Wx, Ty, Wy,
                              total_step, index_start, store_step, Fin, Gin):

        # conditions number (x, y)
        total_conds = xx.size

        # return
        x_max_hist = np.empty(total_conds, dtype=np.int16)
        x_min_hist = np.empty(total_conds, dtype=np.int16)

        # loop
        for idx in prange(total_conds):

            _, x_hist, _ = calc_time_evolution_eca(xx[idx], yy[idx], pp, qq, phxx, phyy,
                                                   N, M, Tc, Tx, Wx, Ty, Wy,
                                                   total_step, index_start, store_step, Fin, Gin)

            # update max, min
            x_max_hist[idx] = np.max(x_hist)
            x_min_hist[idx] = np.min(x_hist)

        return x_max_hist, x_min_hist


    def analyze_results(self, Q, S, x_max, x_min):

        # [(x_max[0], x_min[0]), (x_max[1], x_min[1]), ...]
        x_max_min = np.column_stack((x_max, x_min))

        """ analysis """

        # get unique (max, min) combination
        x_max_min_sort = np.unique(x_max_min, axis=0)

        required = 10
        current = x_max_min_sort.shape[0]

        if current < required:
            padding = np.array([[None, None]] * (required - current), dtype=object)
            x_max_min_sort = np.vstack((x_max_min_sort, padding))
        else:
            x_max_min_sort = x_max_min_sort[:required]

        # get arrays without (None, None)
        valid_pairs = x_max_min_sort[~np.any(x_max_min_sort == None, axis=1)]

        # judge equilibrium (eq) or periodic orbit (po)
        eq_pairs = []
        po_pairs = []

        for pair in valid_pairs:

            # equilibirum ( <= 4)
            if pair[0] - pair[1] <= 4: eq_pairs.append(pair)

            # periodic orbit
            else: po_pairs.append(pair)

        # get unique equilibrium (distance >= 3)
        #unique_eq = [eq_pairs[0]]

        #for eq in eq_pairs:
        #    unique_eq.append(eq)
        #    if all(np.linalg.norm(eq - existing_eq) >= 3 for existing_eq in unique_eq):
        #        unique_eq.append(eq)

        # get unique equilibrium
        unique_eq = []

        for eq in eq_pairs:
            if eq[0] is None:
                continue

            eq_max, eq_min = eq[0], eq[1]
            eq_size = eq_max - eq_min

            merged = False
            for i, existing in enumerate(unique_eq):
                ex_max, ex_min = existing[0], existing[1]
                ex_size = ex_max - ex_min

                # i) eq is contained within existing
                if eq_max <= ex_max and eq_min >= ex_min:
                    merged = True
                    # ii) if eq is smaller, replace
                    if eq_size < ex_size:
                        unique_eq[i] = eq
                    break

                # ii) nearly same position and size, within ±1 shift
                if (abs(eq_max - ex_max) <= 1 and abs(eq_min - ex_min) <= 1):
                    merged = True
                    # replace if eq is smaller
                    if eq_size < ex_size:
                        unique_eq[i] = eq
                    break

            # iii) not merged means it has min > existing max or max < existing min
            # i.e., clearly separate region -> new set
            if not merged:
                unique_eq.append(eq)

        # get unique periodic orbit (same logic)
        unique_po = []

        for po in po_pairs:
            if po[0] is None:
                continue

            po_max, po_min = po[0], po[1]
            po_size = po_max - po_min

            merged = False
            for i, existing in enumerate(unique_po):
                ex_max, ex_min = existing[0], existing[1]
                ex_size = ex_max - ex_min

                # i) po is contained within existing
                if po_max <= ex_max and po_min >= ex_min:
                    merged = True
                    if po_size < ex_size:
                        unique_po[i] = po
                    break

                # ii) nearly same position and size
                if (abs(po_max - ex_max) <= 1 and abs(po_min - ex_min) <= 1):
                    merged = True
                    if po_size < ex_size:
                        unique_po[i] = po
                    break

            if not merged:
                unique_po.append(po)

        # count up eq and po
        num_eq = len(unique_eq)
        num_po = len(unique_po)

        """ classified state """

        # 1. monostable
        if num_eq == 1 and num_po == 0: state = 1

        # 2. bistable
        elif num_eq == 2 and num_po == 0: state = 2

        # 3. periodic orbit
        elif num_eq == 0 and num_po == 1: state = 3

        # 4. coexistence (1 eq and 1 po)
        elif num_eq == 1 and num_po == 1: state = 4

        # 5. others
        else: state = 5

        """ Summarized results """
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

        return result



""" For graphic """

def plot_combined_results(csv_paths, output_dir):
    """
    複数のCSVファイルを結合して、delta_X, delta_Yごとの折れ線グラフを描画

    Parameters
    ----------
    csv_paths : list of str
        読み込むCSVファイルのパスのリスト
    output_dir : str
        グラフの保存先ディレクトリ
    """
    
    # 複数のCSVファイルを結合
    df_list = []
    for path in csv_paths:
        df = pd.read_csv(path, encoding='utf-8')
        df_list.append(df)
    
    combined_df = pd.concat(df_list, ignore_index=True)
    
    # delta_X, delta_Yのユニークな組み合わせを取得
    delta_combinations = combined_df[['delta_X', 'delta_Y']].drop_duplicates().sort_values(['delta_X', 'delta_Y'])
    
    # 出力ディレクトリの作成
    os.makedirs(output_dir, exist_ok=True)
    
    # 各delta_X, delta_Yの組み合わせごとにグラフを作成
    for idx, row in delta_combinations.iterrows():
        delta_x = row['delta_X']
        delta_y = row['delta_Y']
        
        # 該当データを抽出
        subset = combined_df[(combined_df['delta_X'] == delta_x) & 
                            (combined_df['delta_Y'] == delta_y)].sort_values('deg')
        
        # グラフ作成
        plt.figure(figsize=(10, 6))
        plt.plot(subset['deg'], subset['res1'], marker='o', linewidth=2, markersize=6)
        plt.xlabel('theta (deg)', fontsize=12)
        plt.ylabel('res1 (%)', fontsize=12)
        plt.title(f'delta_X={delta_x}, delta_Y={delta_y}', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # 保存
        save_path = os.path.join(output_dir, f'line_graph_dX{delta_x}_dY{delta_y}.png')
        plt.savefig(save_path, dpi=150)
        plt.close()
        
        print(f"Saved: {save_path}")
    
    print(f"\nAll graphs saved to: {output_dir}")
    
    # 結合したデータも保存
    combined_csv_path = os.path.join(output_dir, 'combined_results.csv')
    combined_df.to_csv(combined_csv_path, index=False, encoding='utf-8')
    print(f"Combined data saved to: {combined_csv_path}")


if __name__ == "__main__":
    
    # 読み込むCSVファイルのパスを指定
    csv_paths = [
        r"c:\Storage\02_paper\04_2025_Nolta journal\04_Python\data\results\set 1\rotated-LUT CA\results\Scheduled Analysis\results_0--1.csv",
        #r"c:\path\to\result_txty_2.csv",
        #r"c:\path\to\result_txty_3.csv",
        # 必要に応じて追加
    ]
    
    # グラフの出力先ディレクトリ
    output_dir = r"c:\path\to\output\line_graphs"
    
    # 折れ線グラフを生成
    plot_combined_results(csv_paths, output_dir)