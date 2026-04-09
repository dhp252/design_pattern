"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  COMBINATION: Command + Memento                                             ║
║  Real-World App: Text Editor with Undo/Redo                                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  How they combine:                                                          ║
║    • Command encapsulates each editing operation                            ║
║    • Memento stores the document state BEFORE each command executes        ║
║    • Together they enable full undo/redo with state snapshots              ║
║                                                                             ║
║  Why together:                                                              ║
║    Command alone can undo simple operations, but complex ones              ║
║    (like a regex find-replace) are hard to reverse algorithmically.         ║
║    Mementos capture the EXACT state, making any operation undoable.        ║
║                                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
import copy


# ═══════════════════════════════════════════════════════
#  The Document (Originator for Memento)
# ═══════════════════════════════════════════════════════

@dataclass(frozen=True)
class DocumentMemento:
    """Immutable snapshot of the document state."""
    content: str
    cursor_pos: int
    selection: tuple[int, int] | None
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))


class TextDocument:
    """The document — creates and restores from mementos."""

    def __init__(self, content: str = ""):
        self.content = content
        self.cursor_pos = len(content)
        self.selection: tuple[int, int] | None = None

    def save_state(self) -> DocumentMemento:
        return DocumentMemento(
            content=self.content,
            cursor_pos=self.cursor_pos,
            selection=self.selection,
        )

    def restore_state(self, memento: DocumentMemento):
        self.content = memento.content
        self.cursor_pos = memento.cursor_pos
        self.selection = memento.selection

    def display(self) -> str:
        # Show content with cursor position
        before = self.content[:self.cursor_pos]
        after = self.content[self.cursor_pos:]
        indicator = f"  ({len(self.content)} chars, cursor at {self.cursor_pos})"
        return f'  "{before}▌{after}"{indicator}'


# ═══════════════════════════════════════════════════════
#  Command Interface
# ═══════════════════════════════════════════════════════

class EditorCommand(ABC):
    """Each command saves a memento before executing."""

    def __init__(self, document: TextDocument):
        self._document = document
        self._memento: DocumentMemento | None = None

    def execute(self) -> str:
        # MEMENTO: save state before modifying
        self._memento = self._document.save_state()
        return self._do_execute()

    def undo(self) -> str:
        if self._memento:
            self._document.restore_state(self._memento)
            return f"↩️  Undone: {self.description()}"
        return "Nothing to undo"

    @abstractmethod
    def _do_execute(self) -> str:
        pass

    @abstractmethod
    def description(self) -> str:
        pass


# ═══════════════════════════════════════════════════════
#  Concrete Commands
# ═══════════════════════════════════════════════════════

class InsertTextCommand(EditorCommand):
    def __init__(self, document: TextDocument, text: str, position: int | None = None):
        super().__init__(document)
        self._text = text
        self._position = position

    def _do_execute(self) -> str:
        pos = self._position if self._position is not None else self._document.cursor_pos
        doc = self._document
        doc.content = doc.content[:pos] + self._text + doc.content[pos:]
        doc.cursor_pos = pos + len(self._text)
        return f"✏️  Inserted '{self._text}' at position {pos}"

    def description(self) -> str:
        return f"Insert '{self._text[:20]}{'...' if len(self._text) > 20 else ''}'"


class DeleteTextCommand(EditorCommand):
    def __init__(self, document: TextDocument, start: int, end: int):
        super().__init__(document)
        self._start = start
        self._end = end

    def _do_execute(self) -> str:
        doc = self._document
        deleted = doc.content[self._start:self._end]
        doc.content = doc.content[:self._start] + doc.content[self._end:]
        doc.cursor_pos = self._start
        return f"🗑️  Deleted '{deleted}' [{self._start}:{self._end}]"

    def description(self) -> str:
        return f"Delete [{self._start}:{self._end}]"


class ReplaceAllCommand(EditorCommand):
    """Complex operation — hard to undo without Memento!"""

    def __init__(self, document: TextDocument, find: str, replace: str):
        super().__init__(document)
        self._find = find
        self._replace = replace
        self._count = 0

    def _do_execute(self) -> str:
        doc = self._document
        self._count = doc.content.count(self._find)
        doc.content = doc.content.replace(self._find, self._replace)
        return f"🔄 Replaced {self._count} occurrences of '{self._find}' → '{self._replace}'"

    def description(self) -> str:
        return f"Replace all '{self._find}' → '{self._replace}' ({self._count}x)"


