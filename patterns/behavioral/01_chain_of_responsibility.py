"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  CHAIN OF RESPONSIBILITY — Behavioral Pattern                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  Intent:   Pass a request along a chain of handlers. Each handler          ║
║            decides to process the request or pass it to the next handler.  ║
║                                                                             ║
║  Problem:  A request could be handled by several different objects, and    ║
║            you don't know which one should handle it until runtime.        ║
║            Hard-coding the handler logic makes the sender tightly coupled. ║
║                                                                             ║
║  Solution: Build a chain of handler objects. Each handler either processes ║
║            the request or passes it along. The sender doesn't know which  ║
║            handler will ultimately process the request.                    ║
║                                                                             ║
║  Use When:                                                                  ║
║    • Multiple objects may handle a request, determined at runtime          ║
║    • You want to decouple sender from receiver                            ║
║    • You want to process a request through a pipeline of processors       ║
║                                                                             ║
║  Real-World Analogy:                                                        ║
║    Customer support escalation: Level 1 → Level 2 → Manager.              ║
║    Each level either solves it or escalates it.                            ║
║                                                                             ║
║  Related Patterns:                                                          ║
║    • Decorator — similar chain structure, but all decorators run           ║
║    • Command — the request itself can be a Command object                 ║
║    • Composite — chains can be built from a composite tree                ║
║                                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


# ═══════════════════════════════════════════════════════
#  Request
# ═══════════════════════════════════════════════════════

@dataclass
class HTTPRequest:
    method: str
    path: str
    headers: dict[str, str] = field(default_factory=dict)
    body: str = ""
    user: str | None = None
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class HTTPResponse:
    status: int
    body: str
    headers: dict[str, str] = field(default_factory=dict)


# ═══════════════════════════════════════════════════════
#  Abstract Handler
# ═══════════════════════════════════════════════════════

class Middleware(ABC):
    """
    Each middleware EITHER handles the request (returns a response)
    OR passes it to the next handler in the chain.
    """

    def __init__(self):
        self._next: Middleware | None = None

    def set_next(self, handler: Middleware) -> Middleware:
        """Set the next handler and return it (for chaining)."""
        self._next = handler
        return handler

    def handle(self, request: HTTPRequest) -> HTTPResponse:
        """Template: try to process, else pass to next."""
        response = self.process(request)
        if response is not None:
            return response
        if self._next is not None:
            return self._next.handle(request)
        return HTTPResponse(404, "No handler found for this request")

    @abstractmethod
    def process(self, request: HTTPRequest) -> HTTPResponse | None:
        """
        Process the request.
        Return an HTTPResponse to stop the chain.
        Return None to pass to the next handler.
        """
        pass


# ═══════════════════════════════════════════════════════
#  Concrete Handlers
# ═══════════════════════════════════════════════════════

class CORSMiddleware(Middleware):
    """Handles CORS preflight requests, passes others through."""

    def process(self, request: HTTPRequest) -> HTTPResponse | None:
        if request.method == "OPTIONS":
            print("  🌐 CORS: Handling preflight request")
            return HTTPResponse(
                200, "",
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE",
                }
            )
        # Add CORS headers for non-preflight (pass through)
        request.metadata["cors"] = True
        print("  🌐 CORS: Added headers, passing through →")
        return None


class AuthMiddleware(Middleware):
    """Validates authentication tokens."""

    VALID_TOKENS = {"admin-token-123", "user-token-456"}

    def process(self, request: HTTPRequest) -> HTTPResponse | None:
        token = request.headers.get("Authorization", "")
        if not token:
            print("  🔐 Auth: No token → 401")
            return HTTPResponse(401, "Unauthorized: Please provide a token")

        if token not in self.VALID_TOKENS:
            print(f"  🔐 Auth: Invalid token '{token}' → 403")
            return HTTPResponse(403, "Forbidden: Invalid token")

        # Set user based on token
        request.user = "admin" if "admin" in token else "user"
        print(f"  🔐 Auth: Authenticated as '{request.user}' →")
        return None


