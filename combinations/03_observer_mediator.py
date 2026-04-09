"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  COMBINATION: Observer + Mediator                                           ║
║  Real-World App: Event-Driven Dashboard                                     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  How they combine:                                                          ║
║    • Mediator centralizes communication between dashboard widgets          ║
║    • Observer lets widgets subscribe to data changes                       ║
║    Widgets never talk to each other — only through the mediator.          ║
║                                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable


# ═══════════════════════════════════════════════════════
#  Observer: Event system within the mediator
# ═══════════════════════════════════════════════════════

class EventBus:
    """Pub/sub event system used by the mediator."""

    def __init__(self):
        self._subscribers: dict[str, list[Callable]] = {}

    def subscribe(self, event: str, callback: Callable):
        self._subscribers.setdefault(event, []).append(callback)

    def unsubscribe(self, event: str, callback: Callable):
        if event in self._subscribers:
            self._subscribers[event].remove(callback)

    def publish(self, event: str, data: dict = None):
        for callback in self._subscribers.get(event, []):
            callback(data or {})


# ═══════════════════════════════════════════════════════
#  Mediator: Dashboard coordinator
# ═══════════════════════════════════════════════════════

class DashboardMediator:
    """
    MEDIATOR — coordinates all widgets through an EVENT BUS (Observer).
    Widgets register with the mediator and communicate via events.
    """

    def __init__(self):
        self._event_bus = EventBus()
        self._widgets: dict[str, Widget] = {}
        self._data_store: dict[str, object] = {}

    def register_widget(self, widget: Widget):
        widget.set_mediator(self)
        self._widgets[widget.widget_id] = widget
        widget.on_register()

    def notify(self, sender: Widget, event: str, data: dict = None):
        """Widgets call this to communicate — mediator routes the message."""
        full_data = {"sender": sender.widget_id, **(data or {})}
        print(f"  🔀 Mediator: {sender.widget_id} → '{event}'")
        self._event_bus.publish(event, full_data)

    def subscribe(self, event: str, callback: Callable):
        self._event_bus.subscribe(event, callback)

    def set_data(self, key: str, value: object):
        self._data_store[key] = value
        self._event_bus.publish("data_changed", {"key": key, "value": value})

    def get_data(self, key: str) -> object:
        return self._data_store.get(key)


# ═══════════════════════════════════════════════════════
#  Widget base class (Colleague)
# ═══════════════════════════════════════════════════════

class Widget(ABC):
    def __init__(self, widget_id: str):
        self.widget_id = widget_id
        self._mediator: DashboardMediator | None = None

    def set_mediator(self, mediator: DashboardMediator):
        self._mediator = mediator

    def on_register(self):
        """Called when widget is registered — subscribe to events here."""
        pass

    @abstractmethod
    def render(self) -> str:
        pass


# ═══════════════════════════════════════════════════════
#  Concrete Widgets
# ═══════════════════════════════════════════════════════

class FilterPanel(Widget):
    """A filter panel that broadcasts filter changes."""

    def __init__(self):
        super().__init__("filter_panel")
        self.active_filters: dict[str, str] = {}

    def set_filter(self, key: str, value: str):
        self.active_filters[key] = value
        if self._mediator:
            self._mediator.notify(self, "filter_changed", {
                "filter_key": key,
                "filter_value": value,
                "all_filters": dict(self.active_filters),
            })

    def clear_filters(self):
        self.active_filters.clear()
        if self._mediator:
            self._mediator.notify(self, "filters_cleared", {})

    def render(self) -> str:
        filters = " | ".join(f"{k}={v}" for k, v in self.active_filters.items())
        return f"  🔍 Filters: [{filters or 'None'}]"


class DataTable(Widget):
    """A table that updates when filters or data change."""

    def __init__(self):
        super().__init__("data_table")
        self._data: list[dict] = [
            {"name": "Alice", "dept": "Engineering", "sales": 150_000},
            {"name": "Bob", "dept": "Marketing", "sales": 95_000},
            {"name": "Charlie", "dept": "Engineering", "sales": 180_000},
            {"name": "Dana", "dept": "Sales", "sales": 220_000},
            {"name": "Eve", "dept": "Marketing", "sales": 110_000},
        ]
        self._filtered_data = self._data.copy()

    def on_register(self):
        self._mediator.subscribe("filter_changed", self._on_filter)
        self._mediator.subscribe("filters_cleared", self._on_clear)

    def _on_filter(self, data: dict):
        key = data["filter_key"]
        value = data["filter_value"]
        self._filtered_data = [
            row for row in self._data
            if str(row.get(key, "")).lower() == value.lower()
        ]
        print(f"    📊 Table: Filtered to {len(self._filtered_data)} rows")
        # Notify that visible data changed (for chart to update)
        if self._mediator:
            self._mediator.notify(self, "data_updated", {
                "rows": self._filtered_data,
                "count": len(self._filtered_data),
            })

    def _on_clear(self, data: dict):
        self._filtered_data = self._data.copy()
        print(f"    📊 Table: Showing all {len(self._filtered_data)} rows")
        if self._mediator:
            self._mediator.notify(self, "data_updated", {
                "rows": self._filtered_data,
                "count": len(self._filtered_data),
            })

    def render(self) -> str:
        lines = [f"  📊 Data Table ({len(self._filtered_data)} rows):"]
        lines.append(f"    {'Name':<12} {'Dept':<15} {'Sales':>10}")
        lines.append(f"    {'─'*12} {'─'*15} {'─'*10}")
        for row in self._filtered_data:
            lines.append(f"    {row['name']:<12} {row['dept']:<15} ${row['sales']:>9,}")
        return "\n".join(lines)