class FormatUppercaseCommand(EditorCommand):
    """Convert selection or all text to uppercase."""

    def __init__(self, document: TextDocument, start: int | None = None, end: int | None = None):
        super().__init__(document)
        self._start = start or 0
        self._end = end or len(document.content)

    def _do_execute(self) -> str:
        doc = self._document
        target = doc.content[self._start:self._end]
        doc.content = doc.content[:self._start] + target.upper() + doc.content[self._end:]
        return f"🔠 Uppercased [{self._start}:{self._end}]"

    def description(self) -> str:
        return f"Uppercase [{self._start}:{self._end}]"


# ═══════════════════════════════════════════════════════
#  Editor (Invoker + Caretaker)
# ═══════════════════════════════════════════════════════

class TextEditor:
    """
    Combines the Invoker (Command) and Caretaker (Memento) roles.
    Maintains command history for undo/redo.
    """

    def __init__(self, initial_content: str = ""):
        self.document = TextDocument(initial_content)
        self._undo_stack: list[EditorCommand] = []
        self._redo_stack: list[EditorCommand] = []
        self._history: list[str] = []

    def execute(self, command: EditorCommand) -> str:
        result = command.execute()
        self._undo_stack.append(command)
        self._redo_stack.clear()
        self._history.append(command.description())
        return result

    def undo(self) -> str:
        if not self._undo_stack:
            return "Nothing to undo!"
        cmd = self._undo_stack.pop()
        result = cmd.undo()
        self._redo_stack.append(cmd)
        return result

    def redo(self) -> str:
        if not self._redo_stack:
            return "Nothing to redo!"
        cmd = self._redo_stack.pop()
        result = cmd.execute()  # Re-execute saves a new memento
        self._undo_stack.append(cmd)
        return result

    # --- Convenience methods ---

    def insert(self, text: str, position: int | None = None) -> str:
        return self.execute(InsertTextCommand(self.document, text, position))

    def delete(self, start: int, end: int) -> str:
        return self.execute(DeleteTextCommand(self.document, start, end))

    def replace_all(self, find: str, replace: str) -> str:
        return self.execute(ReplaceAllCommand(self.document, find, replace))

    def uppercase(self, start: int = None, end: int = None) -> str:
        return self.execute(FormatUppercaseCommand(self.document, start, end))

    def show(self) -> str:
        return self.document.display()

    def show_history(self) -> str:
        lines = ["  📋 Edit History:"]
        for i, desc in enumerate(self._history, 1):
            lines.append(f"    {i}. {desc}")
        lines.append(f"  Undo available: {len(self._undo_stack)}")
        lines.append(f"  Redo available: {len(self._redo_stack)}")
        return "\n".join(lines)


# ─────────────────────────────────────────────────────
#  Demo
# ─────────────────────────────────────────────────────

def demo():
    print("=" * 60)
    print("  COMMAND + MEMENTO COMBINATION DEMO")
    print("  Text Editor with Undo/Redo")
    print("=" * 60)

    editor = TextEditor()

    # --- Build up some text ---
    print("\n1. Writing text:")
    print(f"  {editor.insert('Hello World! ')}")
    print(f"  {editor.show()}")

    print(f"  {editor.insert('Design patterns are powerful. ')}")
    print(f"  {editor.show()}")

    print(f"  {editor.insert('Python makes them elegant. ')}")
    print(f"  {editor.show()}")

    # --- Complex operation: replace all ---
    print("\n2. Replace all (complex operation):")
    print(f"  {editor.replace_all('patterns', 'PATTERNS')}")
    print(f"  {editor.show()}")

    # --- Uppercase a range ---
    print(f"\n  {editor.uppercase(0, 5)}")
    print(f"  {editor.show()}")

    # --- Undo chain ---
    print("\n3. Undo chain:")
    print(f"  {editor.undo()}")  # Undo uppercase
    print(f"  {editor.show()}")

    print(f"  {editor.undo()}")  # Undo replace-all (restores from Memento!)
    print(f"  {editor.show()}")

    print(f"  {editor.undo()}")  # Undo last insert
    print(f"  {editor.show()}")

    # --- Redo ---
    print("\n4. Redo:")
    print(f"  {editor.redo()}")  # Redo insert
    print(f"  {editor.show()}")

    print(f"  {editor.redo()}")  # Redo replace-all
    print(f"  {editor.show()}")

    # --- Delete and undo ---
    print("\n5. Delete and undo:")
    print(f"  {editor.delete(0, 6)}")
    print(f"  {editor.show()}")

    print(f"  {editor.undo()}")
    print(f"  {editor.show()}")

    # --- History ---
    print(f"\n6. {editor.show_history()}")

    print("\n💡 HOW THEY COMBINE:")
    print("   COMMAND encapsulates 'what to do' as an object")
    print("   MEMENTO captures 'how things were' before the command")
    print("   Together: any operation can be undone by restoring the memento")
    print("   Even complex ops like replace-all are trivially undoable!")


if __name__ == "__main__":
    demo()
