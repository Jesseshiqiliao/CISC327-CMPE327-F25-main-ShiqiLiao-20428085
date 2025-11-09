import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta
from services.library_service import (
    add_book_to_catalog, borrow_book_by_patron, return_book_by_patron,
    calculate_late_fee_for_book, search_books_in_catalog,
    get_patron_status_report, pay_late_fees, refund_late_fee_payment
)
from services.payment_service import PaymentGateway

#R Fixtures
@pytest.fixture
def stub_books(mocker):
    mocker.patch("services.library_service.get_book_by_id", return_value={"book_id":1, "title":"B", "available_copies":1})
    mocker.patch("services.library_service.get_book_by_isbn", return_value=None)
    mocker.patch("services.library_service.insert_book", return_value=True)
    mocker.patch("services.library_service.insert_borrow_record", return_value=True)
    mocker.patch("services.library_service.update_book_availability", return_value=True)
    mocker.patch("services.library_service.get_patron_borrow_count", return_value=0)
    mocker.patch("services.library_service.get_patron_borrowed_books", return_value=[{"book_id":1, "due_date": datetime.now() - timedelta(days=3), "title":"B"}])

@pytest.fixture
def stubs_payment(mocker):
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount": 10.0, "days_overdue": 5, "status": "OK"})
    mocker.patch("services.library_service.get_book_by_id", return_value={"title": "B"})

@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda x: None)

#R1+R2
def test_add_valid(stub_books):
    s,m=add_book_to_catalog("B","A","1234567890123",3)
    assert s

def test_add_bad_title(stub_books):
    s,m=add_book_to_catalog("","A","1234567890123",3)
    assert not s

def test_add_bad_author(stub_books):
    s,m=add_book_to_catalog("B","", "1234567890123",3)
    assert not s

def test_add_bad_isbn(stub_books):
    s,m=add_book_to_catalog("B","A","12345",3)
    assert not s

def test_add_bad_copies(stub_books):
    s,m=add_book_to_catalog("B","A","1234567890123",0)
    assert not s

def test_add_db_fail(stub_books, mocker):
    m=mocker.patch("services.library_service.insert_book", return_value=False)
    s,_=add_book_to_catalog("B","A","1234567890123",1)
    assert not s
    m.assert_called_once()

#R3
def test_borrow_ok(stub_books):
    s,_=borrow_book_by_patron("123456",1)
    assert s

def test_borrow_bad_patron(stub_books):
    s,_=borrow_book_by_patron("ABC",1)
    assert not s

def test_borrow_not_found(mocker):
    m=mocker.patch("services.library_service.get_book_by_id", return_value=None)
    s,_=borrow_book_by_patron("123456",1)
    assert not s
    m.assert_called_once_with(1)

def test_borrow_no_copies(mocker):
    m=mocker.patch("services.library_service.get_book_by_id", return_value={"available_copies":0})
    s,_=borrow_book_by_patron("123456",1)
    assert not s
    m.assert_called_once_with(1)

def test_borrow_limit(mocker):
    mocker.patch("services.library_service.get_book_by_id", return_value={"available_copies":1})
    m2=mocker.patch("services.library_service.get_patron_borrow_count", return_value=6)
    s,_=borrow_book_by_patron("123456",1)
    assert not s
    m2.assert_called_once_with("123456")

#R4
def test_return_ok(stub_books, mocker):
    m=mocker.patch("services.library_service.update_borrow_record_return_date", return_value=True)
    s,_=return_book_by_patron("123456",1)
    assert s
    m.assert_called_once()

def test_return_bad_patron(stub_books):
    s,_=return_book_by_patron("ABC",1)
    assert not s

def test_return_not_borrowed(stub_books, mocker):
    m=mocker.patch("services.library_service.get_patron_borrowed_books", return_value=[])
    s,_=return_book_by_patron("123456",1)
    assert not s
    m.assert_called_once_with("123456")

def test_return_db_fail(stub_books, mocker):
    m=mocker.patch("services.library_service.update_borrow_record_return_date", return_value=False)
    s,_=return_book_by_patron("123456",1)
    assert not s
    m.assert_called_once()

#R5
def test_fee_none(stub_books, mocker):
    m=mocker.patch("services.library_service.get_patron_borrowed_books", return_value=[])
    f=calculate_late_fee_for_book("123456",1)
    assert f['fee_amount']==0.0
    m.assert_called_once_with("123456")

