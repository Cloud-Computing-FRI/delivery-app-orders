"""Ports for the orders service.

The order use case talks to the other microservices only through these
abstract gateways. "Another microservice" is, from the core's point of view,
just an external detail -- the same category as the database. Whether a call
is HTTP, a message queue or an in-process fake is decided by the adapter wired
in at startup, not by the use case.
"""
from abc import ABC, abstractmethod

from .entities import Order, RestaurantItem


class OrderRepository(ABC):
    @abstractmethod
    def add(self, customer: str, restaurant: str, item: str, price: float, notified: bool) -> Order:
        ...

    @abstractmethod
    def set_notified(self, order_id: int) -> Order | None:
        ...

    @abstractmethod
    def list(self) -> list[Order]:
        ...


class RestaurantGateway(ABC):
    @abstractmethod
    def find_item(self, restaurant_id: int, item_id: int) -> RestaurantItem:
        """Return the restaurant/item facts, or raise a domain error."""
        ...


class NotificationGateway(ABC):
    @abstractmethod
    def notify(self, order_id: int, message: str) -> None:
        """Tell the customer, or raise NotificationUnavailable."""
        ...
