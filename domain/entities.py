"""Domain entities for the orders service. No framework or I/O imports.

`RestaurantItem` is what the restaurants gateway promises to return: the facts
the order use case needs, with no trace of HTTP or JSON.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class RestaurantItem:
    restaurant_name: str
    item_name: str
    item_price: float


@dataclass(frozen=True)
class Order:
    id: int
    customer: str
    restaurant: str
    item: str
    price: float
    notified: bool
