"""FastAPI delivery mechanism for the orders service.

The only job here is HTTP: validate the request body, call the use case, and
map domain errors onto HTTP status codes. The business rules are elsewhere.
"""
from dataclasses import asdict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from usecases.create_order import CreateOrder
from usecases.errors import (
    MenuItemNotFound,
    RestaurantNotFound,
    RestaurantUnavailable,
)
from usecases.list_orders import ListOrders


class NewOrder(BaseModel):
    restaurant_id: int
    item_id: int
    customer: str


def create_router(create_order: CreateOrder, list_orders: ListOrders) -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    def health():
        return {"status": "ok"}

    @router.get("/orders")
    def list_all():
        return [asdict(o) for o in list_orders()]

    @router.post("/orders", status_code=201)
    def create(new: NewOrder):
        try:
            order = create_order(new.restaurant_id, new.item_id, new.customer)
        except RestaurantNotFound:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        except MenuItemNotFound:
            raise HTTPException(status_code=404, detail="Menu item not found")
        except RestaurantUnavailable:
            raise HTTPException(
                status_code=503, detail="Restaurants service is unavailable"
            )
        return asdict(order)

    return router
