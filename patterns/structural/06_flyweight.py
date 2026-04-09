"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  FLYWEIGHT — Structural Pattern                                             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  Intent:   Use sharing to support large numbers of fine-grained objects    ║
║            efficiently by sharing common parts of their state.             ║
║                                                                             ║
║  Problem:  You need millions of similar objects (e.g., characters in a     ║
║            text editor, trees in a game forest). Storing full state in     ║
║            each object would exhaust memory.                               ║
║                                                                             ║
║  Solution: Split object state into:                                        ║
║            • Intrinsic (shared) — doesn't change, can be shared           ║
║            • Extrinsic (unique) — varies per context, passed in           ║
║            Store intrinsic state once and share it among many objects.      ║
║                                                                             ║
║  Use When:                                                                  ║
║    • You have a huge number of objects with shared state                   ║
║    • Most object state can be made extrinsic                               ║
║    • Memory is a bottleneck                                                ║
║                                                                             ║
║  Real-World Analogy:                                                        ║
║    A video game forest: instead of storing full tree data                   ║
║    (mesh, texture, color) for each of 10,000 trees, store the              ║
║    template once and only vary position/size per tree.                      ║
║                                                                             ║
║  Related Patterns:                                                          ║
║    • Singleton — flyweight factory is often a singleton                    ║
║    • Composite — flyweights are often leaves in a composite tree           ║
║    • Factory Method — creates and manages flyweight objects                ║
║                                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
import sys
from dataclasses import dataclass


# ═══════════════════════════════════════════════════════
#  The Flyweight (shared intrinsic state)
# ═══════════════════════════════════════════════════════

@dataclass(frozen=True)
class TreeType:
    """
    FLYWEIGHT — stores INTRINSIC state (shared across many trees).

    This object is IMMUTABLE (frozen=True) and shared.
    Many tree instances reference the same TreeType.
    """
    species: str
    color: str
    texture: str  # filename or identifier

    def render(self, x: float, y: float, age: int) -> str:
        """
        Render at a specific position.
        x, y, age are EXTRINSIC state — passed in, not stored here.
        """
        icon = {"Oak": "🌳", "Pine": "🌲", "Palm": "🌴", "Cherry": "🌸"}.get(
            self.species, "🌿"
        )
        return f"{icon} {self.species} at ({x:.0f},{y:.0f}) age={age}"


# ═══════════════════════════════════════════════════════
#  The Flyweight Factory
# ═══════════════════════════════════════════════════════

class TreeFactory:
    """
    Creates and manages shared TreeType flyweights.
    If a TreeType with the same intrinsic state already exists,
    return the existing one instead of creating a new one.
    """
    _cache: dict[tuple, TreeType] = {}

    @classmethod
    def get_tree_type(cls, species: str, color: str, texture: str) -> TreeType:
        key = (species, color, texture)
        if key not in cls._cache:
            cls._cache[key] = TreeType(species, color, texture)
        return cls._cache[key]

    @classmethod
    def type_count(cls) -> int:
        return len(cls._cache)

    @classmethod
    def reset(cls):
        cls._cache.clear()


# ═══════════════════════════════════════════════════════
#  Context (unique extrinsic state)
# ═══════════════════════════════════════════════════════

class Tree:
    """
    A tree in the forest. Stores EXTRINSIC state (position, age)
    and references a shared FLYWEIGHT (TreeType).
    """

    def __init__(self, x: float, y: float, age: int, tree_type: TreeType):
        self.x = x          # Extrinsic
        self.y = y          # Extrinsic
        self.age = age       # Extrinsic
        self._type = tree_type  # Shared flyweight (intrinsic)

    def render(self) -> str:
        return self._type.render(self.x, self.y, self.age)


# ═══════════════════════════════════════════════════════
#  Client Code
# ═══════════════════════════════════════════════════════

class Forest:
    """A forest with potentially thousands of trees."""

    def __init__(self):
        self._trees: list[Tree] = []

    def plant_tree(self, x: float, y: float, age: int,
                   species: str, color: str, texture: str):
        """
        Plant a tree. The factory handles sharing TreeType objects.
        """
        tree_type = TreeFactory.get_tree_type(species, color, texture)
        tree = Tree(x, y, age, tree_type)
        self._trees.append(tree)

    def render(self, max_display: int = 10) -> list[str]:
        """Render the forest (show first N trees)."""
        lines = []
        for tree in self._trees[:max_display]:
            lines.append(f"  {tree.render()}")
        if len(self._trees) > max_display:
            lines.append(f"  ... and {len(self._trees) - max_display} more trees")
        return lines

    @property
    def tree_count(self) -> int:
        return len(self._trees)


