"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  MEMENTO — Behavioral Pattern                                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  Intent:   Capture and externalize an object's internal state so it        ║
║            can be restored later, without violating encapsulation.          ║
║                                                                             ║
║  Problem:  You need to create snapshots of an object's state (for undo,   ║
║            save/load, checkpoints) but you don't want to expose its        ║
║            private fields to the outside world.                            ║
║                                                                             ║
║  Solution: The object (Originator) creates a Memento containing a          ║
║            snapshot of its state. A Caretaker stores mementos but          ║
║            never peeks inside them.                                        ║
║                                                                             ║
║  Three Roles:                                                               ║
║    • Originator — the object whose state we want to save/restore          ║
║    • Memento — the snapshot (immutable, opaque to outsiders)               ║
║    • Caretaker — stores mementos (doesn't inspect them)                   ║
║                                                                             ║
║  Use When:                                                                  ║
║    • You need undo/redo                                                    ║
║    • You need save/load game state                                         ║
║    • You need checkpoints or rollback (database transactions)              ║
║                                                                             ║
║  Related Patterns:                                                          ║
║    • Command — often paired: Command stores a Memento for undo            ║
║    • Prototype — alternative: clone the entire object for snapshots       ║
║    • Iterator — Caretaker can iterate over memento history                ║
║                                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import copy


# ═══════════════════════════════════════════════════════
#  Memento (the snapshot)
# ═══════════════════════════════════════════════════════

@dataclass(frozen=True)
class GameMemento:
    """
    MEMENTO — an immutable snapshot of the game state.
    
    The Caretaker stores these but NEVER inspects
    the state inside. Only the Originator (GameCharacter)
    knows how to unpack it.
    """
    _state: dict  # Private state — opaque to outsiders
    _timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))
    _label: str = ""

    @property
    def timestamp(self) -> str:
        return self._timestamp

    @property
    def label(self) -> str:
        return self._label

    def summary(self) -> str:
        return f"[{self._timestamp}] {self._label}"


# ═══════════════════════════════════════════════════════
#  Originator (creates and restores from mementos)
# ═══════════════════════════════════════════════════════

class GameCharacter:
    """
    ORIGINATOR — this is the object whose state we snapshot.
    Only IT knows how to save/restore its own state.
    """

    def __init__(self, name: str):
        self.name = name
        self.level = 1
        self.health = 100
        self.mana = 50
        self.position = [0, 0]
        self.inventory: list[str] = ["basic_sword"]
        self.gold = 100
        self.experience = 0

    def save(self, label: str = "") -> GameMemento:
        """Create a memento (snapshot) of the current state."""
        state = {
            "level": self.level,
            "health": self.health,
            "mana": self.mana,
            "position": self.position.copy(),
            "inventory": self.inventory.copy(),
            "gold": self.gold,
            "experience": self.experience,
        }
        return GameMemento(_state=state, _label=label or f"Level {self.level}")

    def restore(self, memento: GameMemento):
        """Restore state from a memento."""
        state = memento._state
        self.level = state["level"]
        self.health = state["health"]
        self.mana = state["mana"]
        self.position = state["position"].copy()
        self.inventory = state["inventory"].copy()
        self.gold = state["gold"]
        self.experience = state["experience"]

    # --- Game actions that change state ---

    def take_damage(self, amount: int):
        self.health = max(0, self.health - amount)

    def level_up(self):
        self.level += 1
        self.health = 100 + self.level * 10
        self.mana = 50 + self.level * 5
        self.experience = 0

    def move_to(self, x: int, y: int):
        self.position = [x, y]

    def pick_up(self, item: str):
        self.inventory.append(item)

    def earn_gold(self, amount: int):
        self.gold += amount
        self.experience += amount // 2

    def status(self) -> str:
        items = ", ".join(self.inventory)
        return (f"  {self.name} (Lv.{self.level}) | "
                f"HP:{self.health} MP:{self.mana} | "
                f"Pos:{self.position} | Gold:{self.gold}\n"
                f"    Items: [{items}]")


# ═══════════════════════════════════════════════════════
#  Caretaker (manages memento history)
# ═══════════════════════════════════════════════════════

