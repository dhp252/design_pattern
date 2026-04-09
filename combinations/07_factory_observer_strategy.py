"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  COMBINATION: Factory + Observer + Strategy (3 patterns!)                   ║
║  Real-World App: Plugin System                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  How they combine:                                                          ║
║    • Factory creates plugin instances from registered plugin classes        ║
║    • Observer handles plugin lifecycle events (loaded, activated, error)    ║
║    • Strategy defines the plugin's behavior interface                      ║
║                                                                             ║
║  This is how real plugin systems work (VS Code, Webpack, pytest, etc.)    ║
║                                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable


# ═══════════════════════════════════════════════════════
#  Strategy: Plugin behavior interface
# ═══════════════════════════════════════════════════════

class Plugin(ABC):
    """Strategy — every plugin implements the same interface."""

    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def version(self) -> str:
        pass

    @abstractmethod
    def execute(self, data: dict) -> dict:
        """Process data according to this plugin's strategy."""
        pass

    def on_activate(self):
        """Lifecycle hook — called when plugin is activated."""
        pass

    def on_deactivate(self):
        """Lifecycle hook — called when plugin is deactivated."""
        pass


# ═══════════════════════════════════════════════════════
#  Concrete Plugins (Strategies)
# ═══════════════════════════════════════════════════════

class MarkdownPlugin(Plugin):
    def name(self) -> str:
        return "markdown-renderer"

    def version(self) -> str:
        return "2.1.0"

    def execute(self, data: dict) -> dict:
        text = data.get("text", "")
        # Simple markdown → HTML conversion
        lines = []
        for line in text.split("\n"):
            if line.startswith("# "):
                lines.append(f"<h1>{line[2:]}</h1>")
            elif line.startswith("## "):
                lines.append(f"<h2>{line[3:]}</h2>")
            elif line.startswith("**") and line.endswith("**"):
                lines.append(f"<strong>{line[2:-2]}</strong>")
            else:
                lines.append(f"<p>{line}</p>")
        return {"html": "\n".join(lines), "plugin": self.name()}


class SyntaxHighlightPlugin(Plugin):
    def name(self) -> str:
        return "syntax-highlight"

    def version(self) -> str:
        return "1.3.0"

    def execute(self, data: dict) -> dict:
        code = data.get("code", "")
        language = data.get("language", "python")
        # Simulate syntax highlighting
        keywords = {"def", "class", "return", "import", "from", "if", "else", "for", "while"}
        highlighted = code
        for kw in keywords:
            highlighted = highlighted.replace(kw, f"[KEYWORD:{kw}]")
        return {"highlighted": highlighted, "language": language, "plugin": self.name()}


class SpellCheckPlugin(Plugin):
    def name(self) -> str:
        return "spell-checker"

    def version(self) -> str:
        return "3.0.1"

    DICTIONARY = {"hello", "world", "the", "is", "a", "design", "pattern", "python",
                   "this", "test", "plugin", "system", "building"}

    def execute(self, data: dict) -> dict:
        text = data.get("text", "")
        words = text.lower().split()
        misspelled = [w for w in words if w.strip(".,!?") not in self.DICTIONARY and w.isalpha()]
        return {"misspelled": misspelled, "total_words": len(words), "plugin": self.name()}

    def on_activate(self):
        print(f"    📖 {self.name()}: Loading dictionary ({len(self.DICTIONARY)} words)")


class AnalyticsPlugin(Plugin):
    def name(self) -> str:
        return "analytics"

    def version(self) -> str:
        return "1.0.0"

    def __init__(self):
        self.total_calls = 0

    def execute(self, data: dict) -> dict:
        self.total_calls += 1
        text = data.get("text", data.get("code", ""))
        return {
            "char_count": len(text),
            "word_count": len(text.split()),
            "line_count": text.count("\n") + 1,
            "call_number": self.total_calls,
            "plugin": self.name(),
        }


# ═══════════════════════════════════════════════════════
#  Observer: Plugin lifecycle events
# ═══════════════════════════════════════════════════════

class PluginEventBus:
    """Observer — emits plugin lifecycle events."""

    def __init__(self):
        self._listeners: dict[str, list[Callable]] = {}

    def on(self, event: str, callback: Callable):
        self._listeners.setdefault(event, []).append(callback)

    def emit(self, event: str, **kwargs):
        for cb in self._listeners.get(event, []):
            cb(**kwargs)


# ═══════════════════════════════════════════════════════
#  Factory + Registry: Plugin management
# ═══════════════════════════════════════════════════════

