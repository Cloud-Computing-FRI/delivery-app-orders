"""Use case: list all orders."""
from domain.entities import Order
from domain.ports import OrderRepository


class ListOrders:
    def __init__(self, repository: OrderRepository):
        self._repository = repository

    def __call__(self) -> list[Order]:
        return self._repository.list()
