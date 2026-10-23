# payroll_report_app.py
import pandas as pd
import streamlit as st

from payroll import (
    build_history,
    hours_grid,
    load_employees,
    load_export,
    missed_weeks,
    pay_by_month,
    summarize_employees,
)

st.title("Salt City Coffee — Quarterly Payroll Report")

employees = load_employees()
uploads = st.file_uploader(
    "Upload weekly payroll exports",
    type=["csv"],
    accept_multiple_files=True,
    key="exports",
)

if uploads:
    history = build_history([load_export(u) for u in uploads], employees)

    unmatched = history[history["department"].isna()]
    if not unmatched.empty:
        ids = ", ".join(sorted(unmatched["employeeid"].astype(str).unique()))
        st.warning(f"No department found for employeeid: {ids}")
        history = history[history["department"].notna()]

    departments = ["All"] + sorted(history["department"].unique())
    department = st.selectbox("Department", departments, key="department")

    first = history["pay_date"].min().date()
    last = history["pay_date"].max().date()
    dates = st.date_input(
        "Pay dates",
        value=(first, last),
        min_value=first,
        max_value=last,
        key="dates",
    )
    start, end = dates if len(dates) == 2 else (dates[0], dates[0])

    filtered = history[
        (history["pay_date"].dt.date >= start)
        & (history["pay_date"].dt.date <= end)
    ]
    if department != "All":
        filtered = filtered[filtered["department"] == department]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Weeks", filtered["week_ending"].nunique())
    col2.metric("Employees", filtered["employee_id"].nunique())
    col3.metric("Total hours", f"{filtered['hours_worked'].sum():,.2f}")
    col4.metric("Total gross pay", f"${filtered['gross_pay'].sum():,.2f}")

    monthly = pay_by_month(filtered)
    st.bar_chart(monthly, x="month")

    grid = hours_grid(filtered)
    st.dataframe(summarize_employees(filtered))
    st.dataframe(grid)
    st.dataframe(missed_weeks(grid))

    st.download_button(
        "Download pay by month (CSV)",
        data=monthly.to_csv(index=False),
        file_name="pay_by_month.csv",
        mime="text/csv",
        key="download",
    )