"""Run with:  python -m pytest -v   (inside this folder)"""
import pytest

from shop import Cart, apply_discount


def test_ten_percent():
    assert apply_discount(200, 10) == 180


def test_zero_percent_changes_nothing():
    assert apply_discount(99.5, 0) == 99.5


@pytest.mark.parametrize("price, pct, expected", [(100, 10, 90), (50, 50, 25), (80, 0, 80), (80, 100, 0)])
def test_discount_table(price, pct, expected):
    assert apply_discount(price, pct) == expected


def test_negative_price_rejected():
    with pytest.raises(ValueError):
        apply_discount(-5, 10)


@pytest.fixture
def cart():
    c = Cart()
    c.add("pen", 10, 3)
    c.add("book", 120.5)
    return c


def test_cart_total(cart):
    assert cart.total() == 150.5


def test_coupon_applies(cart):
    assert cart.total_with_coupon("SAVE10") == pytest.approx(135.45)


def test_unknown_coupon_ignored(cart):
    assert cart.total_with_coupon("NOPE") == 150.5


def test_zero_quantity_rejected():
    with pytest.raises(ValueError):
        Cart().add("pen", 10, 0)

# TODO (your turn): add a test for an empty cart, and one for a 100% price edge case.
