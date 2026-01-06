"""Review Console for writing review YAML records."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import streamlit as st

# Default workstreams if config not loaded
DEFAULT_WORKSTREAMS = [
    "Trend_Model_Project",
    "Agent Integration",
    "Consumer Usability",
    "Marketplace Plan",
]


def load_rubric_options(rubrics_path: Path) -> list[str]:
    """Load available rubric IDs from rubrics directory."""
    if not rubrics_path.exists():
        return []

    rubric_ids = []
    for yml_file in rubrics_path.glob("*.yml"):
        if yml_file.name == "rubric_index.yml":
            continue
        # Use filename without extension as rubric ID
        rubric_ids.append(yml_file.stem)
    return sorted(rubric_ids)


def load_rubric_dimensions(rubric_path: Path) -> list[dict[str, Any]]:
    """Load dimensions from a rubric file."""
    if not rubric_path.exists():
        return []

    try:
        import yaml

        data = yaml.safe_load(rubric_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return []
        dimensions = data.get("dimensions", [])
        if not isinstance(dimensions, list):
            return []
        return dimensions
    except Exception:
        return []


def load_rubric_levels(rubric_path: Path) -> list[str]:
    """Load rating levels from a rubric file."""
    if not rubric_path.exists():
        return ["Poor", "Mediocre", "High", "Excellent"]

    try:
        import yaml

        data = yaml.safe_load(rubric_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return ["Poor", "Mediocre", "High", "Excellent"]
        levels = data.get("levels", [])
        if isinstance(levels, list) and levels:
            return [str(level) for level in levels]
        return ["Poor", "Mediocre", "High", "Excellent"]
    except Exception:
        return ["Poor", "Mediocre", "High", "Excellent"]


def generate_review_yaml(
    pr_number: int,
    reviewer: str,
    review_date: date,
    workstream: str,
    rubric_used: str,
    dimension_ratings: list[dict[str, str]],
    strengths: list[str],
    risks: list[str],
    notes: list[str],
    follow_ups: list[dict[str, Any]],
) -> str:
    """Generate YAML content for a review record."""
    try:
        import yaml
    except ImportError:
        return "# Error: PyYAML not installed"

    record = {
        "pr_number": pr_number,
        "reviewer": reviewer,
        "date": review_date.isoformat(),
        "workstream": workstream,
        "rubric_used": rubric_used,
        "dimension_ratings": dimension_ratings,
        "feedback": {
            "strengths": strengths if strengths else [],
            "risks": risks if risks else [],
            "notes": notes if notes else [],
        },
        "follow_up_issues": follow_ups if follow_ups else [],
    }

    return yaml.dump(record, default_flow_style=False, sort_keys=False, allow_unicode=True)


def render_review_console(
    workstreams: list[str] | None = None,
    rubrics_path: Path | None = None,
    reviews_path: Path | None = None,
) -> None:
    """Render the review console UI."""
    if workstreams is None:
        workstreams = DEFAULT_WORKSTREAMS
    if rubrics_path is None:
        rubrics_path = Path("rubrics")
    if reviews_path is None:
        reviews_path = Path("reviews")

    st.subheader("📝 Create Review Record")

    # Basic info
    col1, col2 = st.columns(2)
    with col1:
        pr_number = st.number_input("PR Number", min_value=1, value=1, step=1)
        reviewer = st.text_input("Reviewer", value="stranske")
    with col2:
        review_date = st.date_input("Review Date", value=date.today())
        workstream = st.selectbox("Workstream", options=workstreams)

    # Rubric selection
    rubric_options = load_rubric_options(rubrics_path)
    if rubric_options:
        rubric_used = st.selectbox("Rubric", options=rubric_options)
    else:
        rubric_used = st.text_input("Rubric ID", value="writing_quality")

    # Load dimensions for selected rubric
    rubric_file = rubrics_path / f"{rubric_used}.yml"
    dimensions = load_rubric_dimensions(rubric_file)
    levels = load_rubric_levels(rubric_file)

    # Dimension ratings
    st.markdown("### Dimension Ratings")
    dimension_ratings = []

    if dimensions:
        for dim in dimensions:
            dim_id = dim.get("id", "unknown")
            dim_name = dim.get("name", dim_id)
            descriptors = dim.get("descriptors", {})

            col1, col2 = st.columns([1, 2])
            with col1:
                rating = st.selectbox(
                    dim_name,
                    options=levels,
                    key=f"dim_{dim_id}",
                )
            with col2:
                # Show descriptor for selected rating
                if isinstance(descriptors, dict) and rating in descriptors:
                    st.caption(descriptors[rating])

            dimension_ratings.append(
                {
                    "dimension": dim_id,
                    "rating": rating,
                }
            )
    else:
        st.info("No dimensions found for selected rubric. Add manually in YAML.")

    # Feedback sections
    st.markdown("### Feedback")

    strengths_text = st.text_area(
        "Strengths (one per line)",
        height=100,
        help="List the strengths of this submission",
    )
    strengths = [s.strip() for s in strengths_text.split("\n") if s.strip()]

    risks_text = st.text_area(
        "Risks / Concerns (one per line)",
        height=100,
        help="List any risks or concerns",
    )
    risks = [r.strip() for r in risks_text.split("\n") if r.strip()]

    notes_text = st.text_area(
        "Additional Notes (one per line)",
        height=100,
        help="Any other notes or observations",
    )
    notes = [n.strip() for n in notes_text.split("\n") if n.strip()]

    # Follow-up issues
    st.markdown("### Follow-up Issues")
    num_followups = st.number_input("Number of follow-ups", min_value=0, max_value=5, value=0)

    follow_ups = []
    for i in range(int(num_followups)):
        st.markdown(f"**Follow-up {i + 1}**")
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            fu_id = st.text_input("ID", key=f"fu_id_{i}", value=f"FU-{i+1}")
        with col2:
            fu_desc = st.text_input("Description", key=f"fu_desc_{i}")
        with col3:
            fu_required = st.checkbox("Required", key=f"fu_req_{i}")

        if fu_desc:
            follow_ups.append(
                {
                    "id": fu_id,
                    "description": fu_desc,
                    "required": fu_required,
                }
            )

    # Generate YAML
    st.markdown("---")
    st.markdown("### Generated YAML")

    yaml_content = generate_review_yaml(
        pr_number=int(pr_number),
        reviewer=reviewer,
        review_date=review_date,
        workstream=workstream,
        rubric_used=rubric_used,
        dimension_ratings=dimension_ratings,
        strengths=strengths,
        risks=risks,
        notes=notes,
        follow_ups=follow_ups,
    )

    st.code(yaml_content, language="yaml")

    # Save button
    col1, col2 = st.columns(2)
    with col1:
        filename = f"review_pr{pr_number}_{review_date.isoformat()}.yml"
        st.download_button(
            label="📥 Download YAML",
            data=yaml_content,
            file_name=filename,
            mime="text/yaml",
        )
    with col2:
        if st.button("💾 Save to reviews/"):
            save_path = reviews_path / filename
            try:
                save_path.write_text(yaml_content, encoding="utf-8")
                st.success(f"Saved to {save_path}")
            except Exception as e:
                st.error(f"Failed to save: {e}")
