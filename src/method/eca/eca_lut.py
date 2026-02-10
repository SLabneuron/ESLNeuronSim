


import numpy as np
from src.method.eca.eca_basic import _make_lut_numba, _make_rotated_lut_numba
from src.graphics.graphic_lut import _make_rotated_coordinate


def make_lut_for_verilog(params, filename, mode):

    """ configuration"""

    # inits
    x = np.arange(0, params["N"], 1, dtype=np.int16)
    y = np.arange(0, params["N"], 1, dtype=np.int16)

    # meshgrid -> 1d
    xx_mesh, yy_mesh = np.meshgrid(x, y, indexing = "ij")
    xx, yy = xx_mesh.flatten(), yy_mesh.flatten()

    # parameters
    sT, eT = 300, 500
    tau1, b1, S, WE11, WE12, WI11, WI12 = params['tau1'], params['b1'], params['S'], params['WE11'], params['WE12'], params['WI11'], params['WI12']
    tau2, b2, WE21, WE22, WI21, WI22 = params['tau2'], params['b2'], params['WE21'], params['WE22'], params['WI21'], params['WI22']
    N, M, s1, s2, gamma_X, gamma_Y, Tc, Tx, Ty = params["N"], params["M"], params["s1"], params["s2"], params["gamma_X"], params["gamma_Y"], params["Tc"], params["Tx"], params["Ty"]
    deg = params["deg"]

    rotated_x, rotated_y =_make_rotated_coordinate(N, deg) # (size, degree)


    if mode == "rotated":
        F, G = _make_rotated_lut_numba(N, M, s1, s2, gamma_X, gamma_Y, Tc, Tx, Ty,
                                       tau1, b1, S, WE11, WE12, WI11, WI12,
                                       tau2, b2, WE21, WE22, WI21, WI22,
                                       rotated_x, rotated_y, deg)
    else:
        F, G = _make_lut_numba(N, M, s1, s2, gamma_X, gamma_Y, Tc, Tx, Ty,
                               tau1, b1, S, WE11, WE12, WI11, WI12,
                               tau2, b2, WE21, WE22, WI21, WI22)


    F = np.clip(F, -params["M"]+1, params["M"]-1)
    G = np.clip(G, -params["M"]+1, params["M"]-1)

    print(F, G)

    with open(filename, "w") as f:

        for idx in range(N*N):

            x = idx // N
            y = idx % N

            print(f"Fmatrix[{x}][{y}]={F[x,y]};", file = f)
            print(f"Gmatrix[{x}][{y}]={G[x,y]};", file = f)


    print(filename)
