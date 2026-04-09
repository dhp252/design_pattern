"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  DECORATOR — Structural Pattern                                             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  Intent:   Attach additional responsibilities to an object dynamically.    ║
║            Provide a flexible alternative to subclassing for extending     ║
║            functionality.                                                   ║
║                                                                             ║
║  Problem:  You want to add behavior to objects at runtime without          ║
║            affecting other objects of the same class. Subclassing for      ║
║            every combination leads to class explosion.                      ║
║                                                                             ║
║  Solution: Wrap the object in a decorator that has the same interface      ║
║            but adds behavior before/after delegating to the wrapped object. ║
║                                                                             ║
║  Use When:                                                                  ║
║    • You need to add responsibilities dynamically and transparently        ║
║    • Subclassing to extend would produce too many combinations             ║
║    • You want to compose behaviors like building blocks                    ║
║                                                                             ║
║  Real-World Analogy:                                                        ║
║    Wearing clothes: you put on a shirt, then a sweater, then a jacket.     ║
║    Each layer adds warmth but you're still "you". You can remove/add       ║
║    layers independently.                                                    ║
║                                                                             ║
║  Python Bonus:                                                              ║
║    Python has @decorator syntax for functions! The GoF Decorator is for    ║
║    objects, but the concept maps beautifully to Python's function           ║
║    decorators using closures and functools.wraps.                           ║
║                                                                             ║
║  Related Patterns:                                                          ║
║    • Adapter — changes interface; Decorator keeps the SAME interface      ║
║    • Composite — similar structure, but Composite aggregates children     ║
║    • Strategy — changes guts; Decorator changes skin                      ║
║    • Proxy — same interface, but controls access rather than adds behavior ║
║                                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from abc import ABC, abstractmethod
import functools
import time


# ═══════════════════════════════════════════════════════
#  Classic GoF Style: Coffee Shop Example
# ═══════════════════════════════════════════════════════

class Beverage(ABC):
    """Component interface — all beverages and decorators share this."""

    @abstractmethod
    def cost(self) -> float:
        pass

    @abstractmethod
    def description(self) -> str:
        pass


# --- Concrete components (base beverages) ---

class Espresso(Beverage):
    def cost(self) -> float:
        return 2.50

    def description(self) -> str:
        return "Espresso"


class Latte(Beverage):
    def cost(self) -> float:
        return 3.50

    def description(self) -> str:
        return "Latte"


# --- Decorators (toppings) ---

class BeverageDecorator(Beverage, ABC):
    """Base decorator — wraps a beverage and extends it."""

    def __init__(self, beverage: Beverage):
        self._beverage = beverage


class WhipCream(BeverageDecorator):
    def cost(self) -> float:
        return self._beverage.cost() + 0.75

    def description(self) -> str:
        return f"{self._beverage.description()} + Whip Cream"


class CaramelDrizzle(BeverageDecorator):
    def cost(self) -> float:
        return self._beverage.cost() + 0.50

    def description(self) -> str:
        return f"{self._beverage.description()} + Caramel"


class ExtraShot(BeverageDecorator):
    def cost(self) -> float:
        return self._beverage.cost() + 1.00

    def description(self) -> str:
        return f"{self._beverage.description()} + Extra Shot"


class OatMilk(BeverageDecorator):
    def cost(self) -> float:
        return self._beverage.cost() + 0.60

    def description(self) -> str:
        return f"{self._beverage.description()} + Oat Milk"


# ═══════════════════════════════════════════════════════
#  Real-World: API Middleware Pipeline
# ═══════════════════════════════════════════════════════

class Handler(ABC):
    """A request handler interface."""

    @abstractmethod
    def handle(self, request: dict) -> dict:
        pass


class CoreAPIHandler(Handler):
    """The actual business logic handler."""

    def handle(self, request: dict) -> dict:
        endpoint = request.get("endpoint", "/")
        return {"status": 200, "body": f"Response from {endpoint}", "endpoint": endpoint}


class HandlerDecorator(Handler, ABC):
    def __init__(self, handler: Handler):
        self._handler = handler


class AuthMiddleware(HandlerDecorator):
    """Check authentication before passing to the next handler."""

    def handle(self, request: dict) -> dict:
        token = request.get("auth_token", "")
        if not token:
            return {"status": 401, "body": "Unauthorized: missing token"}
        if token != "valid_token":
            return {"status": 403, "body": "Forbidden: invalid token"}
        print("    ✅ Auth: Token validated")
        return self._handler.handle(request)


