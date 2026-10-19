"""HTTP gateways: the outbound adapters that talk to the other microservices.

All the HTTP detail -- the URL shapes, status-code meanings, httpx, timeouts --
lives here. The adapters translate transport failures into domain errors so the
use case never sees an HTTP concept. Swapping to a message queue later would
mean a new adapter here and nothing else.
"""
import httpx

from domain.entities import RestaurantItem
from domain.ports import NotificationGateway, RestaurantGateway
from usecases.errors import (
    MenuItemNotFound,
    NotificationUnavailable,
    RestaurantNotFound,
    RestaurantUnavailable,
)


class HttpRestaurantGateway(RestaurantGateway):
    def __init__(self, base_url: str, timeout: float = 3):
        self._base_url = base_url
        self._timeout = timeout

    def find_item(self, restaurant_id: int, item_id: int) -> RestaurantItem:
        try:
            response = httpx.get(
                f"{self._base_url}/restaurants/{restaurant_id}", timeout=self._timeout
            )
        except httpx.HTTPError:
            raise RestaurantUnavailable()
        if response.status_code == 404:
            raise RestaurantNotFound()
        if response.status_code != 200:
            raise RestaurantUnavailable()

        restaurant = response.json()
        item = next((i for i in restaurant["menu"] if i["id"] == item_id), None)
        if item is None:
            raise MenuItemNotFound()
        return RestaurantItem(
            restaurant_name=restaurant["name"],
            item_name=item["name"],
            item_price=item["price"],
        )


class HttpNotificationGateway(NotificationGateway):
    def __init__(self, base_url: str, timeout: float = 3):
        self._base_url = base_url
        self._timeout = timeout

    def notify(self, order_id: int, message: str) -> None:
        try:
            httpx.post(
                f"{self._base_url}/notifications",
                json={"order_id": order_id, "message": message},
                timeout=self._timeout,
            ).raise_for_status()
        except httpx.HTTPError:
            raise NotificationUnavailable()
