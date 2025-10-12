import pytest
from library_service import(
    search_books_in_catalog
)

#test cases for searching bks
def test_search_by_title_partial():
    bks = search_bks_in_catalog("harry", "title")
    assert isinstance(bks, list)
    for b in bks:
        assert "title" in b

def test_search_by_author_case_insensitive():
    bks = search_bks_in_catalog("rowling", "author")
    assert all("author" in b for b in bks)

def test_search_by_isbn_exact():
    bks = search_bks_in_catalog("1234567890123", "isbn")
    assert all(b["isbn"] == "1234567890123" for b in bks)

def test_empty_search_term():
    bks = search_bks_in_catalog("", "title")
    assert bks == []

def test_invalid_search_type():
    bks = search_bks_in_catalog("anything", "publisher")
    assert bks == []
