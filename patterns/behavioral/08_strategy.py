"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  STRATEGY — Behavioral Pattern                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  Intent:   Define a family of algorithms, encapsulate each one, and make   ║
║            them interchangeable. Strategy lets the algorithm vary           ║
║            independently from clients that use it.                          ║
║                                                                             ║
║  Problem:  You have multiple ways to do the same thing (different sorting  ║
║            algorithms, different routing strategies, etc.) and you want    ║
║            to swap between them without changing the client code.           ║
║                                                                             ║
║  Solution: Extract each algorithm into its own class (or function) with   ║
║            a common interface. The context object holds a reference to     ║
║            a strategy and delegates the work.                              ║
║                                                                             ║
║  Use When:                                                                  ║
║    • Multiple algorithms exist for the same task                           ║
║    • You want to switch algorithms at runtime                              ║
║    • You want to isolate algorithm-specific data/behavior                  ║
║    • A class has many conditional behaviors that differ in variants        ║
║                                                                             ║
║  Python Bonus:                                                              ║
║    In Python, functions are first-class objects, so you can use plain      ║
║    functions as strategies — no need for a class hierarchy!               ║
║                                                                             ║
║  vs State:                                                                  ║
║    Both use the same structure, but Strategy is chosen BY THE CLIENT;     ║
║    State changes AUTOMATICALLY based on internal transitions.              ║
║                                                                             ║
║  Related Patterns:                                                          ║
║    • State — same structure, different intent                             ║
║    • Factory Method — can select the right strategy                       ║
║    • Decorator — Strategy changes the core; Decorator wraps it            ║
║    • Template Method — inversion of Template Method                       ║
║                                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
import math


# ═══════════════════════════════════════════════════════
#  Strategy Interface
# ═══════════════════════════════════════════════════════

@dataclass
class Route:
    name: str
    distance_km: float
    estimated_time_min: float
    fuel_cost: float
    scenic_score: int  # 1-10


class RouteStrategy(ABC):
    """Each strategy defines HOW to rank and select a route."""

    @abstractmethod
    def select_route(self, routes: list[Route]) -> Route:
        pass

    @abstractmethod
    def name(self) -> str:
        pass


# ═══════════════════════════════════════════════════════
#  Concrete Strategies (class-based)
# ═══════════════════════════════════════════════════════

class FastestRoute(RouteStrategy):
    def select_route(self, routes: list[Route]) -> Route:
        return min(routes, key=lambda r: r.estimated_time_min)

    def name(self) -> str:
        return "⚡ Fastest"


class ShortestRoute(RouteStrategy):
    def select_route(self, routes: list[Route]) -> Route:
        return min(routes, key=lambda r: r.distance_km)

    def name(self) -> str:
        return "📏 Shortest"


class CheapestRoute(RouteStrategy):
    def select_route(self, routes: list[Route]) -> Route:
        return min(routes, key=lambda r: r.fuel_cost)

    def name(self) -> str:
        return "💰 Cheapest"


class ScenicRoute(RouteStrategy):
    def select_route(self, routes: list[Route]) -> Route:
        return max(routes, key=lambda r: r.scenic_score)

    def name(self) -> str:
        return "🌄 Most Scenic"


class BalancedRoute(RouteStrategy):
    """Multi-criteria: weighted combination of all factors."""

    def __init__(self, time_weight=0.4, dist_weight=0.2,
                 cost_weight=0.2, scenic_weight=0.2):
        self.tw = time_weight
        self.dw = dist_weight
        self.cw = cost_weight
        self.sw = scenic_weight

    def select_route(self, routes: list[Route]) -> Route:
        # Normalize each metric to 0-1 range, then compute weighted score
        max_time = max(r.estimated_time_min for r in routes) or 1
        max_dist = max(r.distance_km for r in routes) or 1
        max_cost = max(r.fuel_cost for r in routes) or 1

        def score(r: Route) -> float:
            time_score = 1 - r.estimated_time_min / max_time
            dist_score = 1 - r.distance_km / max_dist
            cost_score = 1 - r.fuel_cost / max_cost
            scenic_norm = r.scenic_score / 10
            return (self.tw * time_score + self.dw * dist_score +
                    self.cw * cost_score + self.sw * scenic_norm)

        return max(routes, key=score)

    def name(self) -> str:
        return "⚖️  Balanced"


# ═══════════════════════════════════════════════════════
#  Context
# ═══════════════════════════════════════════════════════

class Navigator:
    """
    CONTEXT — uses a strategy to select the best route.
    The strategy can be swapped at runtime.
    """

    def __init__(self, strategy: RouteStrategy | None = None):
        self._strategy = strategy or FastestRoute()

    def set_strategy(self, strategy: RouteStrategy):
        self._strategy = strategy

    def navigate(self, origin: str, destination: str,
                 routes: list[Route]) -> str:
        selected = self._strategy.select_route(routes)
        lines = [
            f"  🗺️  {origin} → {destination}",
            f"  Strategy: {self._strategy.name()}",
            f"  Selected: {selected.name}",
            f"    Distance: {selected.distance_km:.1f} km",
            f"    Time:     {selected.estimated_time_min:.0f} min",
            f"    Fuel:     ${selected.fuel_cost:.2f}",
            f"    Scenic:   {'⭐' * selected.scenic_score}",
        ]
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════
#  Pythonic: Functions as Strategies
# ═══════════════════════════════════════════════════════

