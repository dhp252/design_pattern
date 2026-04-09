"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  PROXY — Structural Pattern                                                 ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  Intent:   Provide a surrogate or placeholder for another object to        ║
║            control access to it.                                            ║
║                                                                             ║
║  Problem:  You need to add access control, lazy loading, logging, or       ║
║            caching to an object without modifying it.                       ║
║                                                                             ║
║  Solution: Create a proxy class with the SAME interface as the real        ║
║            object. The proxy controls access, then delegates to the real   ║
║            object when appropriate.                                         ║
║                                                                             ║
║  Types of Proxy:                                                            ║
║    • Virtual Proxy — lazy initialization (expensive objects)               ║
║    • Protection Proxy — access control (permissions)                       ║
║    • Logging Proxy — track usage without modifying the real object         ║
║    • Caching Proxy — cache results of expensive operations                 ║
║    • Remote Proxy — represent an object in a different address space       ║
║                                                                             ║
║  vs Decorator:                                                              ║
║    Both wrap an object, but Proxy CONTROLS access while Decorator          ║
║    ADDS behavior. Proxy often manages the lifecycle of the real object.    ║
║                                                                             ║
║  Related Patterns:                                                          ║
║    • Decorator — same structure but adds behavior, not controls access    ║
║    • Adapter — different interface; Proxy has SAME interface              ║
║    • Facade — simplifies interface; Proxy doesn't change it              ║
║                                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from abc import ABC, abstractmethod
import time
from functools import lru_cache


# ═══════════════════════════════════════════════════════
#  Service Interface
# ═══════════════════════════════════════════════════════

class Database(ABC):
    """Interface that both the real DB and proxy implement."""

    @abstractmethod
    def query(self, sql: str) -> list[dict]:
        pass

    @abstractmethod
    def execute(self, sql: str) -> str:
        pass


# ═══════════════════════════════════════════════════════
#  Real Subject (expensive to create/use)
# ═══════════════════════════════════════════════════════

class RealDatabase(Database):
    """
    Simulates a real database that's expensive to connect to
    and slow for certain queries.
    """

    def __init__(self, connection_string: str):
        self._conn = connection_string
        # Simulate expensive connection setup
        print(f"    ⏳ RealDatabase: Connecting to {connection_string}...")
        time.sleep(0.01)  # Simulate connection delay
        self._data = {
            "users": [
                {"id": 1, "name": "Alice", "role": "admin"},
                {"id": 2, "name": "Bob", "role": "user"},
                {"id": 3, "name": "Charlie", "role": "user"},
            ]
        }
        print(f"    ✅ RealDatabase: Connected!")

    def query(self, sql: str) -> list[dict]:
        # Simulate work
        time.sleep(0.005)
        if "users" in sql.lower():
            return self._data["users"]
        return []

    def execute(self, sql: str) -> str:
        time.sleep(0.005)
        return f"Executed: {sql}"


# ═══════════════════════════════════════════════════════
#  1. Virtual Proxy (lazy initialization)
# ═══════════════════════════════════════════════════════

class LazyDatabaseProxy(Database):
    """
    VIRTUAL PROXY — delays creating the real database
    until it's actually needed.

    Why? The connection might be expensive and might not
    even be needed in some code paths.
    """

    def __init__(self, connection_string: str):
        self._connection_string = connection_string
        self._real_db: RealDatabase | None = None

    def _ensure_connected(self):
        """Lazy initialization — create real DB on first use."""
        if self._real_db is None:
            self._real_db = RealDatabase(self._connection_string)

    def query(self, sql: str) -> list[dict]:
        self._ensure_connected()
        return self._real_db.query(sql)

    def execute(self, sql: str) -> str:
        self._ensure_connected()
        return self._real_db.execute(sql)


# ═══════════════════════════════════════════════════════
#  2. Protection Proxy (access control)
# ═══════════════════════════════════════════════════════

class AccessControlProxy(Database):
    """
    PROTECTION PROXY — checks permissions before
    allowing operations on the real database.
    """

    def __init__(self, real_db: Database, user_role: str):
        self._real_db = real_db
        self._user_role = user_role

    def query(self, sql: str) -> list[dict]:
        # Everyone can read
        print(f"    🔐 Access: {self._user_role} → query: ALLOWED")
        return self._real_db.query(sql)

    def execute(self, sql: str) -> str:
        # Only admins can execute write operations
        dangerous_keywords = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER"]
        is_write = any(kw in sql.upper() for kw in dangerous_keywords)

        if is_write and self._user_role != "admin":
            msg = f"    🚫 Access: {self._user_role} → execute '{sql}': DENIED"
            print(msg)
            raise PermissionError(
                f"User role '{self._user_role}' cannot execute write operations"
            )

        print(f"    🔐 Access: {self._user_role} → execute: ALLOWED")
        return self._real_db.execute(sql)


# ═══════════════════════════════════════════════════════
#  3. Logging Proxy
# ═══════════════════════════════════════════════════════

