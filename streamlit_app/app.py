from __future__ import annotations

from pathlib import Path

import altair as alt
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

DEFAULT_WORKSTREAMS = [
    {"id": "ws1_trend", "name": "Trend_Model_Project"},
    {"id": "ws2_agents", "name": "Agent Integration"},
    {"id": "ws3_consumer", "name": "Consumer Usability"},
    {"id": "ws4_marketplace", "name": "Marketplace Plan"},
]

WORKSTREAM_DELIVERABLES = {
    "Trend_Model_Project": [
        "Analyze existing trend model implementation",
        "Document findings and recommendations",
        "Evidence references documented",
    ],
    "Agent Integration": [
        "Claude Code integrated as the next agent",
        "Third agent integrated (Aider/Continue/approved alt)",
        "Stable outputs contract for agent runs",
        "Docs-first future agent onboarding",
    ],
    "Consumer Usability": [
        "Two PRs reduce friction (not just docs)",
        "Workflows-level fixes evidenced when needed",
        "Friction log captured in logs/friction/YYYY-MM.csv",
    ],
    "Marketplace Plan": [
        "Two candidate platforms evaluated",
        "Evaluation rubric defined (time, reliability, security, maintainability, cost)",
        "Two-week execution schedule with exit criteria",
    ],
}

WEEKLY_CAP_HOURS = 40


def load_yaml_module() -> tuple[object | None, str | None]:
    try:
        import yaml  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dependency
        return None, f"PyYAML is required to load review records: {exc}"
    return yaml, None


def load_workstreams(path: Path) -> tuple[list[dict[str, str]], str | None]:
    if not path.exists():
        return DEFAULT_WORKSTREAMS, f"Workstream config not found at {path}."

    yaml_module, yaml_error = load_yaml_module()
    if yaml_error:
        return DEFAULT_WORKSTREAMS, yaml_error

    try:
        data = yaml_module.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - runtime feedback
        return DEFAULT_WORKSTREAMS, f"Unable to read workstream config: {exc}"

    workstreams = (
        data.get("project", {}).get("workstreams") if isinstance(data, dict) else None
    )
    if not isinstance(workstreams, list) or not workstreams:
        return DEFAULT_WORKSTREAMS, "Workstream config missing workstreams list."

    cleaned: list[dict[str, str]] = []
    for item in workstreams:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        ws_id = item.get("id")
        if isinstance(name, str) and isinstance(ws_id, str):
            cleaned.append({"id": ws_id, "name": name})

    return cleaned or DEFAULT_WORKSTREAMS, None


def normalize_workstream(value: str) -> str:
    return value.strip().lower().replace("_", " ")


def compute_workstream_progress(
    workstreams: list[dict[str, str]],
    review_records: list[dict[str, object]],
) -> tuple[pd.DataFrame, dict[str, list[tuple[str, str]]]]:
    counts: dict[str, int] = {ws["name"]: 0 for ws in workstreams}
    lookup = {}
    for ws in workstreams:
        lookup[normalize_workstream(ws["name"])] = ws["name"]
        lookup[normalize_workstream(ws["id"])] = ws["name"]
    for record in review_records:
        data = record.get("data")
        if not isinstance(data, dict):
            continue
        raw = data.get("workstream")
        if isinstance(raw, str):
            normalized = normalize_workstream(raw)
            if normalized in lookup:
                counts[lookup[normalized]] += 1

    rows = []
    deliverable_status: dict[str, list[tuple[str, str]]] = {}
    for workstream in workstreams:
        name = workstream["name"]
        deliverables = WORKSTREAM_DELIVERABLES.get(name, [])
        expected = max(len(deliverables), 1)
        completed = min(counts.get(name, 0), len(deliverables))
        completion = completed / expected
        rows.append(
            {
                "Workstream": name,
                "Deliverables complete": completed,
                "Deliverables total": expected,
                "Completion %": round(completion * 100, 1),
                "Reviews logged": counts.get(name, 0),
            }
        )
        status = []
        for index, deliverable in enumerate(deliverables):
            state = "Done" if index < completed else "Pending"
            status.append((deliverable, state))
        deliverable_status[name] = status

    return pd.DataFrame(rows), deliverable_status


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


