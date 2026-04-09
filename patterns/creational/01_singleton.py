"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  SINGLETON — Creational Pattern                                             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  Intent:   Ensure a class has only ONE instance and provide a global        ║
║            access point to it.                                              ║
║                                                                             ║
║  Problem:  Some resources are expensive to create or must be shared         ║
║            (database connections, loggers, config managers). Creating        ║
║            multiple instances wastes resources or causes conflicts.         ║
║                                                                             ║
║  Solution: Override the class creation mechanism so that repeated           ║
║            instantiation always returns the same object.                    ║
║                                                                             ║
║  Use When:                                                                  ║
║    • You need exactly one instance of a class (DB connection pool)         ║
║    • You need a global access point with lazy initialization               ║
║    • You want controlled access to a sole resource                         ║
║                                                                             ║
║  Real-World Analogy:                                                        ║
║    A country has one government. No matter who asks "who is the             ║
║    government?", they always get the same answer.                           ║
║                                                                             ║
║  Python Bonus:                                                              ║
║    Python modules are natural singletons — importing the same module        ║
║    twice gives you the same object. For simple cases, just use a module!   ║
║                                                                             ║
║  Related Patterns:                                                          ║
║    • Factory Method — can use Singleton to ensure one factory exists       ║
║    • Facade — often implemented as a Singleton                             ║
║    • Flyweight — the flyweight factory is often a Singleton                ║
║                                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
import threading


# ─────────────────────────────────────────────────────
#  Approach 1: Classic Singleton via __new__
# ─────────────────────────────────────────────────────

class ClassicSingleton:
    """
    The simplest Singleton: override __new__ so only one
    instance is ever created.

    ⚠️  NOT thread-safe by default.
    """
    _instance: ClassicSingleton | None = None

    def __new__(cls) -> ClassicSingleton:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # __init__ runs EVERY time you call ClassicSingleton(),
        # so guard against re-initialization:
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self.value = None


# ─────────────────────────────────────────────────────
#  Approach 2: Thread-Safe Singleton (production-ready)
# ─────────────────────────────────────────────────────

class ThreadSafeSingleton:
    """
    Uses a lock to prevent race conditions when two threads
    try to create the instance simultaneously.
    """
    _instance: ThreadSafeSingleton | None = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> ThreadSafeSingleton:
        # Double-checked locking pattern:
        # First check (no lock) — fast path for subsequent calls.
        if cls._instance is None:
            with cls._lock:
                # Second check (with lock) — only ONE thread creates.
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance


# ─────────────────────────────────────────────────────
#  Approach 3: Metaclass Singleton (reusable)
# ─────────────────────────────────────────────────────

class SingletonMeta(type):
    """
    A metaclass that turns ANY class into a Singleton.

    Usage:
        class MyService(metaclass=SingletonMeta):
            pass
    """
    _instances: dict[type, object] = {}
    _lock: threading.Lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]


# ─────────────────────────────────────────────────────
#  Approach 4: Pythonic — Module-level (simplest!)
# ─────────────────────────────────────────────────────
#
#  In Python, a module is loaded once. So simply put your
#  "singleton" as a module-level variable:
#
#  # config.py
#  settings = {"debug": False, "db_url": "sqlite:///app.db"}
#
#  # anywhere.py
#  from config import settings  # always the same dict
#


# ═══════════════════════════════════════════════════════
#  REAL-WORLD SCENARIO: Database Connection Pool Manager
# ═══════════════════════════════════════════════════════

class DatabasePool(metaclass=SingletonMeta):
    """
    A database connection pool that must exist only once.
    Multiple parts of the app share the same pool of connections.
    """

    def __init__(self, db_url: str = "postgresql://localhost/mydb", pool_size: int = 5):
        # Guard against re-initialization (metaclass handles instance reuse,
        # but __init__ would still be called on subsequent calls)
        if hasattr(self, "_initialized"):
            return
        self._initialized = True
        self.db_url = db_url
        self.pool_size = pool_size
        self._connections: list[str] = []
        self._available: list[str] = []
        self._create_pool()

    def _create_pool(self):
        """Simulate creating a pool of database connections."""
        for i in range(self.pool_size):
            conn = f"Connection-{i+1}@{self.db_url}"
            self._connections.append(conn)
            self._available.append(conn)
        print(f"  [Pool] Created {self.pool_size} connections to {self.db_url}")

    def get_connection(self) -> str:
        """Get a connection from the pool."""
        if not self._available:
            raise RuntimeError("No available connections in the pool!")
        conn = self._available.pop()
        print(f"  [Pool] Checked out: {conn}")
        return conn

    def release_connection(self, conn: str):
        """Return a connection to the pool."""
        self._available.append(conn)
        print(f"  [Pool] Released:    {conn}")

    @property
    def available_count(self) -> int:
        return len(self._available)


# ─────────────────────────────────────────────────────
#  Demo
# ─────────────────────────────────────────────────────

def demo():
    print("=" * 60)
    print("  SINGLETON PATTERN DEMO")
    print("=" * 60)

    # --- Classic Singleton ---
    print("\n1. Classic Singleton:")
    a = ClassicSingleton()
    b = ClassicSingleton()
    a.value = 42
    print(f"   a.value = {a.value}")
    print(f"   b.value = {b.value}  (same object!)")
    print(f"   a is b? {a is b}")

    # --- Thread-safe Singleton ---
    print("\n2. Thread-Safe Singleton:")
    results = []

    def create_instance():
        instance = ThreadSafeSingleton()
        results.append(id(instance))

    threads = [threading.Thread(target=create_instance) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"   10 threads created instances. Unique IDs: {len(set(results))}")
    print(f"   All same object? {len(set(results)) == 1}")

    # --- Real-world: Database Pool ---
    print("\n3. Database Pool (real-world scenario):")
    pool1 = DatabasePool("postgresql://prod-server/app_db", pool_size=3)
    pool2 = DatabasePool()  # __init__ args ignored — already created!
    print(f"   pool1 is pool2? {pool1 is pool2}")
    print(f"   Available connections: {pool1.available_count}")

    conn = pool1.get_connection()
    print(f"   Available after checkout: {pool1.available_count}")
    pool2.release_connection(conn)  # pool2 IS pool1
    print(f"   Available after release: {pool1.available_count}")


if __name__ == "__main__":
    demo()
