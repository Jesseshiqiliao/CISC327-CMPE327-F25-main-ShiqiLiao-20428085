import pytest
from library_service import (
    return_book_by_patron
)
#tests for function 3
def test_return_valid():
    suc, str = return_book_by_patron("123456", 1)
    assert isinstance(suc, bool)
    assert isinstance(str, str)

def test_book_not_borrowed():
    suc, str = return_book_by_patron("123456", 999)
    assert suc is False
    assert "not borrowed" in str.lower()

def test_invalid_patron_id():
    suc, str = return_book_by_patron("xxxyyy", 1)
    assert suc is False

def test_calculate_late_fee_trigger():
    suc, str = return_book_by_patron("123456", 2)
    assert isinstance(str, str)

def test_multiple_returns():
    suc, str = return_book_by_patron("123456", 3)
    assert isinstance(suc, bool)
