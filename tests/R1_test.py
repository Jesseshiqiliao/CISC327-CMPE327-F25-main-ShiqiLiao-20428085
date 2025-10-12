import pytest
from library_service import (
    add_book_to_catalog
)
#tests for function 1, adding books
def test_add_book_valid_input():
    suc, str = add_book_to_catalog("Test Book", "Test Author", "1234567890723", 5)
    
    assert suc == True
    assert "sucfully added" in str.lower()

def test_add_book_invalid_isbn():
    suc, str = add_book_to_catalog("Test Book", "Test Author", "123456789", 5)
    
    assert suc == False
    assert "13 digits" in str

def test_add_book_invalid_auth():
    name = ""
    for i in range(199): 
        name+='x'
    suc, str = add_book_to_catalog(name,name,"1111111111111", 5)

    assert suc == False
    assert "characters." in str.lower()

def test_add_book_invalid_bknm():
    name = ""
    for i in range(201): 
        name +='x'
    suc, str = add_book_to_catalog(name,"Tee Hee","1111111111111", 5)
    
    assert suc == False
    assert "characters." in str.lower()


# Add more test methods for each function and edge case. You can keep all your test in a separate folder named `tests`.