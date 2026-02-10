# # -*- coding: utf-8 -*-

"""
Title: graphic heatmmap

@author: shirafujilab

Created on: 2024-11-28

Contents:

    - heatmap of attraction basin

    - heatmap of parameter region

    - any

"""

import pandas as pd
import plotly.graph_objects as go


def graphic_pr(path):

    # file path
    csv_path = path

    # read csv file
    df = pd.read_csv(csv_path)

    # confirm "state" colummn
    if 'state' not in df.columns:
        raise ValueError("Not Found Error: 'state'")

    # confirming type of state is int
    df['state'] = df['state'].astype(int)


    # define heatmap
    heatmap_data = df.pivot(index='Q', columns='S', values='state')

    # sort index
    heatmap_data = heatmap_data.sort_index(ascending=True)  # Qを昇順に
    heatmap_data = heatmap_data.sort_index(axis=1, ascending=True)  # Sを昇順に

    # define color map
    categorical_color_map = {
        1: '#808080',  # gray
        2: '#FFD700',  # gold
        3: '#32CD32',  # lime green
        4: '#1E90FF',  # deep blue
        5: '#FF0000'   # red
    }

    # make figure
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale=[
            [0.0, categorical_color_map[1]],    # state 1
            [0.2, categorical_color_map[2]],    # state 2
            [0.4, categorical_color_map[3]],    # state 3
            [0.6, categorical_color_map[4]],    # state 4
            [0.8, categorical_color_map[5]],    # state 5
            [1.0, categorical_color_map[5]]     # state 5
        ],
        zmin=1,
        zmax=5,
        xgap=1,
        ygap=1,
        colorbar=dict(
            title="State",
            tickvals=[1, 2, 3, 4, 5],
            ticktext=[
                '1: equilibrium 1, periodic orbit 0',
                '2: equilibrium 2, periodic orbit 0',
                '3: equilibrium 0, periodic orbit 1',
                '4: equilibrium 1, periodic orbit 1',
                '5: others'
            ]
        )
    ))

    # adjust layout
    fig.update_layout(
        title="Parameter Region Analysis",
        xaxis=dict(
            title="S",
            showgrid=True,
            gridwidth=1,
            gridcolor='LightGray'
        ),
        yaxis=dict(
            title="Q",
            showgrid=True,
            gridwidth=1,
            gridcolor='LightGray'
        ),
        width=1000,
        height=800,
        plot_bgcolor='white'
    )

    # centerize cell
    fig.update_yaxes(scaleanchor="x", scaleratio=1)

    # show plot
    fig.show()



def match_rate(csv_a: str, csv_b: str) -> None:
    a = pd.read_csv(csv_a, usecols=["Q","S","state"])
    b = pd.read_csv(csv_b, usecols=["Q","S","state"])

    # float揺れ対策（必要なら桁数は調整）
    a["Q"] = a["Q"].round(6); a["S"] = a["S"].round(6)
    b["Q"] = b["Q"].round(6); b["S"] = b["S"].round(6)

    m = a.merge(b, on=["Q","S"], how="inner", suffixes=("_a","_b"))
    rate = (m["state_a"].to_numpy() == m["state_b"].to_numpy()).mean() if len(m) else float("nan")

    print(f"matched rows (by Q,S): {len(m)}")
    print(f"only in A: {len(a) - len(m)}   only in B: {len(b) - len(m)}")
    print(f"state match rate: {rate*100:.6f}")


def match_rate_get_df(csv_a: str, df: pd.DataFrame) -> None:
    a = pd.read_csv(csv_a, usecols=["Q","S","state"])
    b = df[["Q", "S", "state"]].copy()

    # float揺れ対策（必要なら桁数は調整）
    a["Q"] = a["Q"].round(6); a["S"] = a["S"].round(6)
    b["Q"] = b["Q"].round(6); b["S"] = b["S"].round(6)

    m = a.merge(b, on=["Q","S"], how="inner", suffixes=("_a","_b"))
    rate = (m["state_a"].to_numpy() == m["state_b"].to_numpy()).mean() if len(m) else float("nan")

    return rate

if __name__ == "__main__":

    # set 1 (ode)
    ode_set1 = r"c:\Storage\02_paper\04_2025_Nolta journal\04_Python\data\results\set 1\forward euler\results\parameter region\20260108095815.csv"      # t = [400, 700]
    ode_set1_2 = r"c:\Storage\02_paper\04_2025_Nolta journal\04_Python\data\results\set 1\forward euler\results\parameter region\20260112155128.csv"    # t = [1000, 1500]

    # set 2 (ode)
    ode_set2 = r"c:\Storage\02_paper\04_2025_Nolta journal\04_Python\data\results\set 2\forward euler\results\parameter region\20260108101541.csv"
    ode_set2_2 = r"c:\Storage\02_paper\04_2025_Nolta journal\04_Python\data\results\set 2\forward euler\results\parameter region\20260112160036.csv"

    # set 1 (rotated ECA)
    rotated_eca_set1 = r"c:\Storage\02_paper\04_2025_Nolta journal\04_Python\data\results\set 1\rotated-LUT CA\results\parameter region\20260112164116.csv"

    # set 2 (rotated ECA)
    rotated_eca_set2 = r"c:\Storage\02_paper\04_2025_Nolta journal\04_Python\data\results\set 2\rotated-LUT CA\results\parameter region\20260112163022.csv"

    # set 1 (normal ECA)
    normal_eca_set1 = r"c:\Storage\02_paper\04_2025_Nolta journal\04_Python\data\results\set 1\ergodic CA\results\parameter region\20260112162234.csv"

    # set 2 (normal ECA)
    normal_eca_set2 =r"c:\Storage\02_paper\04_2025_Nolta journal\04_Python\data\results\set 2\ergodic CA\results\parameter region\20260112162559.csv"

    filepath = rotated_eca_set2

    graphic_pr(filepath)


    #match_rate(ode_set1, rotated_eca_set1)     # 96.72 %
    match_rate(ode_set1_2, normal_eca_set1)     # 95.39 %   X*Y = 16*16 （間引き⇒１分）
    #match_rate(ode_set2, rotated_eca_set2)     # 92.52 %
    #match_rate(ode_set2, normal_eca_set2)      # 92.02 %