def navigate_with(routes: list[Route],
                  key_func) -> Route:
    """
    In Python, you don't always need a Strategy class.
    A simple function (or lambda) works too!
    """
    return key_func(routes)


# ═══════════════════════════════════════════════════════
#  Another Example: Compression Strategies
# ═══════════════════════════════════════════════════════

class CompressionStrategy(ABC):
    @abstractmethod
    def compress(self, data: str) -> tuple[str, float]:
        """Returns (compressed_repr, compression_ratio)."""
        pass

    @abstractmethod
    def name(self) -> str:
        pass


class NoCompression(CompressionStrategy):
    def compress(self, data: str) -> tuple[str, float]:
        return data, 1.0

    def name(self) -> str:
        return "None"


class RunLengthEncoding(CompressionStrategy):
    def compress(self, data: str) -> tuple[str, float]:
        if not data:
            return "", 1.0
        result = []
        count = 1
        for i in range(1, len(data)):
            if data[i] == data[i-1]:
                count += 1
            else:
                result.append(f"{data[i-1]}{count}" if count > 1 else data[i-1])
                count = 1
        result.append(f"{data[-1]}{count}" if count > 1 else data[-1])
        compressed = "".join(result)
        return compressed, len(compressed) / len(data)

    def name(self) -> str:
        return "RLE"


class DictionaryCompression(CompressionStrategy):
    def compress(self, data: str) -> tuple[str, float]:
        # Simple word-level dictionary compression
        words = data.split()
        dictionary = {}
        encoded = []
        for word in words:
            if word not in dictionary:
                dictionary[word] = f"${len(dictionary)}"
            encoded.append(dictionary[word])
        compressed = " ".join(encoded) + f" | DICT:{dictionary}"
        return compressed, len(compressed) / len(data) if data else 1.0

    def name(self) -> str:
        return "Dictionary"


class FileProcessor:
    """Context that uses a compression strategy."""

    def __init__(self, strategy: CompressionStrategy = None):
        self._strategy = strategy or NoCompression()

    def set_strategy(self, strategy: CompressionStrategy):
        self._strategy = strategy

    def process(self, data: str) -> str:
        compressed, ratio = self._strategy.compress(data)
        return (f"  [{self._strategy.name()}] "
                f"Ratio: {ratio:.2%} | "
                f"Original: {len(data)} chars → Compressed: {len(compressed)} chars")


# ─────────────────────────────────────────────────────
#  Demo
# ─────────────────────────────────────────────────────

def demo():
    print("=" * 60)
    print("  STRATEGY PATTERN DEMO")
    print("=" * 60)

    routes = [
        Route("Highway A1", 120, 75, 15.00, 2),
        Route("Country Road B7", 95, 110, 12.00, 8),
        Route("Expressway E5", 140, 60, 18.00, 1),
        Route("Coastal Road C3", 105, 100, 13.50, 10),
    ]

    nav = Navigator()

    # --- Try each strategy ---
    strategies: list[RouteStrategy] = [
        FastestRoute(),
        ShortestRoute(),
        CheapestRoute(),
        ScenicRoute(),
        BalancedRoute(),
    ]

    print("\n1. Same routes, different strategies:")
    for strategy in strategies:
        nav.set_strategy(strategy)
        print(nav.navigate("Home", "Beach House", routes))
        print()

    # --- Pythonic: functions as strategies ---
    print("2. Pythonic — functions as strategies:")
    fastest = navigate_with(routes, lambda rs: min(rs, key=lambda r: r.estimated_time_min))
    print(f"  Fastest (lambda): {fastest.name} ({fastest.estimated_time_min} min)")

    scenic = navigate_with(routes, lambda rs: max(rs, key=lambda r: r.scenic_score))
    print(f"  Scenic (lambda):  {scenic.name} ({'⭐' * scenic.scenic_score})")

    # --- Compression strategies ---
    print("\n3. Compression Strategies:")
    data = "aaabbbccccddddddeeeeeeeeee test test test hello hello world world world"
    processor = FileProcessor()

    for strategy in [NoCompression(), RunLengthEncoding(), DictionaryCompression()]:
        processor.set_strategy(strategy)
        print(processor.process(data))

    print("\n💡 KEY INSIGHT:")
    print("   Strategy = family of interchangeable algorithms.")
    print("   The Context delegates work to the current Strategy.")
    print("   In Python, simple functions often replace Strategy classes.")
    print("   Strategy is chosen BY THE CLIENT (vs State which auto-transitions).")


if __name__ == "__main__":
    demo()
