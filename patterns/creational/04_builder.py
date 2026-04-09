"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  BUILDER — Creational Pattern                                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  Intent:   Separate the construction of a complex object from its           ║
║            representation, allowing the same process to create different    ║
║            representations.                                                 ║
║                                                                             ║
║  Problem:  You have an object with many optional parameters (a "telescoping ║
║            constructor"). Or construction requires multiple steps that      ║
║            must happen in a specific order.                                 ║
║                                                                             ║
║  Solution: Extract the construction code into a separate Builder class.    ║
║            Optionally use a Director to define common build sequences.      ║
║                                                                             ║
║  Use When:                                                                  ║
║    • Complex objects require step-by-step construction                     ║
║    • You need to create different representations of the same object       ║
║    • Constructor has too many parameters (especially optional ones)         ║
║                                                                             ║
║  Real-World Analogy:                                                        ║
║    Building a house: you lay the foundation, build walls, add a roof,      ║
║    install windows. The same construction process can build a wooden        ║
║    cottage or a stone castle.                                               ║
║                                                                             ║
║  Python Bonus:                                                              ║
║    Method chaining (fluent interface) makes builders feel natural.          ║
║    Python's **kwargs and dataclasses sometimes replace the need for         ║
║    a builder, but complex multi-step construction still benefits.           ║
║                                                                             ║
║  Related Patterns:                                                          ║
║    • Abstract Factory — also creates objects, but in one step              ║
║    • Composite — builders often construct Composite trees                  ║
║    • Prototype — Builder builds step by step; Prototype copies in one go   ║
║                                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


# ═══════════════════════════════════════════════════════
#  The Product
# ═══════════════════════════════════════════════════════

@dataclass
class SQLQuery:
    """A complex SQL query built step by step."""
    query_type: str = "SELECT"
    table: str = ""
    columns: list[str] = field(default_factory=lambda: ["*"])
    conditions: list[str] = field(default_factory=list)
    joins: list[str] = field(default_factory=list)
    order_by: list[str] = field(default_factory=list)
    group_by: list[str] = field(default_factory=list)
    having: str = ""
    limit: int | None = None
    offset: int | None = None

    def to_sql(self) -> str:
        """Generate the final SQL string."""
        parts = [f"{self.query_type} {', '.join(self.columns)}"]
        parts.append(f"FROM {self.table}")

        for join in self.joins:
            parts.append(join)
        if self.conditions:
            parts.append(f"WHERE {' AND '.join(self.conditions)}")
        if self.group_by:
            parts.append(f"GROUP BY {', '.join(self.group_by)}")
        if self.having:
            parts.append(f"HAVING {self.having}")
        if self.order_by:
            parts.append(f"ORDER BY {', '.join(self.order_by)}")
        if self.limit is not None:
            parts.append(f"LIMIT {self.limit}")
        if self.offset is not None:
            parts.append(f"OFFSET {self.offset}")

        return "\n  ".join(parts) + ";"


# ═══════════════════════════════════════════════════════
#  The Builder (with fluent interface)
# ═══════════════════════════════════════════════════════

class QueryBuilder:
    """
    Builds SQL queries step by step with method chaining.

    Each method returns `self` so you can chain:
        query = (QueryBuilder()
                    .select("name", "email")
                    .from_table("users")
                    .where("active = true")
                    .order("name ASC")
                    .build())
    """

    def __init__(self):
        self._query = SQLQuery()

    def select(self, *columns: str) -> QueryBuilder:
        self._query.query_type = "SELECT"
        if columns:
            self._query.columns = list(columns)
        return self

    def from_table(self, table: str) -> QueryBuilder:
        self._query.table = table
        return self

    def where(self, condition: str) -> QueryBuilder:
        self._query.conditions.append(condition)
        return self

    def join(self, table: str, on: str, join_type: str = "INNER") -> QueryBuilder:
        self._query.joins.append(f"{join_type} JOIN {table} ON {on}")
        return self

    def left_join(self, table: str, on: str) -> QueryBuilder:
        return self.join(table, on, "LEFT")

    def order(self, *columns: str) -> QueryBuilder:
        self._query.order_by.extend(columns)
        return self

    def group(self, *columns: str) -> QueryBuilder:
        self._query.group_by.extend(columns)
        return self

    def having(self, condition: str) -> QueryBuilder:
        self._query.having = condition
        return self

    def limit(self, n: int) -> QueryBuilder:
        self._query.limit = n
        return self

    def offset(self, n: int) -> QueryBuilder:
        self._query.offset = n
        return self

    def build(self) -> SQLQuery:
        """Return the constructed query and reset the builder."""
        query = self._query
        self._query = SQLQuery()  # Reset for reuse
        return query


# ═══════════════════════════════════════════════════════
#  The Director — defines common build sequences
# ═══════════════════════════════════════════════════════

class QueryDirector:
    """
    The Director knows HOW to use the builder to create
    commonly-used query shapes. The client doesn't need to
    remember the exact build steps.
    """

    @staticmethod
    def user_listing(builder: QueryBuilder) -> SQLQuery:
        """Standard paginated user listing."""
        return (builder
                .select("id", "name", "email", "role")
                .from_table("users")
                .where("active = true")
                .order("name ASC")
                .limit(20)
                .build())

    @staticmethod
    def user_activity_report(builder: QueryBuilder) -> SQLQuery:
        """Aggregated user activity with join."""
        return (builder
                .select("u.name", "COUNT(a.id) AS actions", "MAX(a.timestamp) AS last_active")
                .from_table("users u")
                .left_join("activities a", "a.user_id = u.id")
                .where("u.active = true")
                .group("u.name")
                .having("COUNT(a.id) > 0")
                .order("actions DESC")
                .limit(50)
                .build())

    @staticmethod
    def search_users(builder: QueryBuilder, term: str) -> SQLQuery:
        """Search users by name or email."""
        return (builder
                .select("id", "name", "email", "avatar_url")
                .from_table("users")
                .where("active = true")
                .where(f"(name ILIKE '%{term}%' OR email ILIKE '%{term}%')")
                .order("name ASC")
                .limit(10)
                .build())


# ═══════════════════════════════════════════════════════
#  Alternative: Builder for a different product
# ═══════════════════════════════════════════════════════

@dataclass
class HTTPRequest:
    method: str = "GET"
    url: str = ""
    headers: dict[str, str] = field(default_factory=dict)
    body: str | None = None
    timeout: int = 30
    retries: int = 0

    def __str__(self) -> str:
        lines = [f"{self.method} {self.url}"]
        for k, v in self.headers.items():
            lines.append(f"  {k}: {v}")
        if self.body:
            lines.append(f"  Body: {self.body[:50]}...")
        lines.append(f"  Timeout: {self.timeout}s, Retries: {self.retries}")
        return "\n".join(lines)


class RequestBuilder:
    def __init__(self, method: str, url: str):
        self._req = HTTPRequest(method=method, url=url)

    def header(self, key: str, value: str) -> RequestBuilder:
        self._req.headers[key] = value
        return self

    def auth(self, token: str) -> RequestBuilder:
        self._req.headers["Authorization"] = f"Bearer {token}"
        return self

    def json_body(self, body: str) -> RequestBuilder:
        self._req.headers["Content-Type"] = "application/json"
        self._req.body = body
        return self

    def timeout(self, seconds: int) -> RequestBuilder:
        self._req.timeout = seconds
        return self

    def retries(self, n: int) -> RequestBuilder:
        self._req.retries = n
        return self

    def build(self) -> HTTPRequest:
        req = self._req
        self._req = HTTPRequest()
        return req


# ─────────────────────────────────────────────────────
#  Demo
# ─────────────────────────────────────────────────────

def demo():
    print("=" * 60)
    print("  BUILDER PATTERN DEMO")
    print("=" * 60)

    builder = QueryBuilder()

    # --- Manual build ---
    print("\n1. Manual query building (fluent interface):")
    query = (builder
             .select("p.name", "p.price", "c.name AS category")
             .from_table("products p")
             .join("categories c", "c.id = p.category_id")
             .where("p.price > 100")
             .where("p.in_stock = true")
             .order("p.price DESC")
             .limit(25)
             .build())
    print(f"  {query.to_sql()}")

    # --- Director builds ---
    print("\n2. Director — standard user listing:")
    query = QueryDirector.user_listing(builder)
    print(f"  {query.to_sql()}")

    print("\n3. Director — activity report:")
    query = QueryDirector.user_activity_report(builder)
    print(f"  {query.to_sql()}")

    print("\n4. Director — search users:")
    query = QueryDirector.search_users(builder, "alice")
    print(f"  {query.to_sql()}")

    # --- HTTP Request Builder ---
    print("\n5. HTTP Request Builder (different product):")
    req = (RequestBuilder("POST", "https://api.example.com/users")
           .auth("sk_live_abc123")
           .json_body('{"name": "Alice", "role": "admin"}')
           .timeout(10)
           .retries(3)
           .build())
    print(f"  {req}")

    print("\n💡 KEY INSIGHT:")
    print("   The Builder separates HOW to construct from WHAT to construct.")
    print("   The Director encapsulates common build recipes.")
    print("   The client only needs to know the builder's fluent API.")


if __name__ == "__main__":
    demo()
