from app.core.exporter import export_csv, export_txt
from app.models.nickname import NicknameCandidate


def test_exports(tmp_path) -> None:
    rows = [NicknameCandidate("검월", 0.9, 0.8, 0.85, True, "cain")]
    txt = tmp_path / "names.txt"
    csv = tmp_path / "names.csv"
    export_txt(txt, rows)
    export_csv(csv, rows)
    assert txt.read_text(encoding="utf-8") == "검월"
    assert "nickname,server,available" in csv.read_text(encoding="utf-8-sig")
