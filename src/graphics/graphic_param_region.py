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



if __name__ == "__main__":

    """ ode: parameter region """

    # set 1
    # filepath = r"c:\Storage\02_paper\03_2025_TEEE\04_Python\data\results\set 1\fem\results\parameter region\parameter_region_time_20241223103022.csv"

    # set 2
    # filepath = r"c:\Storage\02_paper\03_2025_TEEE\04_Python\data\results\set 2\fem\results\parameter region\parameter_region_time_20241223105451.csv"

    """ eca: parameter region """

    # set 1
    # filepath = r"c:\Storage\02_paper\03_2025_TEEE\04_Python\data\results\set 1\ErCA\condition_16\parameter region\parameter_region_time_20241225172601.csv"
    
    # set 2
    # filepath = r"c:\Storage\02_paper\03_2025_TEEE\04_Python\data\results\set 2\ErCA\condition_16\parameter region\parameter_region_time_20241225164159.csv"
    
    """ rca: parameter region """
    
    # set 1
    #filepath = r"c:\Storage\02_paper\03_2025_TEEE\04_Python\data\results\set 1\ErCA\condition_17\parameter region\parameter_region_time_20241226143134.csv"
    
    # set 2
    filepath = r"c:\Storage\02_paper\03_2025_TEEE\04_Python\data\results\set 2\ErCA\condition_17\parameter region\parameter_region_time_20241226152418.csv"
    
    graphic_pr(filepath)

    #graphic_pr(filepath)