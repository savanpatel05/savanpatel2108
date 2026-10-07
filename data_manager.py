"""
data_manager.py
---------------
Handles reading, writing, searching and validating work-hour records.
Uses CSV file storage and Pandas DataFrames.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

import pandas as pd

# Path to the CSV file (next to this package, inside data/)
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DATA_FILE = os.path.join(DATA_DIR, "work_hours.csv")

REQUIRED_COLUMNS = [
    "employee_id",
    "employee_name",
    "department",
    "date",
    "hours_worked",
]


class DataValidationError(ValueError):
    """Raised when user input fails validation."""


def ensure_data_file() -> None:
    """Create data folder and empty CSV if they do not exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        empty = pd.DataFrame(columns=REQUIRED_COLUMNS)
        empty.to_csv(DATA_FILE, index=False)


def load_records() -> pd.DataFrame:
    """Load all work-hour records from CSV into a DataFrame."""
    ensure_data_file()
    try:
        df = pd.read_csv(DATA_FILE)
        if df.empty:
            return pd.DataFrame(columns=REQUIRED_COLUMNS)
        # Normalize types
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["hours_worked"] = pd.to_numeric(df["hours_worked"], errors="coerce")
        df = df.dropna(subset=["employee_id", "date", "hours_worked"])
        return df
    except Exception as exc:
        raise RuntimeError(f"Could not load data file: {exc}") from exc


def save_records(df: pd.DataFrame) -> None:
    """Save DataFrame back to CSV."""
    ensure_data_file()
    out = df.copy()
    if not out.empty and pd.api.types.is_datetime64_any_dtype(out["date"]):
        out["date"] = out["date"].dt.strftime("%Y-%m-%d")
    out.to_csv(DATA_FILE, index=False)


def validate_record(
    employee_id: str,
    employee_name: str,
    department: str,
    date_str: str,
    hours_str: str,
) -> dict:
    """
    Validate one work-hour record.
    Returns a clean dictionary ready to append.
    Raises DataValidationError on bad input.
    """
    employee_id = (employee_id or "").strip()
    employee_name = (employee_name or "").strip()
    department = (department or "").strip()
    date_str = (date_str or "").strip()
    hours_str = (hours_str or "").strip()

    if not employee_id:
        raise DataValidationError("Employee ID is required.")
    if not employee_name:
        raise DataValidationError("Employee name is required.")
    if not department:
        raise DataValidationError("Department is required.")

    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError as exc:
        raise DataValidationError("Date must be in YYYY-MM-DD format.") from exc

    try:
        hours = float(hours_str)
    except ValueError as exc:
        raise DataValidationError("Hours worked must be a number.") from exc

    if hours <= 0 or hours > 24:
        raise DataValidationError("Hours worked must be between 0 and 24.")

    return {
        "employee_id": employee_id.upper(),
        "employee_name": employee_name,
        "department": department,
        "date": date_obj.strftime("%Y-%m-%d"),
        "hours_worked": hours,
    }


def add_record(
    employee_id: str,
    employee_name: str,
    department: str,
    date_str: str,
    hours_str: str,
) -> None:
    """Validate and append one new record to storage."""
    record = validate_record(
        employee_id, employee_name, department, date_str, hours_str
    )
    df = load_records()
    new_row = pd.DataFrame([record])
    new_row["date"] = pd.to_datetime(new_row["date"])
    df = pd.concat([df, new_row], ignore_index=True)
    save_records(df)


def filter_records(
    employee_id: Optional[str] = None,
    department: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Search/filter records by employee, department and date range."""
    df = load_records()
    if df.empty:
        return df

    if employee_id:
        df = df[df["employee_id"].str.upper() == employee_id.strip().upper()]

    if department:
        df = df[df["department"].str.lower() == department.strip().lower()]

    if start_date:
        start = pd.to_datetime(start_date, errors="coerce")
        if pd.isna(start):
            raise DataValidationError("Start date must be YYYY-MM-DD.")
        df = df[df["date"] >= start]

    if end_date:
        end = pd.to_datetime(end_date, errors="coerce")
        if pd.isna(end):
            raise DataValidationError("End date must be YYYY-MM-DD.")
        df = df[df["date"] <= end]

    return df.reset_index(drop=True)


def list_employees() -> list[str]:
    """Return sorted unique employee IDs."""
    df = load_records()
    if df.empty:
        return []
    return sorted(df["employee_id"].dropna().unique().tolist())


def list_departments() -> list[str]:
    """Return sorted unique departments."""
    df = load_records()
    if df.empty:
        return []
    return sorted(df["department"].dropna().unique().tolist())
