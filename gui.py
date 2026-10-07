"""
gui.py
------
Tkinter GUI for the HR Workload Analysis application.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

import data_manager as dm
import analyzer as an
import visualizations as viz


class WorkloadApp(tk.Tk):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.title("HR Workload Analysis")
        self.geometry("980x680")
        self.minsize(860, 560)

        self._build_ui()
        self.refresh_table()

    # ------------------------------------------------------------------ UI
    def _build_ui(self) -> None:
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=8, pady=8)

        self.tab_records = ttk.Frame(notebook)
        self.tab_analysis = ttk.Frame(notebook)
        self.tab_reports = ttk.Frame(notebook)

        notebook.add(self.tab_records, text="Records")
        notebook.add(self.tab_analysis, text="Analysis")
        notebook.add(self.tab_reports, text="Visual Reports")

        self._build_records_tab()
        self._build_analysis_tab()
        self._build_reports_tab()

    def _build_records_tab(self) -> None:
        form = ttk.LabelFrame(self.tab_records, text="Add Work Hours", padding=10)
        form.pack(fill="x", padx=8, pady=8)

        labels = [
            ("Employee ID", "employee_id"),
            ("Employee Name", "employee_name"),
            ("Department", "department"),
            ("Date (YYYY-MM-DD)", "date"),
            ("Hours Worked", "hours"),
        ]
        self.inputs = {}
        for i, (text, key) in enumerate(labels):
            ttk.Label(form, text=text).grid(row=0, column=i, sticky="w", padx=4)
            entry = ttk.Entry(form, width=16)
            entry.grid(row=1, column=i, padx=4, pady=4)
            self.inputs[key] = entry

        ttk.Button(form, text="Add Record", command=self.add_record).grid(
            row=1, column=len(labels), padx=8
        )

        # Filter row
        filt = ttk.LabelFrame(self.tab_records, text="Search / Filter", padding=10)
        filt.pack(fill="x", padx=8, pady=4)

        ttk.Label(filt, text="Employee ID").grid(row=0, column=0, padx=4)
        self.filter_emp = ttk.Entry(filt, width=12)
        self.filter_emp.grid(row=0, column=1, padx=4)

        ttk.Label(filt, text="Department").grid(row=0, column=2, padx=4)
        self.filter_dept = ttk.Entry(filt, width=12)
        self.filter_dept.grid(row=0, column=3, padx=4)

        ttk.Label(filt, text="Start Date").grid(row=0, column=4, padx=4)
        self.filter_start = ttk.Entry(filt, width=12)
        self.filter_start.grid(row=0, column=5, padx=4)

        ttk.Label(filt, text="End Date").grid(row=0, column=6, padx=4)
        self.filter_end = ttk.Entry(filt, width=12)
        self.filter_end.grid(row=0, column=7, padx=4)

        ttk.Button(filt, text="Apply Filter", command=self.apply_filter).grid(
            row=0, column=8, padx=6
        )
        ttk.Button(filt, text="Show All", command=self.refresh_table).grid(
            row=0, column=9, padx=6
        )

        # Table
        table_frame = ttk.Frame(self.tab_records)
        table_frame.pack(fill="both", expand=True, padx=8, pady=8)

        columns = ("employee_id", "employee_name", "department", "date", "hours_worked")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=16)
        headings = {
            "employee_id": "ID",
            "employee_name": "Name",
            "department": "Department",
            "date": "Date",
            "hours_worked": "Hours",
        }
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=120, anchor="center")

        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def _build_analysis_tab(self) -> None:
        top = ttk.Frame(self.tab_analysis, padding=10)
        top.pack(fill="x")

        ttk.Button(top, text="Overall Summary", command=self.show_overall).pack(
            side="left", padx=4
        )
        ttk.Button(top, text="By Employee", command=self.show_by_employee).pack(
            side="left", padx=4
        )
        ttk.Button(top, text="Unusual Patterns", command=self.show_unusual).pack(
            side="left", padx=4
        )

        # Compare employees
        cmp_emp = ttk.LabelFrame(
            self.tab_analysis, text="Compare Two Employees", padding=10
        )
        cmp_emp.pack(fill="x", padx=8, pady=6)
        ttk.Label(cmp_emp, text="Employee A ID").pack(side="left", padx=4)
        self.cmp_a = ttk.Entry(cmp_emp, width=10)
        self.cmp_a.pack(side="left", padx=4)
        ttk.Label(cmp_emp, text="Employee B ID").pack(side="left", padx=4)
        self.cmp_b = ttk.Entry(cmp_emp, width=10)
        self.cmp_b.pack(side="left", padx=4)
        ttk.Button(cmp_emp, text="Compare", command=self.compare_employees).pack(
            side="left", padx=8
        )

        # Compare periods
        cmp_per = ttk.LabelFrame(
            self.tab_analysis, text="Compare Two Periods (YYYY-MM-DD)", padding=10
        )
        cmp_per.pack(fill="x", padx=8, pady=6)
        for label, attr in [
            ("P1 Start", "p1s"),
            ("P1 End", "p1e"),
            ("P2 Start", "p2s"),
            ("P2 End", "p2e"),
        ]:
            ttk.Label(cmp_per, text=label).pack(side="left", padx=3)
            entry = ttk.Entry(cmp_per, width=11)
            entry.pack(side="left", padx=3)
            setattr(self, attr, entry)
        ttk.Button(cmp_per, text="Compare Periods", command=self.compare_periods).pack(
            side="left", padx=8
        )

        self.analysis_text = tk.Text(self.tab_analysis, wrap="word", height=22)
        self.analysis_text.pack(fill="both", expand=True, padx=8, pady=8)

    def _build_reports_tab(self) -> None:
        buttons = ttk.Frame(self.tab_reports, padding=10)
        buttons.pack(fill="x")

        ttk.Button(
            buttons,
            text="Report 1: Hours by Employee",
            command=self.report_hours,
        ).pack(side="left", padx=6)
        ttk.Button(
            buttons,
            text="Report 2: Overtime by Department",
            command=self.report_overtime,
        ).pack(side="left", padx=6)

        self.chart_frame = ttk.Frame(self.tab_reports)
        self.chart_frame.pack(fill="both", expand=True, padx=8, pady=8)

    # ---------------------------------------------------------- Actions
    def _write_analysis(self, text: str) -> None:
        self.analysis_text.delete("1.0", tk.END)
        self.analysis_text.insert(tk.END, text)

    def _fill_table(self, df) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        if df is None or df.empty:
            return
        view = df.copy()
        if "date" in view.columns:
            view["date"] = view["date"].astype(str).str.slice(0, 10)
        for _, row in view.iterrows():
            self.tree.insert(
                "",
                tk.END,
                values=(
                    row["employee_id"],
                    row["employee_name"],
                    row["department"],
                    row["date"],
                    f"{float(row['hours_worked']):.1f}",
                ),
            )

    def refresh_table(self) -> None:
        try:
            df = dm.load_records()
            self._fill_table(df)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def add_record(self) -> None:
        try:
            dm.add_record(
                self.inputs["employee_id"].get(),
                self.inputs["employee_name"].get(),
                self.inputs["department"].get(),
                self.inputs["date"].get(),
                self.inputs["hours"].get(),
            )
            for entry in self.inputs.values():
                entry.delete(0, tk.END)
            self.refresh_table()
            messagebox.showinfo("Success", "Record added successfully.")
        except dm.DataValidationError as exc:
            messagebox.showwarning("Validation", str(exc))
        except Exception as exc:
            messagebox.showerror("Error", f"Could not add record:\n{exc}")

    def apply_filter(self) -> None:
        try:
            df = dm.filter_records(
                employee_id=self.filter_emp.get() or None,
                department=self.filter_dept.get() or None,
                start_date=self.filter_start.get() or None,
                end_date=self.filter_end.get() or None,
            )
            self._fill_table(df)
        except dm.DataValidationError as exc:
            messagebox.showwarning("Validation", str(exc))
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def show_overall(self) -> None:
        try:
            df = dm.load_records()
            stats = an.summary_stats(df)
            self._write_analysis(
                an.format_summary(stats, "Overall Workload Summary")
                + "\n\nRule: overtime = hours above 8 per day."
            )
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def show_by_employee(self) -> None:
        try:
            df = dm.load_records()
            summary = an.employee_summary(df)
            if summary.empty:
                self._write_analysis("No records found.")
                return
            lines = ["=== Workload by Employee ===\n"]
            for _, row in summary.iterrows():
                lines.append(
                    f"{row['employee_id']} | {row['employee_name']}\n"
                    f"  Days: {int(row['days_worked'])} | "
                    f"Total: {row['total_hours']:.2f}h | "
                    f"Avg: {row['avg_hours']:.2f}h | "
                    f"OT: {row['overtime_hours']:.2f}h\n"
                )
            self._write_analysis("\n".join(lines))
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def show_unusual(self) -> None:
        try:
            df = dm.load_records()
            unusual = an.find_unusual_patterns(df)
            if unusual.empty:
                self._write_analysis("No unusual patterns detected.")
                return
            lines = ["=== Unusual Patterns ===\n"]
            for _, row in unusual.iterrows():
                date_str = str(row["date"])[:10]
                lines.append(
                    f"{row['employee_id']} | {row['employee_name']} | "
                    f"{date_str} | {row['hours_worked']:.1f}h\n"
                    f"  Reason: {row['reason']}\n"
                )
            self._write_analysis("\n".join(lines))
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def compare_employees(self) -> None:
        try:
            a = self.cmp_a.get().strip()
            b = self.cmp_b.get().strip()
            if not a or not b:
                messagebox.showwarning("Validation", "Enter both employee IDs.")
                return
            df = dm.load_records()
            result = an.compare_employees(df, a, b)
            parts = []
            for emp_id, stats in result.items():
                parts.append(an.format_summary(stats, f"Employee {emp_id}"))
            self._write_analysis("\n\n".join(parts))
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def compare_periods(self) -> None:
        try:
            start1, end1 = self.p1s.get().strip(), self.p1e.get().strip()
            start2, end2 = self.p2s.get().strip(), self.p2e.get().strip()
            if not all([start1, end1, start2, end2]):
                messagebox.showwarning("Validation", "Fill all four dates.")
                return
            df = dm.load_records()
            result = an.compare_periods(df, start1, end1, start2, end2)
            parts = []
            for label, stats in result.items():
                parts.append(an.format_summary(stats, f"Period: {label}"))
            self._write_analysis("\n\n".join(parts))
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def report_hours(self) -> None:
        try:
            df = dm.load_records()
            viz.plot_hours_by_employee(df, parent=self.chart_frame)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def report_overtime(self) -> None:
        try:
            df = dm.load_records()
            viz.plot_overtime_by_department(df, parent=self.chart_frame)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))


def run_app() -> None:
    """Start the GUI application."""
    dm.ensure_data_file()
    app = WorkloadApp()
    app.mainloop()
