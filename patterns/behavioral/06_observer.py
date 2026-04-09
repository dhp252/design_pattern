"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  OBSERVER — Behavioral Pattern                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  Intent:   Define a one-to-many dependency between objects so that when    ║
║            one object changes state, all its dependents are notified       ║
║            and updated automatically.                                      ║
║                                                                             ║
║  Problem:  Multiple objects need to react when another object changes,     ║
║            but you don't want tight coupling between them.                 ║
║                                                                             ║
║  Solution: The Subject maintains a list of subscribers (Observers).        ║
║            When the subject's state changes, it notifies all observers.    ║
║            Observers can subscribe/unsubscribe at runtime.                  ║
║                                                                             ║
║  Use When:                                                                  ║
║    • Changes in one object should trigger updates in others               ║
║    • You don't know how many objects need to be updated                   ║
║    • You want loose coupling between the publisher and subscribers         ║
║                                                                             ║
║  Real-World Analogy:                                                        ║
║    Magazine subscription: you subscribe, get issues when published,        ║
║    and can unsubscribe anytime. The publisher doesn't need to know you.   ║
║                                                                             ║
║  Related Patterns:                                                          ║
║    • Mediator — centralizes communication; Observer is decentralized      ║
║    • Command — notifications can carry Command objects                    ║
║    • Singleton — event bus is often a singleton                           ║
║                                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable


# ═══════════════════════════════════════════════════════
#  Classic Observer (GoF style)
# ═══════════════════════════════════════════════════════

class Observer(ABC):
    @abstractmethod
    def update(self, subject: Subject, event: str, data: dict) -> None:
        pass


class Subject:
    """
    The Subject (Publisher) maintains a list of observers
    and notifies them of state changes.
    """

    def __init__(self):
        self._observers: dict[str, list[Observer]] = {}

    def subscribe(self, event: str, observer: Observer):
        if event not in self._observers:
            self._observers[event] = []
        self._observers[event].append(observer)

    def unsubscribe(self, event: str, observer: Observer):
        if event in self._observers:
            self._observers[event].remove(observer)

    def notify(self, event: str, data: dict = None):
        for observer in self._observers.get(event, []):
            observer.update(self, event, data or {})


# ═══════════════════════════════════════════════════════
#  Real-World: Stock Market Ticker
# ═══════════════════════════════════════════════════════

class StockMarket(Subject):
    """Publisher — tracks stock prices and notifies on changes."""

    def __init__(self):
        super().__init__()
        self._prices: dict[str, float] = {}

    def update_price(self, symbol: str, price: float):
        old_price = self._prices.get(symbol, 0)
        self._prices[symbol] = price
        change = ((price - old_price) / old_price * 100) if old_price else 0

        self.notify("price_change", {
            "symbol": symbol,
            "price": price,
            "old_price": old_price,
            "change_pct": change,
        })

        # Special events
        if change > 5:
            self.notify("spike", {"symbol": symbol, "change": change})
        elif change < -5:
            self.notify("crash", {"symbol": symbol, "change": change})

    def get_price(self, symbol: str) -> float:
        return self._prices.get(symbol, 0)


# --- Concrete Observers ---

class PriceDisplay(Observer):
    """Shows current prices in real-time."""

    def __init__(self, name: str):
        self.name = name

    def update(self, subject: Subject, event: str, data: dict):
        symbol = data["symbol"]
        price = data["price"]
        change = data.get("change_pct", 0)
        arrow = "📈" if change >= 0 else "📉"
        print(f"  {self.name}: {arrow} {symbol} ${price:.2f} ({change:+.1f}%)")


class AlertSystem(Observer):
    """Sends alerts on significant price movements."""

    def update(self, subject: Subject, event: str, data: dict):
        symbol = data["symbol"]
        change = data["change"]
        if event == "spike":
            print(f"  🚨 ALERT: {symbol} SPIKED {change:+.1f}%! Consider selling!")
        elif event == "crash":
            print(f"  🚨 ALERT: {symbol} CRASHED {change:+.1f}%! Consider buying!")


class TradeLog(Observer):
    """Logs all price changes for auditing."""

    def __init__(self):
        self.log: list[str] = []

    def update(self, subject: Subject, event: str, data: dict):
        entry = f"{data['symbol']}: ${data.get('old_price', 0):.2f} → ${data['price']:.2f}"
        self.log.append(entry)


# ═══════════════════════════════════════════════════════
#  Pythonic Alternative: Callback-based Observer
# ═══════════════════════════════════════════════════════

