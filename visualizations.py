"""
visualizations.py
-----------------
Matplotlib charts for workload reports:
1) Total hours by employee (bar chart)
2) Overtime by department (bar chart)
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from analyzer import department_summary, employee_summary


def plot_hours_by_employee(df: pd.DataFrame, parent=None):
    """
    Report 1: Bar chart of total hours per employee.
    If parent is a Tkinter frame, embed the figure there.
    Otherwise show in a separate window.
    """
    summary = employee_summary(df)
    fig, ax = plt.subplots(figsize=(7, 4))

    if summary.empty:
        ax.text(0.5, 0.5, "No data to display", ha="center", va="center")
        ax.set_axis_off()
    else:
        labels = summary["employee_name"].tolist()
        values = summary["total_hours"].tolist()
        bars = ax.bar(labels, values, color="#2E86AB")
        ax.set_title("Total Work Hours by Employee")
        ax.set_xlabel("Employee")
        ax.set_ylabel("Total Hours")
        ax.tick_params(axis="x", rotation=20)
        for bar, val in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f"{val:.1f}",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    fig.tight_layout()
    return _show_or_embed(fig, parent)


def plot_overtime_by_department(df: pd.DataFrame, parent=None):
    """
    Report 2: Bar chart of overtime hours by department.
    """
    summary = department_summary(df)
    fig, ax = plt.subplots(figsize=(7, 4))

    if summary.empty:
        ax.text(0.5, 0.5, "No data to display", ha="center", va="center")
        ax.set_axis_off()
    else:
        labels = summary["department"].tolist()
        values = summary["overtime_hours"].tolist()
        bars = ax.bar(labels, values, color="#E94F37")
        ax.set_title("Overtime Hours by Department")
        ax.set_xlabel("Department")
        ax.set_ylabel("Overtime Hours")
        for bar, val in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f"{val:.1f}",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    fig.tight_layout()
    return _show_or_embed(fig, parent)


def _show_or_embed(fig, parent):
    """Embed in Tkinter if parent given, else plt.show()."""
    if parent is None:
        plt.show()
        return fig

    # Lazy import so module still works without GUI
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

    # Clear previous widgets in the chart frame
    for child in parent.winfo_children():
        child.destroy()

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    return fig
