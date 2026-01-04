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


def load_yaml_module() -> tuple[object | None, str | None]:
    try:
        import yaml  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dependency
        return None, f"PyYAML is required to load review records: {exc}"
    return yaml, None


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
    weekly = df.groupby("week", as_index=False)["hours"].sum().sort_values("week")
    monthly = df.groupby("month", as_index=False)["hours"].sum().sort_values("month")
    return weekly, monthly


def strip_numeric_values(value: object) -> object | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        cleaned_items = [strip_numeric_values(item) for item in value]
        cleaned_items = [item for item in cleaned_items if item is not None]
        return cleaned_items if cleaned_items else None
    if isinstance(value, dict):
        cleaned = {}
        for key, item in value.items():
            if isinstance(key, str) and key.lower() in {"score", "scores", "points"}:
                continue
            cleaned_item = strip_numeric_values(item)
            if cleaned_item is not None:
                cleaned[key] = cleaned_item
        return cleaned if cleaned else None
    return str(value)


def load_review_records(path: Path) -> tuple[list[dict[str, object]], list[str]]:
    if not path.exists():
        return [], [f"Reviews directory not found at {path}."]

    yaml_module, yaml_error = load_yaml_module()
    if yaml_error:
        return [], [yaml_error]

    review_files = sorted(path.rglob("*.yml")) + sorted(path.rglob("*.yaml"))
    if not review_files:
        return [], [f"No review records found under {path}."]

    records: list[dict[str, object]] = []
    errors: list[str] = []
    for review_file in review_files:
        try:
            raw_text = review_file.read_text(encoding="utf-8")
            data = yaml_module.safe_load(raw_text)
        except Exception as exc:  # pragma: no cover - runtime feedback
            errors.append(f"Unable to read {review_file}: {exc}")
            continue

        cleaned = strip_numeric_values(data)
        if cleaned is None:
            errors.append(f"Review file {review_file} has no displayable content.")
            continue

        records.append(
            {
                "path": str(review_file),
                "data": cleaned,
            }
        )

    return records, errors


def extract_text_section(record: dict[str, object], keys: list[str]) -> object | None:
    data = record.get("data")
    if not isinstance(data, dict):
        return None
    for key in keys:
        value = data.get(key)
        if value:
            return value
    return None


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

st.header("Review Records")
reviews_path = Path("reviews")
review_records, review_errors = load_review_records(reviews_path)
for message in review_errors:
    st.info(message)

if review_records:
    for record in review_records:
        st.subheader(Path(record["path"]).name)
        feedback = extract_text_section(record, ["feedback", "summary", "notes"])
        follow_ups = extract_text_section(record, ["follow_ups", "followups", "actions"])
        if feedback:
            st.markdown("**Feedback**")
            st.write(feedback)
        if follow_ups:
            st.markdown("**Follow-ups**")
            st.write(follow_ups)
        st.markdown("**Details (scores removed)**")
        st.json(record["data"])
