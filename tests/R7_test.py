import pytest
from library_service import(
    get_patron_status_report
)

#test for getting patron status reports
def test_status_contains_keys():
    report = get_patron_status_report("123456")
    assert "currently_borrowed" in report
    assert "late_fees" in report
    assert "borrow_count" in report
    assert "history" in report

def test_invalid_patron_id():
    report = get_patron_status_report("badid")
    assert report == {}

def test_borrowed_books_list():
    report = get_patron_status_report("123456")
    assert isinstance(report.get("currently_borrowed"), list)

def test_late_fees_is_number():
    report = get_patron_status_report("123456")
    assert isinstance(report.get("late_fees", 0), (int, float))

def test_history_format():
    report = get_patron_status_report("123456")
    assert isinstance(report.get("history"), list)
