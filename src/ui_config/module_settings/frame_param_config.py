# -*- coding: utf-8 -*-

"""
Title: frame_settings > param configure

@author: shirafujilab

Created on: 2024-11-14
Updated on: 2026-02-26


"""

# import standard library
import tkinter as tk
from tkinter import ttk

# import my libraries
from src.utils.json_import import json_import
from src.utils.param_resolver import param_resolver


class FrParamConfig:

    def  __init__(self, master, fr):

        # get master
        self.master = master

        # set up
        self.set_param_config(fr)


    def set_param_config(self, row_fr):

        """ Preset """

        # Title
        title = ttk.Label(row_fr, text="Parameters")
        title.grid(row=5, column=0, padx=2,  pady=2, sticky="nsew")

        # master frame
        fr = ttk.Frame(row_fr, style="Custom1.TFrame")
        fr.grid(row=6, column=0, padx=2,  pady=2, sticky="nsew")


        # row 0 (bifurcation parameters)
        fr1 = ttk.Frame(fr, style= "Custom2.TFrame") # Custom2.TFrame does not have frames
        fr1.grid(row=7, column=0, padx=2, pady=2, sticky="nsew")
        self.set_bif_param_frame(fr1)

        # row 1 (ESL parameters)
        fr2 = ttk.Frame(fr, style="Custom2.TFrame")
        fr2.grid(row=8, column=0, padx=2, pady=2, sticky="nsew")
        self.set_ca_param_frame(fr2)

        # row 2 (simulation parameters)
        fr3 = ttk.Frame(fr, style="Custom2.TFrame")
        fr3.grid(row=9, column=0, padx=2, pady=2, sticky="nsew")
        self.set_sim_param_frame(fr3)


    def set_bif_param_frame(self, fr):

        """ Setting: Bifurcation Parameters """
        title = ttk.Label(fr, text="Bifurcation Parameter", style = "Custom1.TLabel")
        title.grid(row=0, column=0, columnspan=4, padx=2,  pady=2, sticky=tk.W)

        # Set column width
        fr_col_config = [20, 20, 20, 20]
        for i, width in enumerate(fr_col_config):
            fr.columnconfigure(i, minsize=width)

        atrs = ["I_ext", "g_s"]

        for index, n in enumerate(atrs):

            txt = ttk.Label(fr, text= n, style="Custom1.TLabel")
            txt.grid(row=1, column=index*2, padx=4, pady=2)

            entry = ttk.Entry(fr, width = 6)
            entry.grid(row=1, column=index*2+1, padx=4, pady=2)
            entry.insert(0, self.master.params[n])      # Default value

            self.master.entries[n] = entry



    def set_ca_param_frame(self, fr):

        """ Setting: CA parameters """
        text = ttk.Label(fr, text="CA parameters", style="Custom1.TLabel")
        text.grid(row=0, column=0, columnspan=3, padx=2, pady=2, sticky=tk.W)

        """ Resolutions of registers """

        fr1 = ttk.Frame(fr, style="Custom2.TFrame")
        fr1.grid(row=1, column=0, sticky=tk.W)

        atrs1 = [
                 ("M:", "Ms", 1, 0, "2**M= "),
                 ("N1:", "N1_s", 2, 0, "2**N1= "), ("s1:", "s1_s", 2, 3, "2**s1= "),
                 ("N2:", "N2_s", 3, 0, "2**N2= "), ("s2:", "s2_s", 3, 3, "2**s2= "),
                 ("N3:", "N3_s", 4, 0, "2**N3= "), ("s3:", "s3_s", 4, 3, "2**s3= "),
                ]

        for _, n in enumerate(atrs1):

            # label
            txt = ttk.Label(fr1, text= n[0], style="Custom1.TLabel")
            txt.grid(row=n[2], column=n[3], padx=6, pady=2, sticky=tk.W)

            # entry + stringvar (for trace)
            sv = tk.StringVar(value=self.master.params[n[1]])
            entry = ttk.Entry(fr1, width = 3, textvariable=sv)
            entry.grid(row=n[2], column=n[3]+1, padx=4, pady=2)
            sv.trace_add("write", lambda *args, sv=sv, key=n[1]: self.update_power_label(sv, key))
            self.master.string_var[n[1]]= sv

            # display the value
            string = n[4] + str(2 ** int(self.master.string_var[n[1]].get()))
            txt = ttk.Label(fr1, text= string, style="Custom1.TLabel")
            txt.grid(row=n[2], column=n[3]+2, padx=4, pady=2, sticky=tk.W)
            self.master.power_labels[n[1]] = txt

        """ Switch signals and Clock """
        fr2 = ttk.Frame(fr, style="Custom2.TFrame")
        fr2.grid(row=2, column=0, sticky=tk.W)

        atrs2 = [
                 ("Tc:", "Tc", 5, 0, ""),
                 ("Tx:", "Tx_rat", 6, 0, "Tx_sqrt"), ("Wx:", "Wx_rat", 6, 4, "Wx_sqrt"),
                 ("Ty:", "Ty_rat", 7, 0, "Ty_sqrt"), ("Wy:", "Wy_rat", 7, 4, "Wy_sqrt"),
                 ("Tz:", "Tz_rat", 8, 0, "Tz_sqrt"), ("Wz:", "Wz_rat", 8, 4, "Wz_sqrt"),
                ]

        for _, n in enumerate(atrs2):

            txt = ttk.Label(fr2, text= n[0], style="Custom1.TLabel")
            txt.grid(row=n[2], column=n[3], padx=6, pady=2, sticky=tk.W)

            entry1 = ttk.Entry(fr2, width = 8)
            entry1.grid(row=n[2], column=n[3]+1, padx=4, pady=2)
            entry1.insert(0, self.master.params[n[1]])

            self.master.entries[n[1]] = entry1

            if n[4] == "":
                pass
            else:
                txt = ttk.Label(fr2, text= "*√", style="Custom1.TLabel")
                txt.grid(row=n[2], column=n[3]+2, padx=6, pady=2, sticky=tk.W)

                entry2 = ttk.Entry(fr2, width = 2)
                entry2.grid(row=n[2], column=n[3]+3, padx=4, pady=2)
                entry2.insert(0, self.master.params[n[4]])
                self.master.entries[n[4]] = entry2




    def update_power_label(self, sv, key):

        value = sv.get()

        lut = {"Ms": "M",
               "N1_s": "N1", "s1_s": "s1",
               "N2_s": "N2", "s2_s": "s2",
               "N3_s": "N3", "s3_s": "s3"}

        try:
            result = 2 ** int(value)
            self.master.power_labels[key].config(text=f"2**{lut[key]}= {result}")

            # update self.master.params[N, M]
            self.master.params[lut[key]] = result
        except ValueError:
            self.master.power_labels[key].config(text="= ...")


    def set_sim_param_frame(self, fr):

        """ Preset """

        # Title
        title = ttk.Label(fr, text="Simulation Parameter", style="Custom1.TLabel")
        title.grid(row=0, column=0, columnspan=3, padx=2, pady=2, sticky=tk.W)

        # Set column width
        fr_column_setting = [30, 30, 30, 30]
        for index, span in enumerate(fr_column_setting):
            fr.columnconfigure(index, minsize=span)

        """ Setting: Simulation Condition """

        atrs = ["sT", "eT", "h"]

        for index, name in enumerate(atrs):

            txt = ttk.Label(fr, text = name, style = "Custom1.TLabel")
            txt.grid(row=1, column=index*2, padx=4, pady=2, sticky="nsew")

            entry = ttk.Entry(fr, width=6)
            entry.grid(row=1, column=index*2+1, padx=4, pady=2)
            entry.insert(0, self.master.params[name])      # Default value

            self.master.entries[name] = entry