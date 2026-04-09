"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  COMBINATION: MVC — Observer + Strategy + Composite                         ║
║  Real-World App: Todo Application                                           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  MVC is an ARCHITECTURAL pattern that combines multiple GoF patterns:      ║
║    • Model — uses OBSERVER to notify views of data changes                 ║
║    • View — uses COMPOSITE to build the UI tree                           ║
║    • Controller — uses STRATEGY for input handling logic                   ║
║                                                                             ║
║  This is the "grand unification" — showing how patterns form an            ║
║  architecture together.                                                     ║
║                                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable
from enum import Enum, auto


# ═══════════════════════════════════════════════════════
#  MODEL (with Observer for change notifications)
# ═══════════════════════════════════════════════════════

@dataclass
class Todo:
    id: int
    title: str
    completed: bool = False
    priority: str = "medium"
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))


class TodoModel:
    """
    MODEL — manages todo data and notifies observers on changes.
    Uses the OBSERVER pattern internally.
    """

    def __init__(self):
        self._todos: dict[int, Todo] = {}
        self._next_id = 1
        self._observers: list[Callable] = []

    # --- Observer methods ---

    def subscribe(self, callback: Callable):
        self._observers.append(callback)

    def _notify(self, event: str, data: dict = None):
        for observer in self._observers:
            observer(event, data or {})

    # --- CRUD operations ---

    def add(self, title: str, priority: str = "medium") -> Todo:
        todo = Todo(id=self._next_id, title=title, priority=priority)
        self._todos[self._next_id] = todo
        self._next_id += 1
        self._notify("todo_added", {"todo": todo})
        return todo

    def toggle(self, todo_id: int) -> Todo | None:
        todo = self._todos.get(todo_id)
        if todo:
            todo.completed = not todo.completed
            self._notify("todo_toggled", {"todo": todo})
        return todo

    def delete(self, todo_id: int) -> bool:
        todo = self._todos.pop(todo_id, None)
        if todo:
            self._notify("todo_deleted", {"todo": todo})
            return True
        return False

    def edit(self, todo_id: int, title: str) -> Todo | None:
        todo = self._todos.get(todo_id)
        if todo:
            todo.title = title
            self._notify("todo_edited", {"todo": todo})
        return todo

    def get_all(self) -> list[Todo]:
        return list(self._todos.values())

    def get_active(self) -> list[Todo]:
        return [t for t in self._todos.values() if not t.completed]

    def get_completed(self) -> list[Todo]:
        return [t for t in self._todos.values() if t.completed]

    @property
    def stats(self) -> dict:
        all_todos = self.get_all()
        return {
            "total": len(all_todos),
            "active": sum(1 for t in all_todos if not t.completed),
            "completed": sum(1 for t in all_todos if t.completed),
        }


# ═══════════════════════════════════════════════════════
#  VIEW (with Composite for UI structure)
# ═══════════════════════════════════════════════════════

class UIComponent(ABC):
    """Composite interface for UI components."""

    @abstractmethod
    def render(self) -> str:
        pass


class TextComponent(UIComponent):
    def __init__(self, text: str):
        self.text = text

    def render(self) -> str:
        return self.text


class ContainerComponent(UIComponent):
    """Composite — contains other components."""

    def __init__(self, border: str = "", header: str = ""):
        self._children: list[UIComponent] = []
        self._border = border
        self._header = header

    def add(self, child: UIComponent) -> ContainerComponent:
        self._children.append(child)
        return self

    def render(self) -> str:
        lines = []
        if self._header:
            lines.append(f"  {self._border} {self._header} {self._border}")
        for child in self._children:
            lines.append(f"  {child.render()}")
        return "\n".join(lines)


class TodoView:
    """
    VIEW — builds the UI using COMPOSITE components.
    Reacts to model changes via OBSERVER.
    """

    def __init__(self, model: TodoModel):
        self._model = model
        self._filter = "all"  # all, active, completed
        # Subscribe to model changes (Observer)
        model.subscribe(self._on_model_change)

    def _on_model_change(self, event: str, data: dict):
        """Observer callback — re-render when model changes."""
        todo = data.get("todo")
        if todo:
            action = event.replace("todo_", "").title()
            print(f"  🔔 View: {action} — #{todo.id} '{todo.title}'")

    def set_filter(self, filter_name: str):
        self._filter = filter_name

    def render(self) -> str:
        """Build the UI tree using Composite and render it."""
        # Select todos based on filter
        if self._filter == "active":
            todos = self._model.get_active()
        elif self._filter == "completed":
            todos = self._model.get_completed()
        else:
            todos = self._model.get_all()

        stats = self._model.stats

        # Build the Composite UI tree
        root = ContainerComponent(border="═" * 20, header="📋 TODO APP")

        # Stats bar
        root.add(TextComponent(
            f"  Total: {stats['total']} | Active: {stats['active']} | Done: {stats['completed']}"
        ))
        root.add(TextComponent(f"  Filter: [{self._filter.upper()}]"))
        root.add(TextComponent(f"  {'─' * 40}"))

        # Todo list
        if not todos:
            root.add(TextComponent("  (no items)"))
        else:
            for todo in todos:
                checkbox = "✅" if todo.completed else "⬜"
                priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(todo.priority, "⚪")
                strike = f"~~{todo.title}~~" if todo.completed else todo.title
                root.add(TextComponent(
                    f"  {checkbox} #{todo.id} {priority_icon} {strike} [{todo.created_at}]"
                ))

        root.add(TextComponent(f"  {'═' * 42}"))
        return root.render()