class RateLimitMiddleware(Middleware):
    """Simple rate limiter."""

    def __init__(self, max_requests: int = 5):
        super().__init__()
        self._max = max_requests
        self._counts: dict[str, int] = {}

    def process(self, request: HTTPRequest) -> HTTPResponse | None:
        user = request.user or "anonymous"
        self._counts[user] = self._counts.get(user, 0) + 1

        if self._counts[user] > self._max:
            print(f"  🚦 RateLimit: {user} exceeded {self._max} requests → 429")
            return HTTPResponse(429, "Too Many Requests")

        print(f"  🚦 RateLimit: {user} [{self._counts[user]}/{self._max}] →")
        return None


class ValidationMiddleware(Middleware):
    """Validates request body for POST/PUT."""

    def process(self, request: HTTPRequest) -> HTTPResponse | None:
        if request.method in ("POST", "PUT"):
            if not request.body:
                print("  ✅ Validation: Empty body for POST/PUT → 400")
                return HTTPResponse(400, "Bad Request: Body required for POST/PUT")
            print(f"  ✅ Validation: Body OK ({len(request.body)} chars) →")
        else:
            print(f"  ✅ Validation: {request.method} doesn't need body →")
        return None


class RouteHandler(Middleware):
    """The final handler — processes the actual request."""

    def process(self, request: HTTPRequest) -> HTTPResponse | None:
        print(f"  🎯 Router: Handling {request.method} {request.path}")
        routes = {
            "/users": f"User list (requested by {request.user})",
            "/products": f"Product catalog (requested by {request.user})",
            "/admin": f"Admin panel (requested by {request.user})",
        }
        body = routes.get(request.path)
        if body:
            return HTTPResponse(200, body)
        return HTTPResponse(404, f"Not Found: {request.path}")


# ═══════════════════════════════════════════════════════
#  Alternative: Functional Chain (Pythonic)
# ═══════════════════════════════════════════════════════

def build_chain(*handlers):
    """Build a chain from a list of handler functions."""
    def chain(request: HTTPRequest) -> HTTPResponse:
        for handler in handlers:
            result = handler(request)
            if result is not None:
                return result
        return HTTPResponse(404, "No handler matched")
    return chain


# ─────────────────────────────────────────────────────
#  Demo
# ─────────────────────────────────────────────────────

def demo():
    print("=" * 60)
    print("  CHAIN OF RESPONSIBILITY PATTERN DEMO")
    print("=" * 60)

    # --- Build the chain ---
    cors = CORSMiddleware()
    auth = AuthMiddleware()
    rate_limit = RateLimitMiddleware(max_requests=3)
    validation = ValidationMiddleware()
    router = RouteHandler()

    # Chain: CORS → Auth → RateLimit → Validation → Router
    cors.set_next(auth).set_next(rate_limit).set_next(validation).set_next(router)

    # --- Test requests ---
    test_cases = [
        ("CORS preflight", HTTPRequest("OPTIONS", "/users")),
        ("Valid GET", HTTPRequest("GET", "/users", headers={"Authorization": "admin-token-123"})),
        ("No auth token", HTTPRequest("GET", "/products")),
        ("Bad token", HTTPRequest("GET", "/users", headers={"Authorization": "bad-token"})),
        ("Valid POST", HTTPRequest("POST", "/users",
                                   headers={"Authorization": "user-token-456"},
                                   body='{"name": "Alice"}')),
        ("POST without body", HTTPRequest("POST", "/users",
                                          headers={"Authorization": "user-token-456"})),
        ("Unknown route", HTTPRequest("GET", "/unknown",
                                      headers={"Authorization": "admin-token-123"})),
    ]

    for name, request in test_cases:
        print(f"\n── {name}: {request.method} {request.path} ──")
        response = cors.handle(request)
        print(f"  📤 Response: {response.status} — {response.body}")

    print("\n💡 KEY INSIGHT:")
    print("   Each handler is independent — handles or passes.")
    print("   Adding/removing middleware doesn't affect others.")
    print("   The sender (client) doesn't know WHO handles it.")
    print("   Perfect for: HTTP middleware, event processing, validations.")


if __name__ == "__main__":
    demo()
