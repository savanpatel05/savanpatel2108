"""
analyzer.py
-----------
Workload analysis: totals, averages, overtime, comparisons,
and unusual pattern detection using Pandas and NumPy.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd

# Business rule: regular day = 8 hours; anything above is overtime
STANDARD_DAILY_HOURS = 8.0
# Flag as unusual if hours are this many std-devs from the mean
UNUSUAL_Z_SCORE = 2.0


def _with_overtime(df: pd.DataFrame) -> pd.DataFrame:
    """Add overtime_hours column based on STANDARD_DAILY_HOURS."""
    if df.empty:
        return df.copy()
    out = df.copy()
    out["overtime_hours"] = np.maximum(
        out["hours_worked"].to_numpy(dtype=float) - STANDARD_DAILY_HOURS, 0.0
    )
    return out


def summary_stats(df: pd.DataFrame) -> dict:
    """
    Calculate totals, averages and overtime for a set of records.
    Returns a dictionary of summary metrics.
    """
    if df is None or df.empty:
        return {
            "total_records": 0,
            "total_hours": 0.0,
            "average_hours": 0.0,
            "total_overtime": 0.0,
            "max_hours": 0.0,
            "min_hours": 0.0,
        }

    work = _with_overtime(df)
    hours = work["hours_worked"].to_numpy(dtype=float)
    overtime = work["overtime_hours"].to_numpy(dtype=float)

    return {
        "total_records": int(len(work)),
        "total_hours": float(np.sum(hours)),
        "average_hours": float(np.mean(hours)),
        "total_overtime": float(np.sum(overtime)),
        "max_hours": float(np.max(hours)),
        "min_hours": float(np.min(hours)),
    }


def employee_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Group by employee and return totals / averages / overtime."""
    if df is None or df.empty:
        return pd.DataFrame(
            columns=[
                "employee_id",
                "employee_name",
                "total_hours",
                "avg_hours",
                "overtime_hours",
                "days_worked",
            ]
        )

    work = _with_overtime(df)
    grouped = (
        work.groupby(["employee_id", "employee_name"], as_index=False)
        .agg(
            total_hours=("hours_worked", "sum"),
            avg_hours=("hours_worked", "mean"),
            overtime_hours=("overtime_hours", "sum"),
            days_worked=("date", "count"),
        )
        .sort_values("total_hours", ascending=False)
    )
    return grouped.reset_index(drop=True)


def department_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Group by department for comparison reports."""
    if df is None or df.empty:
        return pd.DataFrame(
            columns=["department", "total_hours", "avg_hours", "overtime_hours"]
        )

    work = _with_overtime(df)
    grouped = (
        work.groupby("department", as_index=False)
        .agg(
            total_hours=("hours_worked", "sum"),
            avg_hours=("hours_worked", "mean"),
            overtime_hours=("overtime_hours", "sum"),
        )
        .sort_values("total_hours", ascending=False)
    )
    return grouped.reset_index(drop=True)


def compare_employees(
    df: pd.DataFrame, emp_a: str, emp_b: str
) -> dict:
    """Compare two employees' totals, averages and overtime."""
    emp_a = emp_a.strip().upper()
    emp_b = emp_b.strip().upper()

    a_df = df[df["employee_id"].str.upper() == emp_a]
    b_df = df[df["employee_id"].str.upper() == emp_b]

    return {
        emp_a: summary_stats(a_df),
        emp_b: summary_stats(b_df),
    }


def compare_periods(
    df: pd.DataFrame,
    start1: str,
    end1: str,
    start2: str,
    end2: str,
) -> dict:
    """Compare workload between two date ranges."""
    dates = pd.to_datetime(df["date"])
    p1 = df[(dates >= pd.to_datetime(start1)) & (dates <= pd.to_datetime(end1))]
    p2 = df[(dates >= pd.to_datetime(start2)) & (dates <= pd.to_datetime(end2))]

    return {
        f"{start1} to {end1}": summary_stats(p1),
        f"{start2} to {end2}": summary_stats(p2),
    }


def find_unusual_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identify unusual daily hours using z-score:
    |hours - mean| / std >= UNUSUAL_Z_SCORE
    Also flags any day with more than 12 hours.
    """
    if df is None or df.empty:
        return pd.DataFrame(
            columns=list(df.columns) + ["reason"] if df is not None else ["reason"]
        )

    work = df.copy()
    hours = work["hours_worked"].to_numpy(dtype=float)
    mean = float(np.mean(hours))
    std = float(np.std(hours))

    reasons = []
    keep = []
    for h in hours:
        reason_parts = []
        if h > 12:
            reason_parts.append("Very high day (>12h)")
        if std > 0 and abs(h - mean) / std >= UNUSUAL_Z_SCORE:
            reason_parts.append(f"Unusual vs average (z-score)")
        if reason_parts:
            keep.append(True)
            reasons.append("; ".join(reason_parts))
        else:
            keep.append(False)
            reasons.append("")

    work["reason"] = reasons
    unusual = work[np.array(keep)].copy()
    return unusual.reset_index(drop=True)


def format_summary(stats: dict, title: str = "Summary") -> str:
    """Pretty text for GUI / console."""
    lines = [
        f"=== {title} ===",
        f"Records         : {stats['total_records']}",
        f"Total hours     : {stats['total_hours']:.2f}",
        f"Average hours   : {stats['average_hours']:.2f}",
        f"Total overtime  : {stats['total_overtime']:.2f}",
        f"Max day hours   : {stats['max_hours']:.2f}",
        f"Min day hours   : {stats['min_hours']:.2f}",
    ]
    return "\n".join(lines)
