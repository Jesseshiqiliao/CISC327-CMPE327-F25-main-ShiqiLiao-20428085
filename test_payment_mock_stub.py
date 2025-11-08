import pytest
from unittest.mock import Mock
from services.library import pay_late_fees, refund_late_fee_payment
from services.library import calculate_late_fee_for_book, get_book_by_id


@pytest.fixture
def stubs(mocker):
    mocker.patch("services.library.calculate_late_fee_for_book")
    mocker.patch("services.library.get_book_by_id")


def test_pay_ok(mocker, stubs):
    calculate_late_fee_for_book.return_value = {"fee_amount": 10.0}
    get_book_by_id.return_value = {"title": "A"}
    gw = Mock()
    gw.process_payment.return_value = (True, "t1", "OK")
    s, m, t = pay_late_fees("123456", 1, gw)
    assert s is True
    assert t == "t1"
    gw.process_payment.assert_called_once_with(
        patron_id="123456", amount=10.0, description="Late fees for 'A'"
    )


def test_pay_decline(mocker, stubs):
    calculate_late_fee_for_book.return_value = {"fee_amount": 5.0}
    get_book_by_id.return_value = {"title": "B"}
    gw = Mock()
    gw.process_payment.return_value = (False, None, "X")
    s, m, t = pay_late_fees("123456", 2, gw)
    assert s is False
    assert t is None


def test_pay_bad_patron(mocker, stubs):
    gw = Mock()
    s, m, t = pay_late_fees("AA", 1, gw)
    assert s is False
    gw.process_payment.assert_not_called()


def test_pay_zero_fee(mocker, stubs):
    calculate_late_fee_for_book.return_value = {"fee_amount": 0.0}
    get_book_by_id.return_value = {"title": "C"}
    gw = Mock()
    s, m, t = pay_late_fees("123456", 1, gw)
    assert s is False
    gw.process_payment.assert_not_called()


def test_pay_exc(mocker, stubs):
    calculate_late_fee_for_book.return_value = {"fee_amount": 7.0}
    get_book_by_id.return_value = {"title": "D"}
    gw = Mock()
    gw.process_payment.side_effect = Exception("E")
    s, m, t = pay_late_fees("123456", 1, gw)
    assert s is False
    assert t is None


def test_refund_ok():
    gw = Mock()
    gw.refund_payment.return_value = (True, "R")
    s, m = refund_late_fee_payment("txn_1", 10.0, gw)
    assert s is True
    gw.refund_payment.assert_called_once_with("txn_1", 10.0)


def test_refund_bad_txn():
    gw = Mock()
    s, m = refund_late_fee_payment("x", 10.0, gw)
    assert s is False
    gw.refund_payment.assert_not_called()


def test_refund_neg():
    gw = Mock()
    s, m = refund_late_fee_payment("txn_2", -1, gw)
    assert s is False
    gw.refund_payment.assert_not_called()


def test_refund_zero():
    gw = Mock()
    s, m = refund_late_fee_payment("txn_2", 0, gw)
    assert s is False
    gw.refund_payment.assert_not_called()


def test_refund_too_high():
    gw = Mock()
    s, m = refund_late_fee_payment("txn_2", 20, gw)
    assert s is False
    gw.refund_payment.assert_not_called()