class LoggingMiddleware(HandlerDecorator):
    """Log the request and response."""

    def handle(self, request: dict) -> dict:
        endpoint = request.get("endpoint", "?")
        method = request.get("method", "GET")
        print(f"    📝 Log: {method} {endpoint}")
        response = self._handler.handle(request)
        print(f"    📝 Log: → {response['status']}")
        return response


class RateLimitMiddleware(HandlerDecorator):
    """Simple rate limiting decorator."""

    def __init__(self, handler: Handler, max_requests: int = 5):
        super().__init__(handler)
        self._max = max_requests
        self._count = 0

    def handle(self, request: dict) -> dict:
        self._count += 1
        if self._count > self._max:
            return {"status": 429, "body": "Too Many Requests"}
        print(f"    🚦 Rate: {self._count}/{self._max}")
        return self._handler.handle(request)


class CacheMiddleware(HandlerDecorator):
    """Cache responses by endpoint."""

    def __init__(self, handler: Handler):
        super().__init__(handler)
        self._cache: dict[str, dict] = {}

    def handle(self, request: dict) -> dict:
        key = request.get("endpoint", "")
        if key in self._cache:
            print(f"    ⚡ Cache: HIT for {key}")
            return self._cache[key]
        print(f"    ⚡ Cache: MISS for {key}")
        response = self._handler.handle(request)
        self._cache[key] = response
        return response


# ═══════════════════════════════════════════════════════
#  Python-Style: Function Decorators
# ═══════════════════════════════════════════════════════

def timer(func):
    """Measure execution time (Python function decorator)."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"    ⏱️  {func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper


def retry(max_retries: int = 3):
    """Retry on failure (parameterized decorator)."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"    🔄 Retry {attempt}/{max_retries}: {e}")
                    if attempt == max_retries:
                        raise
        return wrapper
    return decorator


def validate_args(**validators):
    """Validate function arguments using decorators."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for param, check in validators.items():
                if param in kwargs:
                    if not check(kwargs[param]):
                        raise ValueError(f"Validation failed for '{param}'")
            return func(*args, **kwargs)
        return wrapper
    return decorator


@timer
@retry(max_retries=2)
def fetch_data(url: str) -> str:
    """A function decorated with timer + retry."""
    if "fail" in url:
        raise ConnectionError(f"Cannot connect to {url}")
    return f"Data from {url}"


# ─────────────────────────────────────────────────────
#  Demo
# ─────────────────────────────────────────────────────

def demo():
    print("=" * 60)
    print("  DECORATOR PATTERN DEMO")
    print("=" * 60)

    # --- Coffee shop ---
    print("\n1. Coffee Shop — stacking toppings:")
    drinks: list[Beverage] = [
        Espresso(),
        ExtraShot(Espresso()),
        WhipCream(CaramelDrizzle(Latte())),
        OatMilk(ExtraShot(WhipCream(Latte()))),
    ]
    for drink in drinks:
        print(f"   {drink.description():<50} ${drink.cost():.2f}")

    # --- API middleware pipeline ---
    print("\n2. API Middleware Pipeline:")
    # Build the pipeline inside-out:
    # Request → Logging → Auth → RateLimit → Cache → CoreHandler
    pipeline = LoggingMiddleware(
        AuthMiddleware(
            RateLimitMiddleware(
                CacheMiddleware(
                    CoreAPIHandler()
                ),
                max_requests=3
            )
        )
    )

    requests = [
        {"endpoint": "/users", "method": "GET", "auth_token": "valid_token"},
        {"endpoint": "/users", "method": "GET", "auth_token": "valid_token"},  # cached
        {"endpoint": "/data", "method": "GET", "auth_token": ""},  # no auth
        {"endpoint": "/admin", "method": "POST", "auth_token": "bad_token"},  # bad token
    ]

    for i, req in enumerate(requests):
        print(f"\n   Request {i+1}: {req.get('method')} {req.get('endpoint')}")
        resp = pipeline.handle(req)
        print(f"   Response: {resp['status']} — {resp['body']}")

    # --- Python function decorators ---
    print("\n\n3. Python Function Decorators:")
    print("   Successful call:")
    result = fetch_data(url="https://api.example.com/data")
    print(f"   Result: {result}")

    print("\n   Failing call (with retry):")
    try:
        fetch_data(url="https://fail.example.com")
    except ConnectionError as e:
        print(f"   Final error: {e}")

    print("\n💡 KEY INSIGHT:")
    print("   Decorators wrap objects with the SAME interface.")
    print("   You can stack them like layers — each adds one concern.")
    print("   Coffee: Espresso → +Whip → +Caramel → still a Beverage.")
    print("   API: Handler → +Auth → +Logging → still a Handler.")


if __name__ == "__main__":
    demo()
