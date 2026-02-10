import json
from pathlib import Path

from bot import (
    DEFAULT_AUTOMATION_CONFIG,
    DEFAULT_LOTS,
    build_lot_rows,
    configure_golden_key,
    ensure_automation_config,
    export_to_csv,
    export_to_text,
    load_automation_config,
)


def test_build_rows_count_matches_default_lots() -> None:
    rows = build_lot_rows(DEFAULT_LOTS)
    assert len(rows) == len(DEFAULT_LOTS)


def test_exports_create_files(tmp_path: Path) -> None:
    rows = build_lot_rows(DEFAULT_LOTS)
    csv_file = tmp_path / "lots.csv"
    txt_file = tmp_path / "lots.txt"

    export_to_csv(rows, csv_file)
    export_to_text(rows, txt_file)

    assert csv_file.exists()
    assert txt_file.exists()
    assert "description_html" in csv_file.read_text(encoding="utf-8")
    assert "Лот #1" in txt_file.read_text(encoding="utf-8")


def test_ensure_automation_config_creates_default_file(tmp_path: Path) -> None:
    config_path = tmp_path / "automation.json"

    ensure_automation_config(config_path)

    raw = json.loads(config_path.read_text(encoding="utf-8"))
    assert raw == DEFAULT_AUTOMATION_CONFIG


def test_load_automation_config_reads_existing_file(tmp_path: Path) -> None:
    config_path = tmp_path / "automation.json"
    config_path.write_text(json.dumps({"golden_key": "secret"}), encoding="utf-8")

    loaded = load_automation_config(config_path)

    assert loaded["golden_key"] == "secret"


def test_configure_golden_key_updates_file(tmp_path: Path, monkeypatch) -> None:
    config_path = tmp_path / "automation.json"
    original = {"golden_key": "CHANGE_ME", "funpay_lots_url": "https://funpay.com/lots/"}
    config_path.write_text(json.dumps(original), encoding="utf-8")

    monkeypatch.setattr("bot.getpass", lambda _: "new-secret")

    updated = configure_golden_key(config_path, original)

    assert updated["golden_key"] == "new-secret"
    raw = json.loads(config_path.read_text(encoding="utf-8"))
    assert raw["golden_key"] == "new-secret"
