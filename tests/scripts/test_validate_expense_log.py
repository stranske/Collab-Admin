"""Tests for validate_expense_log script."""

from __future__ import annotations

import csv
import importlib.util
from datetime import date, timedelta
from pathlib import Path


def load_module():
    script_path = (
        Path(__file__).resolve().parents[2] / "scripts" / "validate_expense_log.py"
    )
    spec = importlib.util.spec_from_file_location("validate_expense_log", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


validate_expense_log = load_module()


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=validate_expense_log.REQUIRED)
        writer.writeheader()
        writer.writerows(rows)


def base_row() -> dict[str, str]:
    return {
        "date": (date.today() - timedelta(days=7)).isoformat(),
        "amount": "49.99",
        "currency": "USD",
        "category": "hardware",
        "description": "USB hub",
        "receipt_link": "https://example.com/receipt",
        "issue_or_pr": "PR-123",
        "preapproval_link": "https://example.com/preapproval",
    }


def test_valid_log_passes(tmp_path: Path) -> None:
    path = tmp_path / "expenses.csv"
    write_csv(path, [base_row()])

    errors = validate_expense_log.validate_expense_log(str(path))

    assert errors == []


def test_missing_columns_fails(tmp_path: Path) -> None:
    path = tmp_path / "expenses.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "amount", "category"])
        writer.writerow(["2024-01-08", "12.00", "supplies"])

    errors = validate_expense_log.validate_expense_log(str(path))

    assert any("Missing columns" in err for err in errors)


def test_invalid_date_format_fails(tmp_path: Path) -> None:
    path = tmp_path / "expenses.csv"
    row = base_row()
    row["date"] = "2024/01/08"
    write_csv(path, [row])

    errors = validate_expense_log.validate_expense_log(str(path))

    assert any("Invalid date" in err for err in errors)


def test_invalid_amount_fails(tmp_path: Path) -> None:
    path = tmp_path / "expenses.csv"
    row = base_row()
    row["amount"] = "12,00"
    write_csv(path, [row])

    errors = validate_expense_log.validate_expense_log(str(path))

    assert any("Invalid amount" in err for err in errors)


def test_invalid_currency_fails(tmp_path: Path) -> None:
    path = tmp_path / "expenses.csv"
    row = base_row()
    row["currency"] = "usd"
    write_csv(path, [row])

    errors = validate_expense_log.validate_expense_log(str(path))

    assert any("Invalid currency" in err for err in errors)


def test_missing_required_value_fails(tmp_path: Path) -> None:
    path = tmp_path / "expenses.csv"
    row = base_row()
    row["description"] = ""
    write_csv(path, [row])

    errors = validate_expense_log.validate_expense_log(str(path))

    assert any("Missing value for 'description'" in err for err in errors)
