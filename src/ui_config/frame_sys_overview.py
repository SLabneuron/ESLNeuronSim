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



# import my library

from src.analyses.analysis_null_cline import Nullcline
from src.analyses.analysis_Jacobian import SolveNonlinear as SolN

from src.graphics.graphic_phase_plain import GraphicPhasePlain as GraphicPP


class SysOverview:

    def __init__(self, master):

        # get parent class
        self.master = master

        # set widget
        self.set_widget()


    def set_widget(self):

        """ Config Main Frame of System Dynamic Overview """

        # main frame
        fr = ttk.Frame(self.master.root)
        fr.grid(row=0, column=1, sticky = "nw")

        # title
        title = ttk.Label(fr, text="System Dynamic Overview")
        title.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")

        # set frame
        frame = ttk.Frame(fr, style="Custom1.TFrame")
        frame.grid(row=1, column=0, padx=2, pady=2, sticky = "nw")

        # column and row configure
        frame.columnconfigure(0, minsize=220)
        frame.columnconfigure(1, minsize=440)
        frame.rowconfigure(1, minsize=220)

        """ Set Overview """

        # set phase plain including nullclines and node information (sink, source, saddle)
        self.phase_plain(frame)

        # set table for output console
        self.output_console(frame)


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

        """
        Summary:
            Create graphic space of vector field information

        return:
            self.master.axes["vfi"]

        """

        # Label
        title = ttk.Label(frame, text="Phase Plane", style="Custom1.TLabel")
        title.grid(row=0, column=0, padx=2, pady=2, sticky="nw")

        # Frame
        fr = ttk.Frame(frame, style="Custom2.TFrame")
        fr.grid(row=1, column=0, padx=2, pady=2)

        # Graph Space
        fig = Figure(figsize=(2.2, 2.1), facecolor="lightgray", tight_layout=True)

        # Add plot of phase_portrait
        ax = fig.add_subplot()

        # Canvas
        canvas = FigureCanvasTkAgg(fig, master = fr)
        canvas.get_tk_widget().grid(row=0, column=0, padx=2, pady=2, sticky="wn")

        # Store ax
        self.master.axes["vfi"] = ax


    def update_display(self):

        """ Calculate nullclines and nodes """

        # Calculate nullcline
        self.master.parameter_update()
        inst = Nullcline(self.master.params)

        # Set nullcline
        x1_null, x2_null = inst.nullcline_fx_x, inst.nullcline_fx_y
        y1_null, y2_null = inst.nullcline_fy_x, inst.nullcline_fy_y

        # Set equilibrium set
        self.eset_y = inst.equilibrium_points[:, 1]
        self.eset_x = inst.equilibrium_points[:, 0]

        # Analysis nonlinear characteristics
        self.results = SolN(self.eset_x, self.eset_y, self.master.params)

        # fill in tables
        self.fill_in_table(self.master.tables["sys overview"])

        """ Graphic """

        # Get mode
        axes = self.master.axes["vfi"]

        # Set Graph Space
        PP = GraphicPP(self.master, axes)

        # Plot nullclines
        PP.plot_nullcline(x2_null, x1_null, y2_null, y1_null)

        # Plot nodes (sink, source, saddle)
        PP.plot_nodes(self.eset_x, self.eset_y, self.results.classifications)

        # Graphics
        axes.figure.canvas.draw()