class SalesChart(Widget):
    """A chart that reacts to data changes."""

    def __init__(self):
        super().__init__("chart")
        self._chart_data: list[dict] = []

    def on_register(self):
        self._mediator.subscribe("data_updated", self._on_data)

    def _on_data(self, data: dict):
        self._chart_data = data.get("rows", [])
        print(f"    📈 Chart: Updated with {len(self._chart_data)} data points")

    def render(self) -> str:
        if not self._chart_data:
            return "  📈 Chart: No data"
        lines = ["  📈 Sales Chart:"]
        max_sales = max(r["sales"] for r in self._chart_data) if self._chart_data else 1
        for row in self._chart_data:
            bar_len = int(row["sales"] / max_sales * 30)
            bar = "█" * bar_len
            lines.append(f"    {row['name']:<10} {bar} ${row['sales']:,}")
        return "\n".join(lines)


class StatusBar(Widget):
    """Shows summary statistics — reacts to data changes."""

    def __init__(self):
        super().__init__("status_bar")
        self._total = 0
        self._count = 0

    def on_register(self):
        self._mediator.subscribe("data_updated", self._on_data)
        self._mediator.subscribe("filter_changed", self._on_filter)
        self._mediator.subscribe("filters_cleared", self._on_clear)

    def _on_data(self, data: dict):
        rows = data.get("rows", [])
        self._count = len(rows)
        self._total = sum(r.get("sales", 0) for r in rows)

    def _on_filter(self, data: dict):
        print(f"    📊 Status: Filter applied — {data['filter_key']}={data['filter_value']}")

    def _on_clear(self, data: dict):
        print(f"    📊 Status: Filters cleared")

    def render(self) -> str:
        avg = self._total / self._count if self._count else 0
        return (f"  📊 Status: {self._count} records | "
                f"Total: ${self._total:,} | Avg: ${avg:,.0f}")


# ─────────────────────────────────────────────────────
#  Demo
# ─────────────────────────────────────────────────────

def demo():
    print("=" * 60)
    print("  OBSERVER + MEDIATOR COMBINATION DEMO")
    print("  Event-Driven Dashboard")
    print("=" * 60)

    # Setup
    dashboard = DashboardMediator()
    filters = FilterPanel()
    table = DataTable()
    chart = SalesChart()
    status = StatusBar()

    print("\n1. Registering widgets:")
    dashboard.register_widget(filters)
    dashboard.register_widget(table)
    dashboard.register_widget(chart)
    dashboard.register_widget(status)

    # --- Initial render ---
    print("\n2. Initial state:")
    print(filters.render())
    print(table.render())
    print(chart.render())
    print(status.render())

    # --- Apply a filter ---
    print(f"\n{'─' * 50}")
    print("3. Filter by dept=Engineering:")
    filters.set_filter("dept", "Engineering")
    print()
    print(filters.render())
    print(table.render())
    print(chart.render())
    print(status.render())

    # --- Change filter ---
    print(f"\n{'─' * 50}")
    print("4. Filter by dept=Marketing:")
    filters.set_filter("dept", "Marketing")
    print()
    print(table.render())
    print(chart.render())
    print(status.render())

    # --- Clear ---
    print(f"\n{'─' * 50}")
    print("5. Clear all filters:")
    filters.clear_filters()
    print()
    print(table.render())
    print(status.render())

    print("\n💡 HOW THEY COMBINE:")
    print("   MEDIATOR: Widgets never talk to each other directly.")
    print("   OBSERVER: Widgets subscribe to events they care about.")
    print("   FilterPanel → (event) → Mediator → (notify) → Table → (event) → Chart")
    print("   Adding a new widget requires ZERO changes to existing widgets.")


if __name__ == "__main__":
    demo()
