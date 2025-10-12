import pytest
from library_service import add_book_to_catalog



def test_add_book_valid_input():
    suc, msg = add_book_to_catalog("Test Book", "Test Author", "1234567890999", 5)
    assert suc is True
    assert "successfully added" in msg.lower()

def test_add_book_invalid_isbn():
    suc, msg = add_book_to_catalog("Test Book", "Test Author", "123456789", 5)
    assert suc is False
    assert "13 digits" in msg

def test_add_book_invalid_auth():
    name = "x" * 199
    suc, msg = add_book_to_catalog(name, name, "1111111111111", 5)
    assert suc is False
    assert "characters." in msg.lower()

def test_add_book_invalid_bknm():
    name = "x" * 201
    suc, msg = add_book_to_catalog(name, "Tee Hee", "1111111111111", 5)
    assert suc is False
    assert "characters." in msg.lower()
