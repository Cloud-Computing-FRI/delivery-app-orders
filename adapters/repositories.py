"""In-memory and PostgreSQL adapters for the OrderRepository port.

`psycopg` is imported lazily, only when the PostgreSQL adapter is actually
constructed, so the in-memory path (and the unit tests) need no database driver.
"""
from dataclasses import replace

from domain.entities import Order
from domain.ports import OrderRepository


class InMemoryOrderRepository(OrderRepository):
    def __init__(self):
        self._orders: list[Order] = []

    def add(self, customer: str, restaurant: str, item: str, price: float, notified: bool) -> Order:
        order = Order(
            id=len(self._orders) + 1,
            customer=customer,
            restaurant=restaurant,
            item=item,
            price=price,
            notified=notified,
        )
        self._orders.append(order)
        return order

    def set_notified(self, order_id: int) -> Order | None:
        for i, order in enumerate(self._orders):
            if order.id == order_id:
                updated = replace(order, notified=True)
                self._orders[i] = updated
                return updated
        return None

    def list(self) -> list[Order]:
        return list(self._orders)


class PostgresOrderRepository(OrderRepository):
    def __init__(self, dsn: str):
        import psycopg

        self._psycopg = psycopg
        self._dsn = dsn

    def add(self, customer: str, restaurant: str, item: str, price: float, notified: bool) -> Order:
        with self._psycopg.connect(self._dsn) as conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO orders (customer, restaurant, item, price, notified) "
                "VALUES (%s, %s, %s, %s, %s) RETURNING id",
                (customer, restaurant, item, price, notified),
            )
            new_id = cur.fetchone()[0]
        return Order(new_id, customer, restaurant, item, price, notified)

    def set_notified(self, order_id: int) -> Order | None:
        with self._psycopg.connect(self._dsn) as conn, conn.cursor() as cur:
            cur.execute(
                "UPDATE orders SET notified = TRUE WHERE id = %s "
                "RETURNING id, customer, restaurant, item, price, notified",
                (order_id,),
            )
            row = cur.fetchone()
        if row is None:
            return None
        return Order(row[0], row[1], row[2], row[3], float(row[4]), row[5])

    def list(self) -> list[Order]:
        with self._psycopg.connect(self._dsn) as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT id, customer, restaurant, item, price, notified "
                "FROM orders ORDER BY id"
            )
            return [
                Order(r[0], r[1], r[2], r[3], float(r[4]), r[5])
                for r in cur.fetchall()
            ]
