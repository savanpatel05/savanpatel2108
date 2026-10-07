# HR Workload Analysis

Python desktop app that records employee work hours and analyzes workload, overtime, and unusual patterns.

## Features

- Add / store work-hour records in CSV
- Search and filter by employee, department, date range
- Totals, averages, and overtime (hours above 8/day)
- Compare employees and date periods
- Detect unusual patterns (very high days / statistical outliers)
- Two Matplotlib reports:
  1. Total hours by employee
  2. Overtime by department
- Tkinter GUI with input validation and error handling

## Project Structure (3+ modules)

| File | Role |
|------|------|
| `main.py` | Application entry point |
| `data_manager.py` | File storage, validation, search |
| `analyzer.py` | Totals, overtime, comparisons, patterns |
| `visualizations.py` | Matplotlib charts |
| `gui.py` | Tkinter user interface |
| `data/work_hours.csv` | Persistent sample data |
| `tests/test_analyzer.py` | Unit tests |

## Tech Used

- Python 3
- Pandas / NumPy
- Tkinter
- Matplotlib
- CSV file handling

## Setup (VS Code) — easy steps

1. Open folder: `File → Open Folder → hr_workload`
2. Open terminal: `Terminal → New Terminal`
3. Create virtual environment (first time only):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

4. Run the app:

```bash
python main.py
```

5. Run tests:

```bash
python -m unittest tests.test_analyzer
```

**Tip:** In VS Code, select the `.venv` Python interpreter  
(`Cmd+Shift+P` → “Python: Select Interpreter” → choose `.venv`).

## How to use

1. **Records tab** – add hours, filter, view table  
2. **Analysis tab** – summary, compare employees/periods, find unusual days  
3. **Visual Reports tab** – open the two charts  

## Overtime rule

Any hours worked **above 8 in a single day** count as overtime.

## Upload to GitHub

See the step-by-step guide in the parent folder notes, or:

```bash
cd hr_workload
git init
git add .
git commit -m "Initial HR Workload Analysis project"
gh repo create hr-workload-analysis --public --source=. --remote=origin --push
```
