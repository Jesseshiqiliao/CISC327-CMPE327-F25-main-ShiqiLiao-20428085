import pytest
from library_service import calculate_late_fee_for_book

def test_no_overdue():
    fee = calculate_late_fee_for_book("123456", 1)
    assert "fee_amount" in fee
    assert fee["fee_amount"] == 0

def test_overdue_within_7_days():
    fee = calculate_late_fee_for_book("123456", 2)
    assert fee["fee_amount"] <= 3.50

def test_overdue_more_than_7_days():
    fee = calculate_late_fee_for_book("123456", 3)
    assert fee["fee_amount"] >= 7.00

def test_fee_capped_at_15():
    fee = calculate_late_fee_for_book("123456", 4)
    assert fee["fee_amount"] <= 15.00

def test_invalid_patron_id():
    fee = calculate_late_fee_for_book("badid", 5)
    assert "status" in fee
