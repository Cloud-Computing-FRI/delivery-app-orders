"""Composition root for the orders service.

Wires the whole onion together: reads configuration, builds the outbound HTTP
gateways and the order repository (PostgreSQL when DATABASE_URL is set,
otherwise in-memory), injects them into the use cases, mounts the web router,
and exposes `app` for `uvicorn main:app`.

The service addresses still come from environment variables, exactly as
before, so the same image runs on a laptop and in Kubernetes.
"""
import os

from fastapi import FastAPI

from adapters.gateways import HttpNotificationGateway, HttpRestaurantGateway
from adapters.repositories import InMemoryOrderRepository, PostgresOrderRepository
from domain.ports import OrderRepository
from usecases.create_order import CreateOrder
from usecases.list_orders import ListOrders
from web.api import create_router

RESTAURANTS_URL = os.getenv("RESTAURANTS_URL", "http://localhost:8001")
NOTIFICATIONS_URL = os.getenv("NOTIFICATIONS_URL", "http://localhost:8003")


def build_repository() -> OrderRepository:
    dsn = os.getenv("DATABASE_URL")
    if dsn:
        return PostgresOrderRepository(dsn)
    return InMemoryOrderRepository()


def create_app() -> FastAPI:
    orders = build_repository()
    restaurants = HttpRestaurantGateway(RESTAURANTS_URL)
    notifications = HttpNotificationGateway(NOTIFICATIONS_URL)

    create_order = CreateOrder(orders, restaurants, notifications)
    list_orders = ListOrders(orders)

    app = FastAPI(title="Orders service")
    app.include_router(create_router(create_order, list_orders))
    return app


app = create_app()
