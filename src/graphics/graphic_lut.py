# -*- coding: utf-8 -*-

"""

Title: graphic_lut

@author: shirafujilab

Created on: 2025-12-26

Memo:
    - LUT and Nullcline
    - For paper
    - Not tkinter


"""


import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

import numpy as np


def graphic_lut(params, x, y):

    """ set figure """
    fig = plt.figure(figsize=(5, 5), facecolor="white", tight_layout=True)
    ax = fig.add_subplot()

    ax.scatter(x, y, s=0.3)
    ax.add_collection(_plot_grid_from_XrYr(x, y))
    
    """ get params """
    N = params["N"]

    """ plot config """

    ax.set_xlim(0, N)
    ax.set_ylim(0, N)

    ax.set_xlabel("Y")
    ax.set_ylabel("X")

    #ax.set_xticks([0, N/4, N/2, 3*N/4, N])
    #ax.set_yticks([0, N/4, N/2, 3*N/4, N])
    #ax.minorticks_on()
    #ax.tick_params(axis="both", which="both", direction="in")

    #ax.grid(True, which="major", linewidth=0.8)
    #ax.grid(True, which="minor", linestyle=":", linewidth=0.5, alpha=0.5)



    plt.show()


def _make_rotated_coordinate(N, degree):

    x = np.arange(0, N, 1)
    y = np.arange(0, N, 1)

    X, Y = np.meshgrid(x, y, indexing="ij")

    cx, cy = max(x)/2, max(y)/2

    theta = degree * np.pi /180  # pi/180 [radian] = 1 [degress]

    R = np.array(
        [[np.cos(theta), -np.sin(theta)],
         [np.sin(theta), np.cos(theta)]])

    # centering for rotation
    P = np.stack([X-cx, Y-cy], axis=-1)
    P_rot = P @ R.T
    Xr = P_rot[..., 0] + cx
    Yr = P_rot[..., 1] + cy

    return Xr, Yr


def _plot_grid_from_XrYr(Xr, Yr, step=2, draw_points=False, lw=0.5, alpha=0.3):

    """
    Xr, Yr : coordinate of shape (N, N)
    step : grid lines (1 = "all", 2 = "Every othe one", 4 = "Every other 4")
    """

    N = Xr.shape[0]

    segs = []

    for i in range(0, N, step):
        pts = np.column_stack([Xr[i,:], Yr[i,:]]) # shape (N, 2)
        segs.append(pts)

    for j in range(0, N, step):
        pts = np.column_stack([Xr[:, j], Yr[:, j]]) # shape (N, 2)
        segs.append(pts)

    lc = LineCollection(segs, linewidth=lw, alpha=alpha)
    
    return lc


if __name__ == "__main__":

    params = {
        "N" : 64,
    }
    
    t = np.linspace(0, 2*np.pi, 200)
    #x = np.abs(np.sin(t))
    #y = np.abs(np.cos(2*t))
    
    x, y = _make_rotated_coordinate(params["N"], degree=1)
    
    graphic_lut(params, x, y)