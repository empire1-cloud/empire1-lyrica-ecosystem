"""Unit tests for omni_agent.scanner."""
from __future__ import annotations

from omni_agent.scanner import scan_text


def test_detects_checkbox_task():
    md = "- [ ] write the docs"
    out = scan_text(md, source_file="x.md")
    assert len(out) == 1
    assert out[0].pattern == "checkbox"
    assert "write the docs" in out[0].text
    assert out[0].id.startswith("TASK-")


def test_skips_completed_checkbox():
    md = "- [x] already done"
    assert scan_text(md, source_file="x.md") == []


def test_detects_todo_and_fixme():
    md = "Some prose. TODO: implement endpoint /api/x\nAnother line\nFIXME: handle null user"
    out = scan_text(md, source_file="y.md")
    patterns = sorted(t.pattern for t in out)
    assert patterns == ["fixme", "todo"]


def test_explicit_id_is_preserved():
    md = "- [ ] TASK-042 hello world"
    out = scan_text(md, source_file="z.md")
    assert out[0].id == "TASK-042"


def test_id_is_stable_for_same_input():
    md = "- [ ] stable id check"
    a = scan_text(md, source_file="z.md")
    b = scan_text(md, source_file="z.md")
    assert a[0].id == b[0].id


def test_multiple_lines_distinct_ids():
    md = "- [ ] one\n- [ ] two"
    out = scan_text(md, source_file="z.md")
    assert len(out) == 2
    assert out[0].id != out[1].id


def test_tags_are_extracted():
    md = "- [ ] add #backend feature for #urgent"
    out = scan_text(md, source_file="z.md")
    assert "backend" in out[0].tags
    assert "urgent" in out[0].tags
