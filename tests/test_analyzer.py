"""
Simple tests for analyzer and data_manager modules.
Run from hr_workload folder:
    python -m unittest tests.test_analyzer
"""

import os
import sys
import tempfile
import unittest

# Allow importing project modules when running tests
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

import analyzer as an
import data_manager as dm


class TestAnalyzer(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame(
            {
                "employee_id": ["E001", "E001", "E002"],
                "employee_name": ["A", "A", "B"],
                "department": ["IT", "IT", "HR"],
                "date": pd.to_datetime(
                    ["2026-01-06", "2026-01-07", "2026-01-06"]
                ),
                "hours_worked": [8.0, 10.0, 8.0],
            }
        )

    def test_summary_stats(self):
        stats = an.summary_stats(self.df)
        self.assertEqual(stats["total_records"], 3)
        self.assertAlmostEqual(stats["total_hours"], 26.0)
        self.assertAlmostEqual(stats["total_overtime"], 2.0)  # 10-8

    def test_employee_summary(self):
        summary = an.employee_summary(self.df)
        self.assertEqual(len(summary), 2)
        e001 = summary[summary["employee_id"] == "E001"].iloc[0]
        self.assertAlmostEqual(e001["total_hours"], 18.0)

    def test_empty_summary(self):
        stats = an.summary_stats(pd.DataFrame())
        self.assertEqual(stats["total_records"], 0)

    def test_unusual_high_hours(self):
        df = self.df.copy()
        df.loc[len(df)] = ["E003", "C", "IT", pd.Timestamp("2026-01-08"), 14.0]
        unusual = an.find_unusual_patterns(df)
        self.assertFalse(unusual.empty)
        self.assertTrue((unusual["hours_worked"] == 14.0).any())


class TestDataManager(unittest.TestCase):
    def test_validate_good_record(self):
        record = dm.validate_record(
            "e005", "Test User", "IT", "2026-02-01", "8.5"
        )
        self.assertEqual(record["employee_id"], "E005")
        self.assertEqual(record["hours_worked"], 8.5)

    def test_validate_bad_hours(self):
        with self.assertRaises(dm.DataValidationError):
            dm.validate_record("E005", "Test", "IT", "2026-02-01", "30")

    def test_validate_bad_date(self):
        with self.assertRaises(dm.DataValidationError):
            dm.validate_record("E005", "Test", "IT", "01-02-2026", "8")


if __name__ == "__main__":
    unittest.main()
