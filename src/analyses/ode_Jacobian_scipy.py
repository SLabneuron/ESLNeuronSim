import numpy as np
from scipy.optimize import fsolve

# パラメータの値
PARAMETERS_2A = {
    "tau1": 1, 
    "tau2": 1,
    "b1": 0.13*(1+0.54),
    "b2": 0,
    "WE11": 3.9,
    "WE12": 0,
    "WE21": 3.0,
    "WE22": 3.0,
    "WI11": 0,
    "WI12": 0.5*0.54,
    "WI21": 0,
    "WI22": 0,
    "S": 0.545
}

def equations(vars, params):
    x, y = vars
    tau1, tau2, b1, b2, WE11, WE12, WE21, WE22, WI11, WI12, WI21, WI22, S = params.values()
    fx = (1/tau1)*((b1*S+WE11*x**2+WE12*y**2)*(1-x)-(1+WI11*x**2+WI12*y**2)*x)
    fy = (1/tau2)*((b2*S+WE21*x**2+WE22*y**2)*(1-y)-(1+WI21*x**2+WI22*y**2)*y)
    return [fx, fy]

solutions = []

# 広範囲の初期値を試す
for x in np.linspace(0, 1, 20):
    for y in np.linspace(0, 1, 20):
        sol = fsolve(equations, (x, y), args=(PARAMETERS_2A))
        
        # 既存の解に十分近い場合はスキップ
        if any(np.allclose(sol, existing_sol, atol=1e-4) for existing_sol in solutions):
            continue
        
        solutions.append(sol)

for idx, sol in enumerate(solutions, 1):
    print(f"交点 {idx} (x, y): {sol}")