class EventEmitter:
    """
    Python-style event system using plain functions as callbacks.
    No need for an Observer interface!
    """

    def __init__(self):
        self._listeners: dict[str, list[Callable]] = {}

    def on(self, event: str, callback: Callable = None) -> Callable:
        """
        Subscribe a callback. Can be used two ways:
          1. Direct call: emitter.on("event", my_func)
          2. Decorator:   @emitter.on("event")
        """
        if callback is not None:
            # Direct call
            self._listeners.setdefault(event, []).append(callback)
            return callback
        else:
            # Decorator factory
            def decorator(func: Callable) -> Callable:
                self._listeners.setdefault(event, []).append(func)
                return func
            return decorator

    def off(self, event: str, callback: Callable):
        if event in self._listeners:
            self._listeners[event].remove(callback)

    def emit(self, event: str, **kwargs):
        for callback in self._listeners.get(event, []):
            callback(**kwargs)

    def once(self, event: str, callback: Callable):
        """Subscribe a callback that fires only once."""
        def wrapper(**kwargs):
            callback(**kwargs)
            self.off(event, wrapper)
        self.on(event, wrapper)


# ═══════════════════════════════════════════════════════
#  Pythonic: Using as decorator
# ═══════════════════════════════════════════════════════

class UserService(EventEmitter):
    """A service that emits events when users are created/deleted."""

    def __init__(self):
        super().__init__()
        self._users: dict[int, str] = {}
        self._next_id = 1

    def create_user(self, name: str) -> int:
        user_id = self._next_id
        self._next_id += 1
        self._users[user_id] = name
        self.emit("user_created", user_id=user_id, name=name)
        return user_id

    def delete_user(self, user_id: int):
        name = self._users.pop(user_id, None)
        if name:
            self.emit("user_deleted", user_id=user_id, name=name)


# ─────────────────────────────────────────────────────
#  Demo
# ─────────────────────────────────────────────────────

def demo():
    print("=" * 60)
    print("  OBSERVER PATTERN DEMO")
    print("=" * 60)

    # --- Stock Market ---
    market = StockMarket()

    display1 = PriceDisplay("📊 Dashboard")
    display2 = PriceDisplay("📱 Mobile")
    alert_sys = AlertSystem()
    trade_log = TradeLog()

    # Subscribe to different events
    market.subscribe("price_change", display1)
    market.subscribe("price_change", display2)
    market.subscribe("price_change", trade_log)
    market.subscribe("spike", alert_sys)
    market.subscribe("crash", alert_sys)

    print("\n1. Stock Price Updates:")
    market.update_price("AAPL", 150.00)
    market.update_price("GOOGL", 2800.00)

    print("\n2. Price spike triggers alert:")
    market.update_price("AAPL", 165.00)  # +10% spike

    print("\n3. Unsubscribe mobile display:")
    market.unsubscribe("price_change", display2)
    market.update_price("GOOGL", 2600.00)  # Only dashboard shows

    print(f"\n4. Trade Log: {len(trade_log.log)} entries:")
    for entry in trade_log.log:
        print(f"   📝 {entry}")

    # --- Pythonic callback-based ---
    print("\n\n5. Pythonic EventEmitter:")
    user_svc = UserService()

    # Register callbacks as plain functions
    @user_svc.on("user_created")
    def send_welcome(user_id, name):
        print(f"   📧 Sending welcome email to {name} (id: {user_id})")

    @user_svc.on("user_created")
    def log_creation(user_id, name):
        print(f"   📝 Logged: User {name} created with id {user_id}")

    @user_svc.on("user_deleted")
    def cleanup(user_id, name):
        print(f"   🧹 Cleaning up data for {name} (id: {user_id})")

    # One-time listener
    user_svc.once("user_created", lambda user_id, name:
                   print(f"   🎉 First user bonus for {name}!"))

    print("   Creating users:")
    user_svc.create_user("Alice")  # Triggers welcome + log + first-user bonus
    user_svc.create_user("Bob")    # Triggers welcome + log (no bonus — it was `once`)

    print("\n   Deleting user:")
    user_svc.delete_user(1)

    print("\n💡 KEY INSIGHT:")
    print("   The publisher (StockMarket) doesn't know its subscribers.")
    print("   Observers subscribe/unsubscribe dynamically at runtime.")
    print("   The Pythonic version uses plain functions (callbacks)")
    print("   instead of requiring an Observer class hierarchy.")


if __name__ == "__main__":
    demo()
