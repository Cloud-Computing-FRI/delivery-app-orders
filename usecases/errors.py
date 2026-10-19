"""Domain-level errors. No HTTP status codes -- the web layer maps these.

The gateway adapters raise these when they interpret a failure from another
service; the use case and web layer react to the meaning, not to a status code.
"""


class RestaurantUnavailable(Exception):
    pass


class RestaurantNotFound(Exception):
    pass


class MenuItemNotFound(Exception):
    pass


class NotificationUnavailable(Exception):
    pass