class SaveManager:
    """
    CARETAKER — stores mementos but never inspects their content.
    Provides save slots, auto-save, and undo/redo.
    """

    def __init__(self, max_autosaves: int = 10):
        self._save_slots: dict[str, GameMemento] = {}
        self._auto_saves: list[GameMemento] = []
        self._max_autosaves = max_autosaves
        self._undo_stack: list[GameMemento] = []
        self._redo_stack: list[GameMemento] = []

    def save_to_slot(self, character: GameCharacter, slot_name: str):
        """Named save slot."""
        memento = character.save(label=f"Slot: {slot_name}")
        self._save_slots[slot_name] = memento
        print(f"  💾 Saved to slot '{slot_name}': {memento.summary()}")

    def load_from_slot(self, character: GameCharacter, slot_name: str) -> bool:
        memento = self._save_slots.get(slot_name)
        if memento is None:
            print(f"  ❌ No save in slot '{slot_name}'")
            return False
        character.restore(memento)
        print(f"  📂 Loaded from slot '{slot_name}': {memento.summary()}")
        return True

    def auto_save(self, character: GameCharacter):
        """Rolling auto-save with limited history."""
        memento = character.save(label="Auto-save")
        self._auto_saves.append(memento)
        if len(self._auto_saves) > self._max_autosaves:
            self._auto_saves.pop(0)

    def checkpoint(self, character: GameCharacter):
        """Save a checkpoint for undo."""
        memento = character.save(label="Checkpoint")
        self._undo_stack.append(memento)
        self._redo_stack.clear()

    def undo(self, character: GameCharacter) -> bool:
        if not self._undo_stack:
            print("  ❌ Nothing to undo!")
            return False
        # Save current state for redo
        self._redo_stack.append(character.save(label="Redo point"))
        # Restore previous state
        memento = self._undo_stack.pop()
        character.restore(memento)
        print(f"  ↩️  Undo: restored {memento.summary()}")
        return True

    def redo(self, character: GameCharacter) -> bool:
        if not self._redo_stack:
            print("  ❌ Nothing to redo!")
            return False
        self._undo_stack.append(character.save(label="Undo point"))
        memento = self._redo_stack.pop()
        character.restore(memento)
        print(f"  ↪️  Redo: restored {memento.summary()}")
        return True

    def list_saves(self) -> str:
        lines = ["  📋 Save Slots:"]
        for name, memento in self._save_slots.items():
            lines.append(f"    [{name}] {memento.summary()}")
        lines.append(f"  Auto-saves: {len(self._auto_saves)}")
        lines.append(f"  Undo stack: {len(self._undo_stack)}")
        return "\n".join(lines)


# ─────────────────────────────────────────────────────
#  Demo
# ─────────────────────────────────────────────────────

def demo():
    print("=" * 60)
    print("  MEMENTO PATTERN DEMO")
    print("=" * 60)

    player = GameCharacter("Hero")
    saves = SaveManager()

    # --- Initial state ---
    print("\n1. Starting state:")
    print(player.status())

    # --- Play through the game ---
    print("\n2. Playing the game (with checkpoints):")

    saves.checkpoint(player)
    player.move_to(10, 20)
    player.pick_up("health_potion")
    player.earn_gold(50)
    print(f"  After exploring:")
    print(player.status())

    saves.save_to_slot(player, "before_boss")

    saves.checkpoint(player)
    player.move_to(50, 50)
    player.level_up()
    player.pick_up("enchanted_shield")
    player.earn_gold(200)
    print(f"\n  After leveling up:")
    print(player.status())

    saves.checkpoint(player)
    player.take_damage(80)
    player.move_to(60, 55)
    print(f"\n  After taking damage in boss fight:")
    print(player.status())

    # --- Undo ---
    print("\n3. Undo (go back before boss damage):")
    saves.undo(player)
    print(player.status())

    # --- Undo again ---
    print("\n4. Undo again (go back before level-up):")
    saves.undo(player)
    print(player.status())

    # --- Redo ---
    print("\n5. Redo (back to post level-up):")
    saves.redo(player)
    print(player.status())

    # --- Load named slot ---
    print("\n6. Load 'before_boss' slot:")
    saves.load_from_slot(player, "before_boss")
    print(player.status())

    # --- Save listing ---
    print(f"\n7. {saves.list_saves()}")

    print("\n💡 KEY INSIGHT:")
    print("   The Memento stores state WITHOUT exposing internal details.")
    print("   The SaveManager (Caretaker) stores snapshots but can't read them.")
    print("   Only the GameCharacter (Originator) knows how to save/restore.")
    print("   This preserves encapsulation while enabling undo, save/load, etc.")


if __name__ == "__main__":
    demo()
