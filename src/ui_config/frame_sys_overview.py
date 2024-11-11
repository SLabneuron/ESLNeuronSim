# -*- coding: utf-8 -*-

"""

Created on: 2024-10-18

@author: SLab

Contents:

    System Dynamic Overview

    - phase plane and nullclines
    - equilibrium
    - eigenvalues of the Jacobian matlix  (linialization)
    - Lyapunov Conefficient

"""


# import standard libralies
import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


# import my library

from src.analyses.analysis_null_cline import Nullcline
from src.analyses.analysis_Jacobian import SolveNonlinear as SolN


class SysOverview:

    def __init__(self, master):

        # get parent class
        self.master = master

        # phase portrait
        self.fr_ni = None
        self.fr_ca = None


    def set_widget(self):

        # main frame
        fr = ttk.Frame(self.master.root)
        fr.grid(row=0, column=1, sticky = "nw")

        # title
        title = ttk.Label(fr, text="System Dynamic Overview")
        title.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")

        # set frame
        frame = ttk.Frame(fr, style="Custom1.TFrame")
        frame.grid(row=1, column=0, padx=2, pady=2, sticky = "nw")

        frame.columnconfigure(0, minsize=220)
        frame.columnconfigure(1, minsize=330)
        frame.rowconfigure(1, minsize=220)

        """ col 0: phase plane """
        self.phase_plain(frame)

        """ Event binding """

        # Set entry bind update
        self.master.combos["model"].bind("<<ComboboxSelected>>", lambda event: self.update_display())
        self.master.combos["param set"].bind("<<ComboboxSelected>>", lambda event: self.update_display(), add="+")

        self.master.entries["Q"].bind("<Return>", lambda event: self.update_display())
        self.master.entries["S"].bind("<Return>", lambda event: self.update_display())

        """ col 1: output console """
        self.output_console(frame)

        """ show init results """
        
        # show display
        self.update_display()



    def output_console(self, frame):

        # Title
        title = ttk.Label(frame, text="Output Console (Stability)", style="Custom1.TLabel")
        title.grid(row=0, column=1, padx=2, pady=2, sticky="nw")

        """ for output systematic information """

        # tree
        tree = ttk.Treeview(frame, columns=("No.", "coords", "lambda_1", "lambda_2", "state"), show="headings")

        # Configs: column header
        tree.heading("No.", text="No.")
        tree.heading("coords", text="coords")
        tree.heading("lambda_1", text="λ_1")
        tree.heading("lambda_2", text="λ_2")
        tree.heading("state", text="state")             # state \in [sink, source, saddle]

        # Configs: column widths
        tree.column("No.", width=30, anchor="center")
        tree.column("coords", width=120, anchor="center")
        tree.column("lambda_1",width=100, anchor="center")
        tree.column("lambda_2",width=100, anchor="center")
        tree.column("state", width=50, anchor="center")

        # Grid Tree
        tree.grid(row=1, column=1, padx=2, pady=2, sticky="nw")
        self.master.tables["sys overview"] = tree


    def fill_in_table(self, tree):

        # data case
        data =  [
            ["-", "-", "-",  "-", "-"],
            ["-", "-", "-",  "-", "-"],
            ["-", "-", "-",  "-", "-"],
            ["-", "-", "-",  "-", "-"],
            ["-", "-",  "-", "-", "-"]
        ]

        for i in range(len(self.results.ls)):
            data[i] = [f"{i}", f"({self.eset_x[i]:.3f},{self.eset_y[i]:.3f})",
                    f"{self.results.eigenvalues[i][0]:.3f}",
                    f"{self.results.eigenvalues[i][1]:.3f}",
                    f"{self.results.classifications[i]}"
                    ]

        # delete
        for item in tree.get_children():
            tree.delete(item)

        # Fill in
        for i, row in enumerate(data, 1):
            tree.insert("", tk.END, values=row)


    def phase_plain(self, frame):

        # Title
        title = ttk.Label(frame, text="Phase Plane", style="Custom1.TLabel")
        title.grid(row=0, column=0, padx=2, pady=2, sticky="nw")

        """ for neumerical integration """

        # master frame
        fr_ni = ttk.Frame(frame, style="Custom2.TFrame")

        # make plot space
        fig_ni = Figure(figsize=(2.2, 2.1), facecolor="lightgray", tight_layout=True)
        plt.rcParams.update({'font.size':8})

        # make canvas including fig
        canvas = FigureCanvasTkAgg(fig_ni, master = fr_ni)
        canvas.get_tk_widget().grid(row=0, column=0, padx=2, pady=2, sticky="wn")

        ax = fig_ni.add_subplot()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xlabel("Y")
        ax.set_ylabel("X")

        self.master.axes["ax_ni"] = ax

        """ for cellular automaton """

        # master frame
        fr_ca = ttk.Frame(frame, style="Custom2.TFrame")

        # make plot space
        fig_ca = Figure(figsize=(2.2, 2.1), facecolor="lightgray", tight_layout=True)
        plt.rcParams.update({'font.size':8})

        # make canvas including fig
        canvas = FigureCanvasTkAgg(fig_ca, master = fr_ca)
        canvas.get_tk_widget().grid(row=0, column=0, padx=2, pady=2, sticky="nw")

        ax = fig_ca.add_subplot()
        ax.set_xlim(0, self.master.params["N"])
        ax.set_ylim(0, self.master.params["N"])
        ax.set_xlabel("Y")
        ax.set_ylabel("X")

        self.master.axes["ax_ca"] = ax

        # store frames for later access
        self.fr_ni = fr_ni
        self.fr_ca = fr_ca


    def update_display(self):

        # Get the value from the Combobox widget
        mode = self.master.combos["model"].get()

        # Remove both frames initially
        self.fr_ni.grid_forget()
        self.fr_ca.grid_forget()

        # Calculate nullcline
        self.master.parameter_update()
        inst = Nullcline(self.master.params)

        # Set nullcline
        x1_null, x2_null = inst.nullcline_fx_x, inst.nullcline_fx_y
        y1_null, y2_null = inst.nullcline_fy_x, inst.nullcline_fy_y

        # Set equilibrium set
        self.eset_y = inst.equilibrium_points[:, 1]
        self.eset_x = inst.equilibrium_points[:, 0]

        """ Analysis results """

        # Analysis nonlinear characteristics
        self.results = SolN(self.eset_x, self.eset_y, self.master.params)

        # fill in tables
        self.fill_in_table(self.master.tables["sys overview"])

        """ Phase Plane """

        # Display the appropriate frame based on the mode
        if mode in ["fem", "rk4", "ode45"]:
            self.fr_ni.grid(row=1, column=0, padx=2, pady=2, sticky="nw")

            # graphics of nullcline
            ax= self.master.axes["ax_ni"]
            ax.clear()
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_xlabel("y")
            ax.set_ylabel("x")
            ax.scatter(x2_null, x1_null, marker=".", s=0.5)
            ax.scatter(y2_null, y1_null, marker=".", s=0.5)

            # set equilibrium
            for i in range(len(self.eset_x)):

                # sink
                if self.results.classifications[i] == "sink":
                    ax.scatter(self.eset_y[i], self.eset_x[i], marker="o", c="red", s= 20)

                # source
                elif self.results.classifications[i] == "source":
                    ax.scatter(self.eset_y[i], self.eset_x[i], marker="x", c="blue", s= 20)

                # saddle
                elif self.results.classifications[i] == "saddle":
                    ax.scatter(self.eset_y[i], self.eset_x[i], marker="^", c="green", s= 20)

            ax.figure.canvas.draw()


        elif mode in ["SynCA", "ErCA"]:
            self.fr_ca.grid(row=1, column=0, padx=2, pady=2, sticky="nw")

            # graphics of nullcline
            ax = self.master.axes["ax_ca"]
            ax.clear()
            ax.set_xlim(0, self.master.params["N"])
            ax.set_ylim(0, self.master.params["N"])
            ax.set_xlabel("Y")
            ax.set_ylabel("X")
            ax.scatter(x2_null*self.master.params["N"], x1_null*self.master.params["N"], marker=".", s=0.1)
            ax.scatter(y2_null*self.master.params["N"], y1_null*self.master.params["N"], marker=".", s=0.1)

            # set equilibrium
            for i in range(len(self.eset_x)):

                # sink
                if self.results.classifications[i] == "sink":
                    ax.scatter(self.eset_y[i]*self.master.params["s1"], self.eset_x[i]*self.master.params["s2"], marker="o", c="red", s= 20)

                # source
                elif self.results.classifications[i] == "source":
                    ax.scatter(self.eset_y[i]*self.master.params["s1"], self.eset_x[i]*self.master.params["s2"], marker="x", c="blue", s= 20)

                # saddle
                elif self.results.classifications[i] == "saddle":
                    ax.scatter(self.eset_y[i]*self.master.params["s1"], self.eset_x[i]*self.master.params["s2"], marker="^", c="green", s= 20)

            ax.figure.canvas.draw()

        else:
            pass