def test_fee_overdue(mocker):
    due=datetime.now()-timedelta(days=10)
    m=mocker.patch("services.library_service.get_patron_borrowed_books", return_value=[{"book_id":1,"due_date":due}])
    f=calculate_late_fee_for_book("123456",1)
    assert f['fee_amount']>0
    m.assert_called_once_with("123456")

#R6
def test_search_found(mocker):
    m=mocker.patch("services.library_service.get_all_books", return_value=[{"title":"Python","author":"A","isbn":"123"}])
    r=search_books_in_catalog("Python","title")
    assert len(r)==1
    m.assert_called_once()

#R7
def test_status_none(mocker):
    m=mocker.patch("services.library_service.get_patron_borrowed_books", return_value=[])
    r=get_patron_status_report("123456")
    assert r["borrow_count"]==0
    m.assert_called_once_with("123456")

def test_status_overdue(mocker):
    due=datetime.now()-timedelta(days=5)
    m=mocker.patch("services.library_service.get_patron_borrowed_books", return_value=[{"book_id":1,"due_date":due,"title":"B"}])
    r=get_patron_status_report("123456")
    assert r["late_fees"]>0
    m.assert_called_once_with("123456")

#Payment & Late Fee
def test_pay_ok(stubs_payment):
    gw=Mock()
    gw.process_payment.return_value=(True,"t1","OK")
    s,_,t=pay_late_fees("123456",1,gw)
    assert s and t=="t1"
    gw.process_payment.assert_called_once_with(patron_id="123456", amount=10.0, description="Late fees for 'B'")

def test_pay_decline(stubs_payment):
    gw=Mock()
    gw.process_payment.return_value=(False,None,"D")
    s,_,t=pay_late_fees("123456",1,gw)
    assert not s
    gw.process_payment.assert_called_once()

def test_pay_bad_patron(stubs_payment):
    gw=Mock()
    s,_,t=pay_late_fees("ABC",1,gw)
    assert not s
    gw.process_payment.assert_not_called()

def test_pay_zero_fee(mocker):
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount":0.0,"days_overdue":0,"status":"OK"})
    mocker.patch("services.library_service.get_book_by_id", return_value={"title":"B"})
    gw=Mock()
    s,_,t=pay_late_fees("123456",1,gw)
    assert not s
    gw.process_payment.assert_not_called()

def test_pay_exc(stubs_payment):
    gw=Mock()
    gw.process_payment.side_effect=Exception("E")
    s,_,t=pay_late_fees("123456",1,gw)
    assert not s
    gw.process_payment.assert_called_once()

#Refund
def test_refund_ok():
    gw=Mock()
    gw.refund_payment.return_value=(True,"OK")
    s,_=refund_late_fee_payment("txn_1",10,gw)
    assert s
    gw.refund_payment.assert_called_once_with("txn_1",10)

def test_refund_bad_txn():
    gw=Mock()
    s,_=refund_late_fee_payment("x",10,gw)
    assert not s
    gw.refund_payment.assert_not_called()

def test_refund_neg():
    gw=Mock()
    s,_=refund_late_fee_payment("txn_2",-1,gw)
    assert not s
    gw.refund_payment.assert_not_called()

def test_refund_zero():
    gw=Mock()
    s,_=refund_late_fee_payment("txn_2",0,gw)
    assert not s
    gw.refund_payment.assert_not_called()

def test_refund_high():
    gw=Mock()
    s,_=refund_late_fee_payment("txn_2",20,gw)
    assert not s
    gw.refund_payment.assert_not_called()

#PaymentGateway direct
def test_pg_proc_ok():
    gw=PaymentGateway()
    s,t,_=gw.process_payment("123456",100,"x")
    assert s and t.startswith("txn_")

def test_pg_proc_bad_amount():
    gw=PaymentGateway()
    s,t,_=gw.process_payment("123456",0,"x")
    assert not s

def test_pg_proc_bad_patron():
    gw=PaymentGateway()
    s,t,_=gw.process_payment("ABC",50,"x")
    assert not s

def test_pg_refund_ok():
    gw=PaymentGateway()
    s,_=gw.refund_payment("txn_123_1",50)
    assert s

def test_pg_refund_bad_id():
    gw=PaymentGateway()
    s,_=gw.refund_payment("x",50)
    assert not s

def test_pg_refund_bad_amount():
    gw=PaymentGateway()
    s,_=gw.refund_payment("txn_123_1",0)
    assert not s

def test_pg_verify_ok():
    gw=PaymentGateway()
    r=gw.verify_payment_status("txn_123_1")
    assert r["status"]=="completed"

def test_pg_verify_nf():
    gw=PaymentGateway()
    r=gw.verify_payment_status("x")
    assert r["status"]=="not_found"
