import pytest
from library_service import return_book_by_patron

def test_return_valid():
    suc, msg = return_book_by_patron("123456", 1)
    assert isinstance(suc, bool)
    assert isinstance(msg, str)

def test_book_not_borrowed():
    suc, msg = return_book_by_patron("123456", 999)
    assert suc is False
    assert "not borrowed" in msg.lower()

def test_invalid_patron_id():
    suc, msg = return_book_by_patron("xxxyyy", 1)
    assert suc is False

def test_calculate_late_fee_trigger():
    suc, msg = return_book_by_patron("123456", 2)
    assert isinstance(msg, str)

def test_multiple_returns():
    suc, msg = return_book_by_patron("123456", 3)
    assert isinstance(suc, bool)