def add_weekly_cap(weekly: pd.DataFrame, cap_hours: float) -> pd.DataFrame:
    capped = weekly.copy()
    capped["Cap hours"] = cap_hours
    capped["Remaining"] = (cap_hours - capped["hours"]).round(1)
    capped["Status"] = capped["hours"].apply(
        lambda hours: "Over cap" if hours > cap_hours else "Within cap"
    )
    return capped


def build_weekly_cap_chart(weekly: pd.DataFrame, cap_hours: float) -> alt.Chart:
    base = alt.Chart(weekly).encode(x=alt.X("week:N", title="Week"))
    bars = base.mark_bar().encode(
        y=alt.Y("hours:Q", title="Hours"),
        color=alt.Color(
            "Status:N",
            scale=alt.Scale(
                domain=["Within cap", "Over cap"], range=["#2a9d8f", "#e76f51"]
            ),
            legend=alt.Legend(title="Cap status"),
        ),
        tooltip=["week", "hours", "Status"],
    )
    cap_rule = (
        alt.Chart(pd.DataFrame({"Cap": [cap_hours]}))
        .mark_rule(color="#264653")
        .encode(y="Cap:Q")
    )
    return alt.layer(bars, cap_rule)


def is_numeric_string(value: str) -> bool:
    stripped = value.strip()
    if not stripped:
        return False
    try:
        float(stripped)
    except ValueError:
        return False
    return True


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
            if isinstance(key, str) and key.lower() in {"rating", "ratings"}:
                if isinstance(item, (int, float)):
                    continue
                if isinstance(item, str) and is_numeric_string(item):
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


def load_rubric_index(path: Path) -> tuple[list[Path], list[str]]:
    if not path.exists():
        return [], [f"Rubric index not found at {path}."]

    yaml_module, yaml_error = load_yaml_module()
    if yaml_error:
        return [], [yaml_error]

    try:
        data = yaml_module.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - runtime feedback
        return [], [f"Unable to read rubric index: {exc}"]

    entries = data.get("rubrics") if isinstance(data, dict) else None
    if not isinstance(entries, list) or not entries:
        return [], ["Rubric index missing list."]

    rubric_paths = []
    for entry in entries:
        if isinstance(entry, str):
            rubric_paths.append(path.parent / entry)
    return rubric_paths, []


