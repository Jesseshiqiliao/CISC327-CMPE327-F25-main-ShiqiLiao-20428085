import pytest
from library_service import (
    borrow_book_by_patron, add_book_to_catalog
)

#test for function 2
def test_borrow_book_valid():
    add_book_to_catalog("Test Book", "Test Author", "1234567890423", 5)
    suc, str = borrow_book_by_patron("123456", 1)
    assert suc == True
    assert "Successfully borrowed" in str

def test_borrow_book_invalid_pid():
    add_book_to_catalog("Test Book", "Test Author", "4434567890423", 5)
    suc, str = borrow_book_by_patron("999999999", 1)
    assert suc == False
    assert "Invalid patron ID" in str

def test_borrow_book_invalid_out_of_storage():
    add_book_to_catalog("Test Book", "Test Author", "7734567890423", 1)
    borrow_book_by_patron("123456", 1)
    suc, str = borrow_book_by_patron("123456", 1)
    assert suc == False
    assert "This book is currently" in str

def test_borrow_book_invalid_bookid():
    suc, str = borrow_book_by_patron("123456", 9999999)
    assert suc == False
    assert "Book not found." in str