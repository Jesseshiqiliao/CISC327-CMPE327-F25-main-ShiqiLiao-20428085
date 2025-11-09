import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta
from services.library_service import (
    calculate_late_fee_for_book, pay_late_fees, refund_late_fee_payment
)
from services.payment_service import PaymentGateway

@pytest.fixture
def stubs_payment(mocker):
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount": 10.0, "days_overdue": 5, "status": "OK"})
    mocker.patch("services.library_service.get_book_by_id", return_value={"title": "B"})

@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda x: None)

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
