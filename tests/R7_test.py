import pytest
from library_service import get_patron_status_report

def test_status_contains_keys():
    rpt = get_patron_status_report("123456")
    assert "currently_borrowed" in rpt
    assert "late_fees" in rpt
    assert "borrow_count" in rpt
    assert "history" in rpt

def test_invalid_patron_id():
    rpt = get_patron_status_report("badid")
    assert rpt == {}

def test_borrowed_books_list():
    rpt = get_patron_status_report("123456")
    assert isinstance(rpt.get("currently_borrowed"), list)

def test_late_fees_is_number():
    rpt = get_patron_status_report("123456")
    assert isinstance(rpt.get("late_fees", 0), (int, float))

def test_history_format():
    rpt = get_patron_status_report("123456")
    assert isinstance(rpt.get("history"), list)
