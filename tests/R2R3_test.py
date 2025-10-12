import pytest
from library_service import add_book_to_catalog, borrow_book_by_patron

def test_borrow_book_valid():
    add_book_to_catalog("Test Book", "Test Author", "1234567890423", 5)
    suc, msg = borrow_book_by_patron("123456", 1)
    assert suc is True
    assert "successfully borrowed" in msg.lower()

def test_borrow_book_invalid_pid():
    add_book_to_catalog("Test Book", "Test Author", "4434567890423", 5)
    suc, msg = borrow_book_by_patron("999999999", 1)
    assert suc is False
    assert "invalid patron id" in msg.lower()

def test_borrow_book_invalid_out_of_storage():
    add_book_to_catalog("Test Book", "Test Author", "7734567890423", 1)
    borrow_book_by_patron("123456", 1)
    suc, msg = borrow_book_by_patron("123456", 1)
    assert suc is False
    assert "currently" in msg.lower()

def test_borrow_book_invalid_bookid():
    suc, msg = borrow_book_by_patron("123456", 9999999)
    assert suc is False
    assert "not found" in msg.lower()