# ═══════════════════════════════════════════════════════
#  CONTROLLER (with Strategy for input handling)
# ═══════════════════════════════════════════════════════

class InputStrategy(ABC):
    """Strategy — defines how to handle a specific command."""

    @abstractmethod
    def can_handle(self, command: str) -> bool:
        pass

    @abstractmethod
    def execute(self, model: TodoModel, view: TodoView, args: list[str]) -> str:
        pass


class AddStrategy(InputStrategy):
    def can_handle(self, command: str) -> bool:
        return command == "add"

    def execute(self, model: TodoModel, view: TodoView, args: list[str]) -> str:
        if not args:
            return "Usage: add <title> [priority:high|medium|low]"
        priority = "medium"
        title_parts = []
        for arg in args:
            if arg.startswith("priority:"):
                priority = arg.split(":")[1]
            else:
                title_parts.append(arg)
        title = " ".join(title_parts)
        todo = model.add(title, priority)
        return f"Added todo #{todo.id}: '{todo.title}' [{todo.priority}]"


class ToggleStrategy(InputStrategy):
    def can_handle(self, command: str) -> bool:
        return command == "toggle"

    def execute(self, model: TodoModel, view: TodoView, args: list[str]) -> str:
        if not args:
            return "Usage: toggle <id>"
        todo = model.toggle(int(args[0]))
        if todo:
            status = "completed" if todo.completed else "active"
            return f"Toggled #{todo.id} → {status}"
        return f"Todo #{args[0]} not found"


class DeleteStrategy(InputStrategy):
    def can_handle(self, command: str) -> bool:
        return command == "delete"

    def execute(self, model: TodoModel, view: TodoView, args: list[str]) -> str:
        if not args:
            return "Usage: delete <id>"
        if model.delete(int(args[0])):
            return f"Deleted #{args[0]}"
        return f"Todo #{args[0]} not found"


class FilterStrategy(InputStrategy):
    def can_handle(self, command: str) -> bool:
        return command == "filter"

    def execute(self, model: TodoModel, view: TodoView, args: list[str]) -> str:
        if not args or args[0] not in ("all", "active", "completed"):
            return "Usage: filter <all|active|completed>"
        view.set_filter(args[0])
        return f"Filter set to: {args[0]}"


class TodoController:
    """
    CONTROLLER — routes user input to the right Strategy.
    Uses Chain of Strategy pattern for command dispatch.
    """

    def __init__(self, model: TodoModel, view: TodoView):
        self._model = model
        self._view = view
        self._strategies: list[InputStrategy] = [
            AddStrategy(),
            ToggleStrategy(),
            DeleteStrategy(),
            FilterStrategy(),
        ]

    def handle(self, raw_input: str) -> str:
        parts = raw_input.strip().split()
        if not parts:
            return "Empty command"

        command = parts[0].lower()
        args = parts[1:]

        for strategy in self._strategies:
            if strategy.can_handle(command):
                return strategy.execute(self._model, self._view, args)

        return f"Unknown command: '{command}'. Available: add, toggle, delete, filter"


# ═══════════════════════════════════════════════════════
#  MVC Application
# ═══════════════════════════════════════════════════════

class TodoApp:
    """The full MVC application."""

    def __init__(self):
        self.model = TodoModel()
        self.view = TodoView(self.model)
        self.controller = TodoController(self.model, self.view)

    def run_command(self, command: str) -> str:
        return self.controller.handle(command)

    def display(self) -> str:
        return self.view.render()


# ─────────────────────────────────────────────────────
#  Demo
# ─────────────────────────────────────────────────────

def demo():
    print("=" * 60)
    print("  MVC COMBINATION DEMO (Observer + Strategy + Composite)")
    print("  Todo Application")
    print("=" * 60)

    app = TodoApp()

    # --- Add todos ---
    print("\n1. Adding todos:")
    commands = [
        "add Learn design patterns priority:high",
        "add Build a project priority:medium",
        "add Write documentation priority:low",
        "add Review pull requests priority:high",
        "add Deploy to production priority:medium",
    ]
    for cmd in commands:
        result = app.run_command(cmd)
        print(f"  → {result}")

    # --- Display ---
    print(f"\n2. Current view [ALL]:")
    print(app.display())

    # --- Toggle some ---
    print("3. Complete some todos:")
    print(f"  → {app.run_command('toggle 1')}")
    print(f"  → {app.run_command('toggle 3')}")

    print(f"\n{app.display()}")

    # --- Filter ---
    print("4. Filter active only:")
    app.run_command("filter active")
    print(app.display())

    print("5. Filter completed only:")
    app.run_command("filter completed")
    print(app.display())

    # --- Delete ---
    print("6. Delete todo #3:")
    print(f"  → {app.run_command('delete 3')}")
    app.run_command("filter all")
    print(app.display())

    print("💡 MVC PATTERN MAP:")
    print("  ┌─────────────────────────────────────────────┐")
    print("  │  MODEL (TodoModel)                          │")
    print("  │    └── OBSERVER: notifies view on changes   │")
    print("  │                                              │")
    print("  │  VIEW (TodoView)                             │")
    print("  │    └── COMPOSITE: builds UI component tree   │")
    print("  │    └── OBSERVER: subscribes to model events  │")
    print("  │                                              │")
    print("  │  CONTROLLER (TodoController)                 │")
    print("  │    └── STRATEGY: routes to command handlers  │")
    print("  └─────────────────────────────────────────────┘")


if __name__ == "__main__":
    demo()
