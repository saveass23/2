from pathlib import Path

from bot import DEFAULT_LOTS, build_lot_rows, export_to_csv, export_to_text


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
