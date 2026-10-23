# summarize.py
import pandas as pd

from payroll.history import (
    add_clean_columns,
    add_date_parts,
    combine_exports,
)


def format_name(names: pd.Series) -> pd.Series:
    parts = names.str.split(",")
    return parts.str[1].str.strip() + " " + parts.str[0].str.strip()


def add_roster(history: pd.DataFrame, employees: pd.DataFrame) -> pd.DataFrame:
    roster = employees[["employee_id", "name", "department"]].copy()
    roster["display_name"] = format_name(roster["name"])
    roster = roster[["employee_id", "display_name", "department"]]
    return history.merge(roster, on="employee_id", how="left")


def build_history(exports: list, employees: pd.DataFrame) -> pd.DataFrame:
    history = combine_exports(exports)
    history = add_clean_columns(history)
    history = add_date_parts(history)
    return add_roster(history, employees)


def summarize_employees(history: pd.DataFrame) -> pd.DataFrame: