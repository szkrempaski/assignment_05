import pandas as pd

from .history import add_clean_columns, add_date_parts, combine_exports
def format_name(names: pd.Series) -> pd.Series:
    # (docstring)
    parts = names.str.split(",")
    return parts.str[1].str.strip() + " " + parts.str[0].str.strip()


def add_roster(history: pd.DataFrame, employees: pd.DataFrame) -> pd.DataFrame:
    # (docstring)
    roster = employees[["employee_id", "name", "department"]].copy()
    roster["display_name"] = format_name(roster["name"])
    roster = roster[["employee_id", "display_name", "department"]]
    return history.merge(roster, on="employee_id", how="left")


def build_history(exports: list, employees: pd.DataFrame) -> pd.DataFrame:
    # (docstring)
    history = combine_exports(exports)
    history = add_clean_columns(history)
    history = add_date_parts(history)
    return add_roster(history, employees)


def summarize_employees(history: pd.DataFrame) -> pd.DataFrame:
    # (docstring)
    summary = (
        history.groupby(["employee_id", "display_name", "department"])
        .agg(
            weeks_paid=("week_ending", "count"),
            total_hours=("hours_worked", "sum"),
            total_pay=("gross_pay", "sum"),
            avg_hours=("hours_worked", "mean"),
            overtime_weeks=("hours_worked", lambda h: (h > 40.0).sum()),
        )
        .reset_index()
    )
    return summary.sort_values("employee_id").reset_index(drop=True)