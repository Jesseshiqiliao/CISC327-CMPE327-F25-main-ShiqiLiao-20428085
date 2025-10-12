import pytest
from library_service import search_books_in_catalog

def test_search_by_title_partial():
    bks = search_books_in_catalog("harry", "title")
    assert isinstance(bks, list)

def test_search_by_author_case_insensitive():
    bks = search_books_in_catalog("rowling", "author")
    assert isinstance(bks, list)

def test_search_by_isbn_exact():
    bks = search_books_in_catalog("1234567890123", "isbn")
    assert isinstance(bks, list)

def test_empty_search_term():
    bks = search_books_in_catalog("", "title")
    assert bks == []

def test_invalid_search_type():
    bks = search_books_in_catalog("anything", "publisher")
    assert bks == []
