"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  PROTOTYPE — Creational Pattern                                             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  Intent:   Create new objects by copying (cloning) an existing object      ║
║            rather than building from scratch.                               ║
║                                                                             ║
║  Problem:  Creating an object is expensive (requires DB queries, file      ║
║            reads, or complex setup), but you need many similar objects.     ║
║            Or you want to create an object without knowing its exact class. ║
║                                                                             ║
║  Solution: Define a clone() method that creates a copy of the current      ║
║            object. Then modify the copy as needed.                          ║
║                                                                             ║
║  Use When:                                                                  ║
║    • Object creation is more expensive than cloning                        ║
║    • You need copies of objects with slight variations                      ║
║    • You want to avoid subclassing just to configure objects               ║
║    • You need a registry of pre-configured object templates                ║
║                                                                             ║
║  Real-World Analogy:                                                        ║
║    Cell division — instead of building a new cell from raw materials,      ║
║    a cell copies itself and the copy diverges slightly.                     ║
║                                                                             ║
║  Python Bonus:                                                              ║
║    Python's `copy` module provides `copy()` and `deepcopy()` built-in.     ║
║    This makes the Prototype pattern almost trivial to implement!           ║
║                                                                             ║
║  Related Patterns:                                                          ║
║    • Factory Method — alternative creation strategy                        ║
║    • Abstract Factory — can use Prototype to clone product families        ║
║    • Memento — can use similar cloning for saving object state             ║
║                                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
import copy
from dataclasses import dataclass, field


# ═══════════════════════════════════════════════════════
#  The Prototype (using copy module)
# ═══════════════════════════════════════════════════════

@dataclass
class GameEntity:
    """
    A game entity that's expensive to configure from scratch.
    Using Prototype, we clone a template and tweak it.
    """
    name: str
    health: int
    attack: int
    defense: int
    position: list[float] = field(default_factory=lambda: [0.0, 0.0])
    inventory: list[str] = field(default_factory=list)
    abilities: dict[str, int] = field(default_factory=dict)
    _id_counter: int = field(default=0, repr=False, init=False)

    def clone(self, **overrides) -> GameEntity:
        """
        Create a deep copy, then apply any overrides.
        Deep copy is essential — we don't want clones sharing
        the same inventory or position lists!
        """
        cloned = copy.deepcopy(self)
        for key, value in overrides.items():
            setattr(cloned, key, value)
        return cloned

    def __str__(self) -> str:
        return (f"  {self.name} | HP:{self.health} ATK:{self.attack} DEF:{self.defense} | "
                f"Pos:{self.position} | Items:{self.inventory} | Skills:{self.abilities}")


# ═══════════════════════════════════════════════════════
#  Prototype Registry (Template Library)
# ═══════════════════════════════════════════════════════

class EntityRegistry:
    """
    A registry of pre-configured entity templates.
    Clone from the registry instead of configuring from scratch.

    This is the classic "Prototype Manager" from GoF.
    """

    def __init__(self):
        self._templates: dict[str, GameEntity] = {}

    def register(self, key: str, entity: GameEntity):
        """Register a pre-configured template."""
        self._templates[key] = entity

    def create(self, key: str, **overrides) -> GameEntity:
        """Clone a template and apply overrides."""
        template = self._templates.get(key)
        if template is None:
            raise KeyError(f"No template registered for '{key}'. "
                           f"Available: {list(self._templates.keys())}")
        return template.clone(**overrides)

    def available(self) -> list[str]:
        return list(self._templates.keys())


# ═══════════════════════════════════════════════════════
#  Demonstrating shallow vs deep copy
# ═══════════════════════════════════════════════════════

@dataclass
class Config:
    """Shows why deep copy matters."""
    name: str
    settings: dict[str, str] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)


def shallow_vs_deep_demo():
    """Demonstrates the danger of shallow copy with mutable fields."""
    original = Config(
        name="Production",
        settings={"debug": "false", "db": "postgres"},
        tags=["stable", "v2.1"]
    )

    # Shallow copy — shares mutable objects!
    shallow = copy.copy(original)
    shallow.name = "Staging"  # OK: strings are immutable
    shallow.settings["debug"] = "true"  # DANGER: modifies original!
    shallow.tags.append("testing")  # DANGER: modifies original!

    print("  Shallow copy pitfall:")
    print(f"    Original settings: {original.settings}")  # debug is now 'true'!
    print(f"    Original tags:     {original.tags}")  # has 'testing'!

    # Deep copy — fully independent
    original2 = Config(
        name="Production",
        settings={"debug": "false", "db": "postgres"},
        tags=["stable", "v2.1"]
    )
    deep = copy.deepcopy(original2)
    deep.name = "Staging"
    deep.settings["debug"] = "true"
    deep.tags.append("testing")

    print("\n  Deep copy (safe):")
    print(f"    Original settings: {original2.settings}")  # Still 'false'
    print(f"    Original tags:     {original2.tags}")  # No 'testing'


# ─────────────────────────────────────────────────────
#  Demo
# ─────────────────────────────────────────────────────

def demo():
    print("=" * 60)
    print("  PROTOTYPE PATTERN DEMO")
    print("=" * 60)

    # --- Setup registry with templates ---
    registry = EntityRegistry()

    registry.register("warrior", GameEntity(
        name="Warrior",
        health=150,
        attack=25,
        defense=20,
        inventory=["sword", "shield"],
        abilities={"slash": 30, "block": 15}
    ))

    registry.register("mage", GameEntity(
        name="Mage",
        health=80,
        attack=40,
        defense=8,
        inventory=["staff", "mana_potion"],
        abilities={"fireball": 50, "heal": 25, "teleport": 10}
    ))

    registry.register("archer", GameEntity(
        name="Archer",
        health=100,
        attack=35,
        defense=12,
        inventory=["bow", "arrows_x50"],
        abilities={"snipe": 45, "dodge": 20}
    ))

    # --- Clone and customize ---
    print(f"\n1. Available templates: {registry.available()}")

    print("\n2. Clone warriors for a squad:")
    for i in range(3):
        soldier = registry.create(
            "warrior",
            name=f"Soldier-{i+1}",
            position=[float(i * 10), 0.0],
        )
        print(soldier)

    print("\n3. Clone a mage with custom abilities:")
    archmage = registry.create(
        "mage",
        name="Archmage Zara",
        health=120,
        abilities={"fireball": 80, "heal": 50, "teleport": 30, "meteor": 100}
    )
    print(archmage)

    print("\n4. Original template is untouched:")
    original_mage = registry.create("mage")
    print(original_mage)

    # --- Deep vs shallow ---
    print("\n5. Shallow vs Deep Copy:")
    shallow_vs_deep_demo()

    # --- Independence proof ---
    print("\n6. Proving clone independence:")
    a1 = registry.create("archer", name="Scout-Alpha")
    a2 = registry.create("archer", name="Scout-Beta")
    a1.inventory.append("smoke_bomb")
    a1.position = [100.0, 50.0]
    print(f"  Alpha: {a1}")
    print(f"  Beta:  {a2}")
    print(f"  Alpha has smoke_bomb, Beta doesn't — ✅ independent!")

    print("\n💡 KEY INSIGHT:")
    print("   Prototype is about CLONING pre-configured objects.")
    print("   In Python, always use deepcopy() for objects with mutable fields.")
    print("   The Registry pattern pairs perfectly with Prototype for")
    print("   managing a library of templates.")


if __name__ == "__main__":
    demo()
