import pytest
from library_service import (
    calculate_late_fee_for_book
)

#tests for function 4, calculating late fee
def test_no_overdue():
    str = calculate_late_fee_for_book("123456", 1)
    assert "fee_amount" in str
    assert str["fee_amount"] == 0

def test_overdue_within_7_days():
    str = calculate_late_fee_for_book("123456", 2)
    assert str["fee_amount"] <= 3.50

def test_overdue_more_than_7_days():
    str = calculate_late_fee_for_book("123456", 3)
    assert str["fee_amount"] >= 7.00

def test_fee_capped_at_15():
    str = calculate_late_fee_for_book("123456", 4)
    assert str["fee_amount"] <= 15.00

def test_invalid_patron_id():
    str = calculate_late_fee_for_book("badid", 5)
    assert "status" in str
