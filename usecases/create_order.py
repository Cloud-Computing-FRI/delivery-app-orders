"""Use case: create an order.

This is the business logic that used to live inside the FastAPI route handler.
It depends only on ports (OrderRepository, RestaurantGateway,
NotificationGateway) and domain errors -- no FastAPI, no httpx, no database.
That is what makes it unit-testable with plain fakes (see tests/).
"""
from domain.entities import Order
from domain.ports import NotificationGateway, OrderRepository, RestaurantGateway

from .errors import NotificationUnavailable


class CreateOrder:
    def __init__(
        self,
        orders: OrderRepository,
        restaurants: RestaurantGateway,
        notifications: NotificationGateway,
    ):
        self._orders = orders
        self._restaurants = restaurants
        self._notifications = notifications

    def __call__(self, restaurant_id: int, item_id: int, customer: str) -> Order:
        # 1. Check the restaurant and item exist. The gateway raises a domain
        #    error (RestaurantNotFound / MenuItemNotFound / RestaurantUnavailable)
        #    which the web layer turns into the right HTTP status.
        found = self._restaurants.find_item(restaurant_id, item_id)

        # 2. Store the order, not yet notified.
        order = self._orders.add(
            customer=customer,
            restaurant=found.restaurant_name,
            item=found.item_name,
            price=found.item_price,
            notified=False,
        )

        # 3. Tell the customer. If notifications is down the order still stands:
        #    one failing service should not take down another.
        message = (
            f"{order.customer}, your {order.item} "
            f"from {order.restaurant} is on its way."
        )
        try:
            self._notifications.notify(order.id, message)
        except NotificationUnavailable:
            return order

        return self._orders.set_notified(order.id) or order
