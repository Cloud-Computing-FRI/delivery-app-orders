"""Unit tests for the CreateOrder use case.

The payoff of Clean Architecture: these run with no web server, no database and
no network. The gateways are replaced by tiny in-memory fakes and the order
repository is the real in-memory adapter. Run with `pytest` from the
delivery-app-orders folder.
"""
import pytest

from adapters.repositories import InMemoryOrderRepository
from domain.entities import RestaurantItem
from usecases.create_order import CreateOrder
from usecases.errors import NotificationUnavailable, RestaurantNotFound


class FakeRestaurantGateway:
    """Returns a fixed item, or raises a preset error."""

    def __init__(self, item=None, error=None):
        self._item = item
        self._error = error

    def find_item(self, restaurant_id, item_id):
        if self._error is not None:
            raise self._error
        return self._item


class FakeNotificationGateway:
    def __init__(self, fail=False):
        self._fail = fail
        self.sent = []

    def notify(self, order_id, message):
        if self._fail:
            raise NotificationUnavailable()
        self.sent.append((order_id, message))


def test_happy_path_creates_and_notifies():
    orders = InMemoryOrderRepository()
    restaurants = FakeRestaurantGateway(
        item=RestaurantItem("Pizza Corner", "Margherita", 8.5)
    )
    notifications = FakeNotificationGateway()
    create_order = CreateOrder(orders, restaurants, notifications)

    order = create_order(restaurant_id=1, item_id=1, customer="Ada")

    assert order.restaurant == "Pizza Corner"
    assert order.item == "Margherita"
    assert order.price == 8.5
    assert order.notified is True
    assert notifications.sent == [(order.id, "Ada, your Margherita from Pizza Corner is on its way.")]
    assert len(orders.list()) == 1


def test_unknown_restaurant_is_not_stored():
    orders = InMemoryOrderRepository()
    restaurants = FakeRestaurantGateway(error=RestaurantNotFound())
    create_order = CreateOrder(orders, restaurants, FakeNotificationGateway())

    with pytest.raises(RestaurantNotFound):
        create_order(restaurant_id=99, item_id=1, customer="Ada")

    assert orders.list() == []


def test_notifications_down_order_still_succeeds():
    orders = InMemoryOrderRepository()
    restaurants = FakeRestaurantGateway(
        item=RestaurantItem("Pizza Corner", "Margherita", 8.5)
    )
    notifications = FakeNotificationGateway(fail=True)
    create_order = CreateOrder(orders, restaurants, notifications)

    order = create_order(restaurant_id=1, item_id=1, customer="Ada")

    assert order.notified is False
    assert len(orders.list()) == 1