class LoggingProxy(Database):
    """
    LOGGING PROXY — logs all database operations
    without modifying the real database.
    """

    def __init__(self, real_db: Database):
        self._real_db = real_db
        self._log: list[dict] = []

    def query(self, sql: str) -> list[dict]:
        start = time.perf_counter()
        result = self._real_db.query(sql)
        elapsed = time.perf_counter() - start
        entry = {"type": "query", "sql": sql, "time": elapsed, "rows": len(result)}
        self._log.append(entry)
        print(f"    📝 Log: QUERY '{sql}' → {len(result)} rows in {elapsed:.4f}s")
        return result

    def execute(self, sql: str) -> str:
        start = time.perf_counter()
        result = self._real_db.execute(sql)
        elapsed = time.perf_counter() - start
        entry = {"type": "execute", "sql": sql, "time": elapsed}
        self._log.append(entry)
        print(f"    📝 Log: EXEC  '{sql}' in {elapsed:.4f}s")
        return result

    @property
    def operation_log(self) -> list[dict]:
        return list(self._log)


# ═══════════════════════════════════════════════════════
#  4. Caching Proxy
# ═══════════════════════════════════════════════════════

class CachingProxy(Database):
    """
    CACHING PROXY — caches query results to avoid
    hitting the real database for repeated queries.
    """

    def __init__(self, real_db: Database, ttl_seconds: float = 60.0):
        self._real_db = real_db
        self._cache: dict[str, tuple[float, list[dict]]] = {}
        self._ttl = ttl_seconds
        self._hits = 0
        self._misses = 0

    def query(self, sql: str) -> list[dict]:
        now = time.time()
        if sql in self._cache:
            timestamp, result = self._cache[sql]
            if now - timestamp < self._ttl:
                self._hits += 1
                print(f"    ⚡ Cache: HIT '{sql}'")
                return result
        # Cache miss — query real DB
        self._misses += 1
        print(f"    ⚡ Cache: MISS '{sql}'")
        result = self._real_db.query(sql)
        self._cache[sql] = (now, result)
        return result

    def execute(self, sql: str) -> str:
        # Write operations invalidate the cache
        self._cache.clear()
        print(f"    ⚡ Cache: INVALIDATED (write operation)")
        return self._real_db.execute(sql)

    @property
    def stats(self) -> str:
        total = self._hits + self._misses
        ratio = self._hits / total * 100 if total else 0
        return f"Hits: {self._hits}, Misses: {self._misses}, Ratio: {ratio:.0f}%"


# ─────────────────────────────────────────────────────
#  Demo
# ─────────────────────────────────────────────────────

def demo():
    print("=" * 60)
    print("  PROXY PATTERN DEMO")
    print("=" * 60)

    # --- Virtual Proxy (lazy init) ---
    print("\n1. Virtual Proxy (lazy initialization):")
    print("   Creating proxy (NO connection yet)...")
    lazy_db = LazyDatabaseProxy("postgresql://prod/mydb")
    print("   Proxy created. DB not connected.")
    print("   First query triggers connection:")
    result = lazy_db.query("SELECT * FROM users")
    print(f"   Got {len(result)} users")
    print("   Second query (already connected):")
    result = lazy_db.query("SELECT * FROM users WHERE role='admin'")

    # --- Protection Proxy ---
    print("\n2. Protection Proxy (access control):")
    real_db = RealDatabase("postgresql://dev/testdb")
    admin_db = AccessControlProxy(real_db, "admin")
    user_db = AccessControlProxy(real_db, "user")

    # Admin can do anything
    admin_db.query("SELECT * FROM users")
    admin_db.execute("INSERT INTO users VALUES (4, 'Dana', 'user')")

    # Regular user can read but not write
    user_db.query("SELECT * FROM users")
    try:
        user_db.execute("DELETE FROM users WHERE id = 1")
    except PermissionError as e:
        print(f"    ❌ {e}")

    # --- Caching Proxy ---
    print("\n3. Caching Proxy:")
    real_db2 = RealDatabase("postgresql://dev/cachedb")
    cached_db = CachingProxy(real_db2)

    cached_db.query("SELECT * FROM users")        # MISS
    cached_db.query("SELECT * FROM users")        # HIT
    cached_db.query("SELECT * FROM users")        # HIT
    cached_db.query("SELECT name FROM users")     # MISS (different query)
    cached_db.execute("UPDATE users SET role='admin' WHERE id=2")  # Invalidates cache
    cached_db.query("SELECT * FROM users")        # MISS (cache was cleared)
    print(f"   Cache stats: {cached_db.stats}")

    # --- Stacking proxies ---
    print("\n4. Stacking Proxies (Logging + Access + Caching):")
    real_db3 = RealDatabase("postgresql://prod/stack")
    stacked = LoggingProxy(
        AccessControlProxy(
            CachingProxy(real_db3),
            user_role="admin"
        )
    )
    stacked.query("SELECT * FROM users")
    stacked.query("SELECT * FROM users")  # Cached!

    print("\n💡 KEY INSIGHT:")
    print("   All proxies have the SAME interface as the real DB.")
    print("   Client code doesn't know (or care) if it's using a")
    print("   proxy or the real thing. Proxies can be stacked!")


if __name__ == "__main__":
    demo()