class PluginManager:
    """
    Combines all three patterns:
      • Factory — creates and manages plugin instances
      • Observer — emits lifecycle events
      • Strategy — plugins are interchangeable via common interface
    """

    def __init__(self):
        self._registry: dict[str, type[Plugin]] = {}
        self._active: dict[str, Plugin] = {}
        self.events = PluginEventBus()

    # --- Factory: Registration and creation ---

    def register(self, plugin_cls: type[Plugin]):
        """Register a plugin class (Factory registration)."""
        temp = plugin_cls()
        name = temp.name()
        self._registry[name] = plugin_cls
        self.events.emit("plugin_registered", name=name, version=temp.version())
        print(f"  📦 Registered: {name} v{temp.version()}")

    def activate(self, name: str) -> bool:
        """Create and activate a plugin (Factory creation)."""
        if name in self._active:
            print(f"  ⚠️  {name} is already active")
            return False

        cls = self._registry.get(name)
        if cls is None:
            self.events.emit("plugin_error", name=name, error="Not found in registry")
            return False

        # Factory creates the instance
        plugin = cls()
        plugin.on_activate()
        self._active[name] = plugin
        self.events.emit("plugin_activated", name=name, version=plugin.version())
        print(f"  ✅ Activated: {name}")
        return True

    def deactivate(self, name: str):
        plugin = self._active.pop(name, None)
        if plugin:
            plugin.on_deactivate()
            self.events.emit("plugin_deactivated", name=name)
            print(f"  ⛔ Deactivated: {name}")

    # --- Strategy: Execute through plugin interface ---

    def run(self, plugin_name: str, data: dict) -> dict | None:
        """Execute a plugin's strategy."""
        plugin = self._active.get(plugin_name)
        if plugin is None:
            self.events.emit("plugin_error", name=plugin_name, error="Not active")
            return None

        try:
            result = plugin.execute(data)
            self.events.emit("plugin_executed", name=plugin_name, result=result)
            return result
        except Exception as e:
            self.events.emit("plugin_error", name=plugin_name, error=str(e))
            return None

    def run_all(self, data: dict) -> dict[str, dict]:
        """Run ALL active plugins on the same data (pipeline)."""
        results = {}
        for name in self._active:
            result = self.run(name, data)
            if result:
                results[name] = result
        return results

    # --- Info ---

    @property
    def registered(self) -> list[str]:
        return list(self._registry.keys())

    @property
    def active(self) -> list[str]:
        return list(self._active.keys())


# ─────────────────────────────────────────────────────
#  Demo
# ─────────────────────────────────────────────────────

def demo():
    print("=" * 60)
    print("  FACTORY + OBSERVER + STRATEGY DEMO")
    print("  Plugin System")
    print("=" * 60)

    manager = PluginManager()

    # --- Observer: Listen to lifecycle events ---
    manager.events.on("plugin_activated",
                       lambda name, version: print(f"    🔔 Event: {name} v{version} activated"))
    manager.events.on("plugin_executed",
                       lambda name, result: print(f"    🔔 Event: {name} executed successfully"))
    manager.events.on("plugin_error",
                       lambda name, error: print(f"    🚨 Event: {name} error: {error}"))

    # --- Factory: Register plugins ---
    print("\n1. Register plugins:")
    manager.register(MarkdownPlugin)
    manager.register(SyntaxHighlightPlugin)
    manager.register(SpellCheckPlugin)
    manager.register(AnalyticsPlugin)

    # --- Activate ---
    print(f"\n2. Activate plugins:")
    print(f"  Available: {manager.registered}")
    manager.activate("markdown-renderer")
    manager.activate("spell-checker")
    manager.activate("analytics")

    # --- Strategy: Execute plugins ---
    print(f"\n3. Run plugins on data:")
    test_data = {"text": "# Hello World\nThis is a tset of the plugin system.\n**Building patterns!**"}

    results = manager.run_all(test_data)
    for name, result in results.items():
        print(f"\n  Plugin: {name}")
        for k, v in result.items():
            if k != "plugin":
                print(f"    {k}: {v}")

    # --- Activate more, run specific ---
    print(f"\n4. Activate syntax-highlight and run specifically:")
    manager.activate("syntax-highlight")
    code_data = {"code": "def hello():\n    return 'world'", "language": "python"}
    result = manager.run("syntax-highlight", code_data)
    print(f"  Result: {result}")

    # --- Try running inactive plugin ---
    print(f"\n5. Try running non-active plugin:")
    manager.run("nonexistent-plugin", {})

    # --- Deactivate ---
    print(f"\n6. Deactivate spell-checker:")
    manager.deactivate("spell-checker")
    print(f"  Active plugins: {manager.active}")

    print("\n💡 HOW THREE PATTERNS COMBINE:")
    print("   FACTORY: register() and activate() create plugin instances")
    print("   OBSERVER: events bus notifies listeners of lifecycle changes")
    print("   STRATEGY: run() executes the plugin's algorithm transparently")
    print("   Result: a flexible, extensible plugin system!")


if __name__ == "__main__":
    demo()
