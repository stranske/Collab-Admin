from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

TIME_LOG_COLUMNS = [
    "date",
    "hours",
    "repo",
    "issue_or_pr",
    "category",
    "description",
    "artifact_link",
]


def load_time_log(path: Path) -> tuple[pd.DataFrame | None, str | None]:
    if not path.exists():
        return None, f"Time log not found at {path}."

    try:
        df = pd.read_csv(path)
    except Exception as exc:  # pragma: no cover - streamlit runtime feedback
        return None, f"Unable to read time log: {exc}"

    if df.empty:
        return None, "Time log is empty."

    missing = [column for column in TIME_LOG_COLUMNS if column not in df.columns]
    if missing:
        return None, f"Time log missing columns: {', '.join(missing)}"

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["hours"] = pd.to_numeric(df["hours"], errors="coerce")
    valid = df.dropna(subset=["date", "hours"])
    if valid.empty:
        return None, "Time log has no valid rows after parsing."

    return valid, None


def aggregate_time_log(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    iso = df["date"].dt.isocalendar()
    df = df.assign(
        week=iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2),
        month=df["date"].dt.to_period("M").astype(str),
    )
    weekly = (
        df.groupby("week", as_index=False)["hours"].sum().sort_values("week")
    )
    monthly = (
        df.groupby("month", as_index=False)["hours"].sum().sort_values("month")
    )
    return weekly, monthly


st.set_page_config(page_title="Collab Dashboard", layout="wide")
st.title("Collab Dashboard (Tim private)")
st.write("Run locally. Do not publish numeric scoring.")

st.header("Time Tracking")
time_log_path = Path("logs/time_log.csv")
time_log_df, time_log_error = load_time_log(time_log_path)
if time_log_error:
    st.info(time_log_error)
else:
    weekly_totals, monthly_totals = aggregate_time_log(time_log_df)
    st.subheader("Weekly totals")
    st.dataframe(weekly_totals, use_container_width=True)
    st.bar_chart(weekly_totals.set_index("week"))
    st.subheader("Monthly totals")
    st.dataframe(monthly_totals, use_container_width=True)
    st.bar_chart(monthly_totals.set_index("month"))