def load_rubric_definitions(
    rubric_paths: list[Path],
) -> tuple[dict[str, dict[str, dict[str, str]]], list[str]]:
    if not rubric_paths:
        return {}, []

    yaml_module, yaml_error = load_yaml_module()
    if yaml_error:
        return {}, [yaml_error]

    errors: list[str] = []
    definitions: dict[str, dict[str, dict[str, str]]] = {}
    for rubric_path in rubric_paths:
        if not rubric_path.exists():
            errors.append(f"Rubric not found at {rubric_path}.")
            continue
        try:
            data = yaml_module.safe_load(rubric_path.read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - runtime feedback
            errors.append(f"Unable to read rubric {rubric_path}: {exc}")
            continue
        if not isinstance(data, dict):
            errors.append(f"Rubric {rubric_path} has invalid format.")
            continue
        raw_rubric_id = data.get("rubric_id")
        rubric_id = (
            raw_rubric_id if isinstance(raw_rubric_id, str) else rubric_path.stem
        )
        dims = (
            data.get("dimensions") if isinstance(data.get("dimensions"), list) else []
        )
        dim_lookup: dict[str, str] = {}
        for dim in dims:
            if not isinstance(dim, dict):
                continue
            dim_id = dim.get("id")
            dim_name = dim.get("name")
            if isinstance(dim_id, str) and isinstance(dim_name, str):
                dim_lookup[dim_id] = dim_name
        definitions[rubric_id] = {"dimensions": dim_lookup}
    return definitions, errors


def aggregate_dimension_ratings(
    review_records: list[dict[str, object]],
    rubric_definitions: dict[str, dict[str, dict[str, str]]],
) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    for record in review_records:
        data = record.get("data")
        if not isinstance(data, dict):
            continue
        ratings = data.get("dimension_ratings")
        if not isinstance(ratings, list):
            continue
        rubric_used = data.get("rubric_used")
        rubric_key = rubric_used if isinstance(rubric_used, str) else ""
        dim_lookup = rubric_definitions.get(rubric_key, {}).get("dimensions", {})
        for rating in ratings:
            if not isinstance(rating, dict):
                continue
            dim_id = rating.get("dimension")
            rating_value = rating.get("rating")
            if not isinstance(dim_id, str) or not isinstance(rating_value, str):
                continue
            if is_numeric_string(rating_value):
                continue
            dimension_name = dim_lookup.get(dim_id, dim_id)
            rows.append({"Dimension": dimension_name, "Rating": rating_value})

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    summary = df.groupby(["Dimension", "Rating"], as_index=False).size()
    return summary.rename(columns={"size": "Count"})


def extract_text_section(record: dict[str, object], keys: list[str]) -> object | None:
    data = record.get("data")
    if not isinstance(data, dict):
        return None
    for key in keys:
        value = data.get(key)
        if value:
            return value
    return None


def render_bullets(items: list[object]) -> None:
    cleaned = [str(item).strip() for item in items if item is not None]
    cleaned = [item for item in cleaned if item]
    if not cleaned:
        st.write("No details recorded.")
        return
    st.markdown("\n".join(f"- {item}" for item in cleaned))


def render_generic(value: object) -> None:
    if value is None:
        st.write("No details recorded.")
        return
    if isinstance(value, list):
        render_bullets(value)
        return
    if isinstance(value, dict):
        lines = []
        for key, item in value.items():
            if item is None:
                continue
            lines.append(f"{key}: {item}")
        if lines:
            render_bullets(lines)
        else:
            st.write("No details recorded.")
        return
    st.write(value)


def render_feedback(value: object) -> None:
    if isinstance(value, dict):
        rendered = False
        for key, item in value.items():
            if item in (None, [], {}):
                continue
            st.markdown(f"**{key.replace('_', ' ').title()}**")
            render_generic(item)
            rendered = True
        if rendered:
            return
    render_generic(value)


def render_follow_ups(value: object) -> None:
    if isinstance(value, list):
        rows: list[dict[str, object]] = []
        for item in value:
            if isinstance(item, dict):
                rows.append(
                    {
                        "ID": item.get("id", ""),
                        "Description": item.get("description", ""),
                        "Required": item.get("required", ""),
                    }
                )
            else:
                rows.append({"ID": "", "Description": str(item), "Required": ""})
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            return
    render_generic(value)


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
    st.subheader("Weekly cap (40 hours)")
    weekly_with_cap = add_weekly_cap(weekly_totals, WEEKLY_CAP_HOURS)
    st.dataframe(
        weekly_with_cap[["week", "hours", "Cap hours", "Remaining", "Status"]],
        use_container_width=True,
    )
    st.altair_chart(
        build_weekly_cap_chart(weekly_with_cap, WEEKLY_CAP_HOURS),
        use_container_width=True,
    )
    st.subheader("Monthly totals")
    st.dataframe(monthly_totals, use_container_width=True)
    st.bar_chart(monthly_totals.set_index("month"))

reviews_path = Path("reviews")
review_records, review_errors = load_review_records(reviews_path)

st.header("Workstream Progress")
workstreams, workstream_error = load_workstreams(Path("config/project.yml"))
if workstream_error:
    st.info(workstream_error)

workstream_table, deliverable_status = compute_workstream_progress(
    workstreams, review_records
)
st.dataframe(workstream_table, use_container_width=True)

for name, statuses in deliverable_status.items():
    st.subheader(name)
    if not statuses:
        st.write("No deliverable checklist configured.")
        continue
    status_df = pd.DataFrame(statuses, columns=["Deliverable", "Status"])
    st.dataframe(status_df, use_container_width=True, hide_index=True)
    completed = sum(1 for _, state in statuses if state == "Done")
    st.progress(completed / len(statuses))

st.header("Review Records")
for message in review_errors:
    st.info(message)

if review_records:
    for record in review_records:
        st.subheader(Path(record["path"]).name)
        feedback = extract_text_section(record, ["feedback", "summary", "notes"])
        follow_ups = extract_text_section(
            record, ["follow_up_issues", "follow_ups", "followups", "actions"]
        )
        if feedback:
            st.markdown("**Feedback**")
            render_feedback(feedback)
        if follow_ups:
            st.markdown("**Follow-ups**")
            render_follow_ups(follow_ups)
        with st.expander("Details (scores removed)"):
            st.json(record["data"])

st.header("Rubric Dimension Distribution")
rubric_paths, rubric_index_errors = load_rubric_index(Path("rubrics/rubric_index.yml"))
rubric_definitions, rubric_load_errors = load_rubric_definitions(rubric_paths)
for message in rubric_index_errors + rubric_load_errors:
    st.info(message)

if not review_records:
    st.info("No review records available to summarize rubric ratings.")
else:
    rating_summary = aggregate_dimension_ratings(review_records, rubric_definitions)
    if rating_summary.empty:
        st.info("No rubric dimension ratings found in review records.")
    else:
        chart = (
            alt.Chart(rating_summary)
            .mark_bar()
            .encode(
                x=alt.X("Dimension:N", sort="-y", title="Dimension"),
                y=alt.Y("Count:Q", title="Ratings count"),
                color=alt.Color("Rating:N", title="Rating"),
                tooltip=["Dimension", "Rating", "Count"],
            )
        )
        st.altair_chart(chart, use_container_width=True)
        st.dataframe(rating_summary, use_container_width=True)

# =============================================================================
# GitHub Integration Section
# =============================================================================

st.header("GitHub Activity")

try:
    from streamlit_app.github_client import fetch_all_github_data
    
    github_data = fetch_all_github_data()
    
    if github_data.error:
        st.warning(github_data.error)
    else:
        # Issues summary
        col1, col2, col3 = st.columns(3)
        
        open_issues = [i for i in github_data.issues if i.state == "open"]
        open_prs = [p for p in github_data.pull_requests if p.state == "open"]
        recent_runs = github_data.workflow_runs[:5]
        
        with col1:
            st.metric("Open Issues", len(open_issues))
        with col2:
            st.metric("Open PRs", len(open_prs))
        with col3:
            passing = sum(1 for r in recent_runs if r.conclusion == "success")
            st.metric("CI Pass Rate (last 5)", f"{passing}/5")
        
        # Issues table
        st.subheader("Recent Issues")
        if github_data.issues:
            issue_rows = []
            for issue in github_data.issues[:10]:
                issue_rows.append({
                    "#": issue.number,
                    "Title": issue.title,
                    "State": issue.state,
                    "Labels": ", ".join(issue.labels[:3]),
                    "Author": issue.author,
                    "Updated": issue.updated_at.strftime("%Y-%m-%d"),
                })
            st.dataframe(pd.DataFrame(issue_rows), use_container_width=True, hide_index=True)
        else:
            st.info("No issues found or GitHub API unavailable.")
        
        # PRs table
        st.subheader("Recent Pull Requests")
        if github_data.pull_requests:
            pr_rows = []
            for pr in github_data.pull_requests[:10]:
                pr_rows.append({
                    "#": pr.number,
                    "Title": pr.title,
                    "State": pr.state,
                    "Labels": ", ".join(pr.labels[:3]),
                    "Author": pr.author,
                    "Updated": pr.updated_at.strftime("%Y-%m-%d"),
                })
            st.dataframe(pd.DataFrame(pr_rows), use_container_width=True, hide_index=True)
        else:
            st.info("No pull requests found or GitHub API unavailable.")
        
        # CI Status
        st.subheader("Recent CI Runs")
        if github_data.workflow_runs:
            run_rows = []
            for run in github_data.workflow_runs[:10]:
                status_emoji = {
                    "success": "✅",
                    "failure": "❌",
                    "cancelled": "⏹️",
                    "skipped": "⏭️",
                    None: "🔄",
                }.get(run.conclusion, "❓")
                run_rows.append({
                    "Workflow": run.name,
                    "Status": f"{status_emoji} {run.conclusion or run.status}",
                    "Branch": run.head_branch,
                    "Date": run.created_at.strftime("%Y-%m-%d %H:%M"),
                })
            st.dataframe(pd.DataFrame(run_rows), use_container_width=True, hide_index=True)
        else:
            st.info("No workflow runs found or GitHub API unavailable.")

except ImportError:
    st.info("GitHub integration requires 'requests' package. Install with: pip install requests")
except Exception as e:
    st.warning(f"GitHub integration error: {e}")
