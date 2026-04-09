"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  COMPOSITE — Structural Pattern                                             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  Intent:   Compose objects into tree structures to represent part-whole     ║
║            hierarchies. Let clients treat individual objects and            ║
║            compositions uniformly.                                          ║
║                                                                             ║
║  Problem:  You have a tree structure (folders with files, menus with       ║
║            sub-menus, organizations with departments). You want to          ║
║            call the same operation on a single item or a group of items.   ║
║                                                                             ║
║  Solution: Define a common interface for both leaf nodes (files) and       ║
║            composite nodes (folders). Composites delegate to children.      ║
║                                                                             ║
║  Use When:                                                                  ║
║    • You have a tree/hierarchy structure (files, UI, organizations)        ║
║    • You want to treat leaves and containers uniformly                     ║
║    • You need recursive operations over a tree                             ║
║                                                                             ║
║  Real-World Analogy:                                                        ║
║    Military: a general gives an order to a division, which passes          ║
║    it to brigades → battalions → companies → soldiers. Same interface     ║
║    (execute order) at every level.                                          ║
║                                                                             ║
║  Related Patterns:                                                          ║
║    • Iterator — traverse composite trees                                   ║
║    • Visitor — add operations to composite elements                        ║
║    • Builder — construct composite trees step by step                      ║
║    • Decorator — similar recursive structure but different intent           ║
║                                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from abc import ABC, abstractmethod


# ═══════════════════════════════════════════════════════
#  Component Interface
# ═══════════════════════════════════════════════════════

class FileSystemItem(ABC):
    """
    The Component interface — both files (leaves) and
    directories (composites) implement this.
    """

    def __init__(self, name: str):
        self.name = name
        self.parent: FileSystemItem | None = None

    @abstractmethod
    def get_size(self) -> int:
        """Return size in bytes."""
        pass

    @abstractmethod
    def display(self, indent: int = 0) -> str:
        """Pretty-print the item with indentation."""
        pass

    @abstractmethod
    def search(self, query: str) -> list[FileSystemItem]:
        """Search for items matching the query."""
        pass

    def get_path(self) -> str:
        """Build the full path by traversing up the tree."""
        parts = []
        current: FileSystemItem | None = self
        while current is not None:
            parts.append(current.name)
            current = current.parent
        return "/".join(reversed(parts))


# ═══════════════════════════════════════════════════════
#  Leaf
# ═══════════════════════════════════════════════════════

class File(FileSystemItem):
    """A leaf node — has no children."""

    def __init__(self, name: str, size: int, file_type: str = "text"):
        super().__init__(name)
        self.size = size
        self.file_type = file_type

    def get_size(self) -> int:
        return self.size

    def display(self, indent: int = 0) -> str:
        icon = {"text": "📄", "image": "🖼️ ", "code": "💻", "data": "📊"}.get(
            self.file_type, "📄"
        )
        return f"{'  ' * indent}{icon} {self.name} ({self._format_size()})"

    def search(self, query: str) -> list[FileSystemItem]:
        if query.lower() in self.name.lower():
            return [self]
        return []

    def _format_size(self) -> str:
        for unit in ["B", "KB", "MB", "GB"]:
            if self.size < 1024:
                return f"{self.size}{unit}"
            self.size //= 1024
        return f"{self.size}TB"


# ═══════════════════════════════════════════════════════
#  Composite
# ═══════════════════════════════════════════════════════

class Directory(FileSystemItem):
    """
    A composite node — can contain files and/or other directories.

    The key insight: Directory.get_size() sums up children's sizes
    WITHOUT knowing whether each child is a File or another Directory.
    """

    def __init__(self, name: str):
        super().__init__(name)
        self._children: list[FileSystemItem] = []

    def add(self, *items: FileSystemItem) -> Directory:
        """Add items to the directory. Returns self for chaining."""
        for item in items:
            item.parent = self
            self._children.append(item)
        return self

    def remove(self, item: FileSystemItem):
        self._children.remove(item)
        item.parent = None

    def get_size(self) -> int:
        """Recursively sum up the size of ALL children."""
        return sum(child.get_size() for child in self._children)

    def display(self, indent: int = 0) -> str:
        lines = [f"{'  ' * indent}📁 {self.name}/"]
        for child in self._children:
            lines.append(child.display(indent + 1))
        return "\n".join(lines)

    def search(self, query: str) -> list[FileSystemItem]:
        """Recursively search all children."""
        results: list[FileSystemItem] = []
        if query.lower() in self.name.lower():
            results.append(self)
        for child in self._children:
            results.extend(child.search(query))
        return results

    @property
    def children(self) -> list[FileSystemItem]:
        return list(self._children)

    def count_items(self) -> tuple[int, int]:
        """Count total files and directories recursively."""
        files, dirs = 0, 0
        for child in self._children:
            if isinstance(child, File):
                files += 1
            elif isinstance(child, Directory):
                dirs += 1
                sub_files, sub_dirs = child.count_items()
                files += sub_files
                dirs += sub_dirs
        return files, dirs