# ═══════════════════════════════════════════════════════
#  Another Example: Text Character Flyweight
# ═══════════════════════════════════════════════════════

@dataclass(frozen=True)
class CharStyle:
    """Shared style information for text characters."""
    font: str
    size: int
    bold: bool
    italic: bool


class CharStyleFactory:
    """Flyweight factory for character styles."""
    _cache: dict[tuple, CharStyle] = {}

    @classmethod
    def get_style(cls, font: str, size: int, bold: bool = False,
                  italic: bool = False) -> CharStyle:
        key = (font, size, bold, italic)
        if key not in cls._cache:
            cls._cache[key] = CharStyle(font, size, bold, italic)
        return cls._cache[key]

    @classmethod
    def style_count(cls) -> int:
        return len(cls._cache)


@dataclass
class FormattedChar:
    """A character in a text editor with position and shared style."""
    char: str       # Extrinsic
    row: int        # Extrinsic
    col: int        # Extrinsic
    style: CharStyle  # Shared flyweight


# ─────────────────────────────────────────────────────
#  Demo
# ─────────────────────────────────────────────────────

def demo():
    print("=" * 60)
    print("  FLYWEIGHT PATTERN DEMO")
    print("=" * 60)

    import random
    random.seed(42)
    TreeFactory.reset()

    # --- Plant a large forest ---
    forest = Forest()
    tree_configs = [
        ("Oak", "dark green", "oak_bark.png"),
        ("Pine", "forest green", "pine_bark.png"),
        ("Palm", "tropical green", "palm_bark.png"),
        ("Cherry", "pink", "cherry_bark.png"),
    ]

    NUM_TREES = 10_000
    print(f"\n1. Planting {NUM_TREES:,} trees...")
    for _ in range(NUM_TREES):
        species, color, texture = random.choice(tree_configs)
        x = random.uniform(0, 1000)
        y = random.uniform(0, 1000)
        age = random.randint(1, 100)
        forest.plant_tree(x, y, age, species, color, texture)

    print(f"   Trees planted:      {forest.tree_count:,}")
    print(f"   Unique TreeTypes:   {TreeFactory.type_count()}")

    # --- Memory comparison ---
    print(f"\n2. Memory Savings:")
    # Size of one Tree context (extrinsic)
    sample_tree = forest._trees[0]
    tree_size = sys.getsizeof(sample_tree) + sys.getsizeof(sample_tree.x) + \
                sys.getsizeof(sample_tree.y) + sys.getsizeof(sample_tree.age)
    # Size of one TreeType flyweight (intrinsic)
    type_size = sys.getsizeof(sample_tree._type)

    without_flyweight = NUM_TREES * (tree_size + type_size)
    with_flyweight = NUM_TREES * tree_size + TreeFactory.type_count() * type_size
    savings = without_flyweight - with_flyweight

    print(f"   Without Flyweight: ~{without_flyweight:>10,} bytes")
    print(f"   With Flyweight:    ~{with_flyweight:>10,} bytes")
    print(f"   Savings:           ~{savings:>10,} bytes ({100*savings/without_flyweight:.1f}%)")

    # --- Rendering ---
    print(f"\n3. Sample trees:")
    for line in forest.render(8):
        print(f"   {line}")

    # --- Prove sharing works ---
    print(f"\n4. Proving flyweight sharing:")
    t1 = TreeFactory.get_tree_type("Oak", "dark green", "oak_bark.png")
    t2 = TreeFactory.get_tree_type("Oak", "dark green", "oak_bark.png")
    print(f"   Same request → same object? {t1 is t2}")
    print(f"   id(t1) == id(t2): {id(t1) == id(t2)}")

    # --- Text editor example ---
    print(f"\n5. Text Editor (character styles):")
    body_style = CharStyleFactory.get_style("Arial", 12)
    heading_style = CharStyleFactory.get_style("Arial", 24, bold=True)

    text = "Hello World"
    chars = []
    for i, ch in enumerate(text):
        style = heading_style if i == 0 else body_style
        chars.append(FormattedChar(ch, row=0, col=i, style=style))

    print(f"   Characters: {len(chars)}")
    print(f"   Unique styles: {CharStyleFactory.style_count()}")
    print(f"   All 'body' chars share style? "
          f"{all(c.style is body_style for c in chars[1:])}")

    print("\n💡 KEY INSIGHT:")
    print("   Flyweight splits state into INTRINSIC (shared) and EXTRINSIC")
    print("   (unique). 10,000 trees but only 4 TreeType objects in memory.")
    print("   The factory ensures flyweights are reused, not duplicated.")


if __name__ == "__main__":
    demo()
