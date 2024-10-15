"""
coding: utf-8

Created on Thu Nov 30 13:52

@author: SLab

BCSwitch controller
"""

#Libralies
import tkinter as tk
from tkinter import ttk
import csv
import numpy as np
import sys
from lib.graphic_basic import Graphic

#Local Libralies
from SLabBCSwitch import BCSwitch as control
from ode_basic import BCSwitch as ode
from eca_basic import BSwitch as eca
from analysis_bif import Bif


# BCSwitch Controller GUI
class BCSwitchGUI:
    def __init__(self, root):
        self.root = root
        root.title("BCSwitch Controller")

        # Column 1: Model, Target, Graphics
        ttk.Label(root, text="Model:").grid(row=1, column=0)
        self.model = ttk.Combobox(root, values=["0", "1"])
        self.model.grid(row=2, column=0)
        self.model.set("0")  # Default value

        ttk.Label(root, text="Target:").grid(row=3, column=0)
        self.target = ttk.Combobox(root, values=["0", "1", "2", "3", "4"])
        self.target.grid(row=4, column=0)
        self.target.set("0")  # Default value

        ttk.Label(root, text="Enable Graphics:").grid(row=5, column=0)
        self.graphic = tk.BooleanVar(value=True)
        ttk.Checkbutton(root, variable=self.graphic).grid(row=6, column=0)
        
        # Column 2: Bifp
        ttk.Label(root, text="Bifp").grid(row=0, column=1)
        ttk.Label(root, text="Q1:").grid(row=1, column=1)
        self.bifp_Q1 = tk.Entry(root)
        self.bifp_Q1.grid(row=2, column=1)
        self.bifp_Q1.insert(0, "0.5")  # Default value

        ttk.Label(root, text="S:").grid(row=3, column=1)
        self.bifp_S = tk.Entry(root)
        self.bifp_S.grid(row=4, column=1)
        self.bifp_S.insert(0, "0.5")  # Default value

        # Column 3: Cap
        ttk.Label(root, text="Cap").grid(row=0, column=2)
        ttk.Label(root, text="s:").grid(row=1, column=2)
        self.cap_s = tk.Entry(root)
        self.cap_s.grid(row=2, column=2)
        self.cap_s.insert(0, "6")  # Default value
        ttk.Button(root, text="Set s", command=self.set_s_values).grid(row=3, column=2)

        ttk.Label(root, text="N:").grid(row=4, column=2)
        self.cap_N = tk.Entry(root)
        self.cap_N.grid(row=5, column=2)
        self.cap_N.insert(0, "64")  # Default value for 2**6

        ttk.Label(root, text="M:").grid(row=6, column=2)
        self.cap_M = tk.Entry(root)
        self.cap_M.grid(row=7, column=2)
        self.cap_M.insert(0, "64")  # Default value for 2**6

        ttk.Label(root, text="s1:").grid(row=8, column=2)
        self.cap_s1 = tk.Entry(root)
        self.cap_s1.grid(row=9, column=2)
        self.cap_s1.insert(0, "64")  # Default value for 2**6

        ttk.Label(root, text="s2:").grid(row=10, column=2)
        self.cap_s2 = tk.Entry(root)
        self.cap_s2.grid(row=11, column=2)
        self.cap_s2.insert(0, "64")  # Default value for 2**6

        ttk.Label(root, text="Tc:").grid(row=12, column=2)
        self.cap_Tc = tk.Entry(root)
        self.cap_Tc.grid(row=13, column=2)
        self.cap_Tc.insert(0, "0.01")  # Default value

        ttk.Label(root, text="Tx (Real):").grid(row=14, column=2)
        self.cap_Tx_real = tk.Entry(root)
        self.cap_Tx_real.grid(row=15, column=2)
        self.cap_Tx_real.insert(0, "0.01")  # Default value

        ttk.Label(root, text="Tx (Irrational):").grid(row=16, column=2)
        self.cap_Tx_irr = tk.Entry(root)
        self.cap_Tx_irr.grid(row=17, column=2)
        self.cap_Tx_irr.insert(0, "1.713")  # Default value

        ttk.Label(root, text="Ty (Real):").grid(row=18, column=2)
        self.cap_Ty_real = tk.Entry(root)
        self.cap_Ty_real.grid(row=19, column=2)
        self.cap_Ty_real.insert(0, "0.01")  # Default value

        ttk.Label(root, text="Ty (Irrational):").grid(row=20, column=2)
        self.cap_Ty_irr = tk.Entry(root)
        self.cap_Ty_irr.grid(row=21, column=2)
        self.cap_Ty_irr.insert(0, "2.313")  # Default value

        # Column 4: Simulation Condition
        ttk.Label(root, text="Simulation Condition").grid(row=0, column=3)

        ttk.Label(root, text="sT:").grid(row=1, column=3)
        self.simp_sT = tk.Entry(root)
        self.simp_sT.grid(row=2, column=3)
        self.simp_sT.insert(0, "0")  # Default value

        ttk.Label(root, text="eT:").grid(row=3, column=3)
        self.simp_eT = tk.Entry(root)
        self.simp_eT.grid(row=4, column=3)
        self.simp_eT.insert(0, "10")  # Default value

        ttk.Label(root, text="h (step):").grid(row=5, column=3)
        self.simp_h = tk.Entry(root)
        self.simp_h.grid(row=6, column=3)
        self.simp_h.insert(0, "0.01")  # Default value

        # Column 5: Initial Variables
        ttk.Label(root, text="Initial Variables").grid(row=0, column=4)

        ttk.Label(root, text="x:").grid(row=1, column=4)
        self.val_init_x = tk.Entry(root)
        self.val_init_x.grid(row=2, column=4)
        self.val_init_x.insert(0, "19")  # Default value

        ttk.Label(root, text="y:").grid(row=3, column=4)
        self.val_init_y = tk.Entry(root)
        self.val_init_y.grid(row=4, column=4)
        self.val_init_y.insert(0, "30")  # Default value

        ttk.Label(root, text="p:").grid(row=5, column=4)
        self.val_init_p = tk.Entry(root)
        self.val_init_p.grid(row=6, column=4)
        self.val_init_p.insert(0, "0")  # Default value

        ttk.Label(root, text="q:").grid(row=7, column=4)
        self.val_init_q = tk.Entry(root)
        self.val_init_q.grid(row=8, column=4)
        self.val_init_q.insert(0, "0")  # Default value

        # Run Simulation Button
        ttk.Button(root, text="Run Simulation", command=self.run_simulation).grid(row=7, column=0)

        # End Protcol
        root.protocol("WM_DELETE_WINDOW", self.on_close)



    def run_simulation(self):
        model = int(self.model.get())
        target = int(self.target.get())
        graphic = self.graphic.get()

        # 分岐パラメータ
        Q1_hist = float(self.bifp_Q1.get())
        S_hist = float(self.bifp_S.get())
        bifp = {
            "Q1": Q1_hist,
            "S": S_hist,
        }

        # モデルのパラメータ
        mp = {
            "tau1": 1,
            "tau2": 1,
            "b1": lambda Q1=bifp["Q1"]: 0.13 * (1 + Q1),
            "b2": 0,
            "WE11": 3.9,
            "WE12": 0,
            "WE21": 3.0,
            "WE22": 3.0,
            "WI11": 0,
            "WI12": lambda Q1=bifp["Q1"]: 0.5 * Q1,
            "WI21": 0,
            "WI22": 0,
        }

        # システム（ECA）のパラメータ
        cap = {
            "N": float(self.cap_N.get()),
            "M": float(self.cap_M.get()),
            "s1": float(self.cap_s1.get()),
            "s2": float(self.cap_s2.get()),
            "Tc": float(self.cap_Tc.get()),
            "Tx": float(self.cap_Tx_real.get()) * (float(self.cap_Tx_irr.get())**(1/2)),
            "Ty": float(self.cap_Ty_real.get()) * (float(self.cap_Ty_irr.get())**(1/2)),
        }

        # シミュレーションのパラメータ
        simp = {
            "sT": float(self.simp_sT.get()),
            "eT": float(self.simp_eT.get()),
            "h": float(self.simp_h.get()),
        }

        # 初期値
        val_init = {
            "x": float(self.val_init_x.get()),
            "y": float(self.val_init_y.get()),
            "p": float(self.val_init_p.get()),
            "q": float(self.val_init_q.get()),
        }

        # BCSwitchインスタンスの作成（call for SLabBCSwitch.py）
        bcs = control(model, target, graphic, bifp, mp, cap, simp, val_init)
        bcs.select()  # 選択した操作の実行


    def set_s_values(self):
        s = int(self.cap_s.get())
        value = 2 ** s
        self.cap_N.delete(0, tk.END)
        self.cap_N.insert(0, str(value))
        self.cap_M.delete(0, tk.END)
        self.cap_M.insert(0, str(value))
        self.cap_s1.delete(0, tk.END)
        self.cap_s1.insert(0, str(value))
        self.cap_s2.delete(0, tk.END)
        self.cap_s2.insert(0, str(value))
        
    
    def on_close(self):
        print("end")
        
        #destory GUI
        self.root.quit()
        
        #end python process
        sys.exit()


    def parse_input(self, input_str):
        try:
            return eval(input_str)
        except:
            return input_str  # Default to string if eval fails



def main_GUI():
    root = tk.Tk()
    app = BCSwitchGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main_GUI()