# ═══════════════════════════════════════════════════════
#  Real-World: Organization Hierarchy (another composite)
# ═══════════════════════════════════════════════════════

class OrgUnit(ABC):
    """Uniform interface for employees and departments."""

    @abstractmethod
    def total_salary(self) -> float:
        pass

    @abstractmethod
    def headcount(self) -> int:
        pass

    @abstractmethod
    def display(self, indent: int = 0) -> str:
        pass


class Employee(OrgUnit):
    def __init__(self, name: str, role: str, salary: float):
        self.name = name
        self.role = role
        self.salary = salary

    def total_salary(self) -> float:
        return self.salary

    def headcount(self) -> int:
        return 1

    def display(self, indent: int = 0) -> str:
        return f"{'  ' * indent}👤 {self.name} ({self.role}) — ${self.salary:,.0f}"


class Department(OrgUnit):
    def __init__(self, name: str):
        self.name = name
        self._members: list[OrgUnit] = []

    def add(self, *members: OrgUnit) -> Department:
        self._members.extend(members)
        return self

    def total_salary(self) -> float:
        return sum(m.total_salary() for m in self._members)

    def headcount(self) -> int:
        return sum(m.headcount() for m in self._members)

    def display(self, indent: int = 0) -> str:
        lines = [f"{'  ' * indent}🏢 {self.name} (headcount: {self.headcount()}, "
                 f"budget: ${self.total_salary():,.0f})"]
        for member in self._members:
            lines.append(member.display(indent + 1))
        return "\n".join(lines)


# ─────────────────────────────────────────────────────
#  Demo
# ─────────────────────────────────────────────────────

def demo():
    print("=" * 60)
    print("  COMPOSITE PATTERN DEMO")
    print("=" * 60)

    # --- Build a file system tree ---
    print("\n1. File System Tree:")
    root = Directory("project")
    src = Directory("src")
    src.add(
        File("main.py", 4200, "code"),
        File("utils.py", 1800, "code"),
        File("config.json", 500, "data"),
    )
    tests = Directory("tests")
    tests.add(
        File("test_main.py", 2100, "code"),
        File("test_utils.py", 1500, "code"),
    )
    assets = Directory("assets")
    images = Directory("images")
    images.add(
        File("logo.png", 152000, "image"),
        File("banner.png", 320000, "image"),
    )
    assets.add(images, File("data.csv", 45000, "data"))
    root.add(src, tests, assets, File("README.md", 3200, "text"))
    print(root.display())

    # --- Uniform operations ---
    print(f"\n2. Total project size: {root.get_size():,} bytes")
    files, dirs = root.count_items()
    print(f"   Files: {files}, Directories: {dirs}")

    # --- Search ---
    print("\n3. Search for 'test':")
    results = root.search("test")
    for item in results:
        print(f"   Found: {item.get_path()}")

    # --- Organization ---
    print("\n4. Organization Hierarchy:")
    engineering = Department("Engineering")
    engineering.add(
        Employee("Alice", "Tech Lead", 180000),
        Employee("Bob", "Senior Dev", 150000),
        Employee("Charlie", "Junior Dev", 95000),
    )
    marketing = Department("Marketing")
    marketing.add(
        Employee("Dana", "Marketing Lead", 140000),
        Employee("Eve", "Content Writer", 85000),
    )
    company = Department("Acme Corp")
    company.add(
        Employee("CEO", "Chief Executive", 250000),
        engineering,
        marketing,
    )
    print(company.display())

    print("\n💡 KEY INSIGHT:")
    print("   Both File and Directory implement get_size(). The client")
    print("   calls get_size() on ANY node — it doesn't need to know")
    print("   whether it's a leaf or a branch. Composites delegate to")
    print("   children recursively. Same pattern: org chart, GUI trees, menus.")


if __name__ == "__main__":
    demo()
