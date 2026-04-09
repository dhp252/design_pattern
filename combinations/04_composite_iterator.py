"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  COMBINATION: Composite + Iterator                                          ║
║  Real-World App: File System Browser                                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  How they combine:                                                          ║
║    • Composite creates the tree structure (files + directories)             ║
║    • Iterator provides multiple traversal strategies over the tree         ║
║    Different iterators = different views of the same structure.             ║
║                                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Callable


# ═══════════════════════════════════════════════════════
#  Composite: File system tree
# ═══════════════════════════════════════════════════════

class FSNode(ABC):
    def __init__(self, name: str):
        self.name = name
        self.parent: FSNode | None = None

    @abstractmethod
    def size(self) -> int:
        pass

    @abstractmethod
    def is_directory(self) -> bool:
        pass

    def path(self) -> str:
        parts = []
        node: FSNode | None = self
        while node:
            parts.append(node.name)
            node = node.parent
        return "/".join(reversed(parts))

    @property
    def depth(self) -> int:
        d = 0
        node = self.parent
        while node:
            d += 1
            node = node.parent
        return d


class File(FSNode):
    def __init__(self, name: str, size_bytes: int, file_type: str = "file"):
        super().__init__(name)
        self._size = size_bytes
        self.file_type = file_type

    def size(self) -> int:
        return self._size

    def is_directory(self) -> bool:
        return False

    def __repr__(self):
        return f"File({self.name}, {self._size}B)"


class Directory(FSNode):
    def __init__(self, name: str):
        super().__init__(name)
        self.children: list[FSNode] = []

    def add(self, *nodes: FSNode) -> Directory:
        for node in nodes:
            node.parent = self
            self.children.append(node)
        return self

    def size(self) -> int:
        return sum(child.size() for child in self.children)

    def is_directory(self) -> bool:
        return True

    def __repr__(self):
        return f"Dir({self.name}, {len(self.children)} children)"


# ═══════════════════════════════════════════════════════
#  Iterators: Different traversal strategies
# ═══════════════════════════════════════════════════════

def depth_first(node: FSNode):
    """DFS — go deep before going wide."""
    yield node
    if isinstance(node, Directory):
        for child in node.children:
            yield from depth_first(child)


def breadth_first(node: FSNode):
    """BFS — level by level."""
    queue = [node]
    while queue:
        current = queue.pop(0)
        yield current
        if isinstance(current, Directory):
            queue.extend(current.children)


def files_only(node: FSNode):
    """Yield only files (skip directories)."""
    if isinstance(node, File):
        yield node
    elif isinstance(node, Directory):
        for child in node.children:
            yield from files_only(child)


def directories_only(node: FSNode):
    """Yield only directories."""
    if isinstance(node, Directory):
        yield node
        for child in node.children:
            yield from directories_only(child)


def by_extension(node: FSNode, ext: str):
    """Find files with a specific extension."""
    for f in files_only(node):
        if f.name.endswith(ext):
            yield f


def by_size(node: FSNode, min_bytes: int = 0, max_bytes: int = float('inf')):
    """Find files within a size range."""
    for f in files_only(node):
        if min_bytes <= f.size() <= max_bytes:
            yield f


def sorted_by_size(node: FSNode, reverse: bool = True):
    """All files sorted by size."""
    all_files = list(files_only(node))
    all_files.sort(key=lambda f: f.size(), reverse=reverse)
    yield from all_files


# ═══════════════════════════════════════════════════════
#  File System Browser (uses both patterns)
# ═══════════════════════════════════════════════════════

class FileBrowser:
    """Uses Composite tree + Iterator strategies for browsing."""

    def __init__(self, root: Directory):
        self.root = root

    def tree_view(self, node: FSNode = None) -> str:
        """Classic tree view using DFS."""
        node = node or self.root
        lines = []
        for item in depth_first(node):
            indent = "  " * item.depth
            if item.is_directory():
                lines.append(f"{indent}📁 {item.name}/")
            else:
                lines.append(f"{indent}📄 {item.name} ({self._format_size(item.size())})")
        return "\n".join(lines)

    def find(self, extension: str) -> list[str]:
        """Find files by extension."""
        return [f.path() for f in by_extension(self.root, extension)]

    def largest_files(self, n: int = 5) -> list[tuple[str, int]]:
        """Top N largest files."""
        return [(f.path(), f.size()) for f in list(sorted_by_size(self.root))[:n]]

    def size_report(self) -> str:
        """Directory sizes using Composite's recursive size()."""
        lines = ["  📊 Directory Sizes:"]
        for d in directories_only(self.root):
            indent = "  " * d.depth
            lines.append(f"  {indent}📁 {d.name}: {self._format_size(d.size())}")
        return "\n".join(lines)

    def stats(self) -> dict:
        """Overall statistics."""
        files = list(files_only(self.root))
        dirs = list(directories_only(self.root))
        return {
            "total_files": len(files),
            "total_dirs": len(dirs),
            "total_size": self.root.size(),
            "avg_file_size": sum(f.size() for f in files) / len(files) if files else 0,
            "largest": max(files, key=lambda f: f.size()).name if files else "N/A",
        }

    @staticmethod
    def _format_size(size: int) -> str:
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.0f}{unit}"
            size /= 1024
        return f"{size:.0f}TB"


# ─────────────────────────────────────────────────────
#  Demo
# ─────────────────────────────────────────────────────

def demo():
    print("=" * 60)
    print("  COMPOSITE + ITERATOR COMBINATION DEMO")
    print("  File System Browser")
    print("=" * 60)

    # Build a project file tree
    root = Directory("my-project")
    root.add(
        Directory("src").add(
            Directory("components").add(
                File("Header.tsx", 2400, "typescript"),
                File("Footer.tsx", 1800, "typescript"),
                File("Sidebar.tsx", 3200, "typescript"),
            ),
            Directory("hooks").add(
                File("useAuth.ts", 1500, "typescript"),
                File("useData.ts", 2100, "typescript"),
            ),
            File("App.tsx", 4500, "typescript"),
            File("index.ts", 800, "typescript"),
            File("styles.css", 12000, "css"),
        ),
        Directory("public").add(
            File("index.html", 2000, "html"),
            File("favicon.ico", 5000, "binary"),
            File("logo.png", 45000, "image"),
            File("banner.jpg", 180000, "image"),
        ),
        Directory("tests").add(
            File("App.test.tsx", 3500, "typescript"),
            File("hooks.test.ts", 2800, "typescript"),
        ),
        File("package.json", 1200, "json"),
        File("README.md", 8500, "markdown"),
        File("tsconfig.json", 600, "json"),
    )

    browser = FileBrowser(root)

    # --- Tree view (DFS) ---
    print("\n1. Tree View (Depth-First):")
    print(browser.tree_view())

    # --- BFS traversal ---
    print("\n2. Breadth-First (level by level):")
    for node in breadth_first(root):
        kind = "📁" if node.is_directory() else "📄"
        print(f"  L{node.depth} {kind} {node.name}")

    # --- Find by extension ---
    print("\n3. Find .tsx files:")
    for path in browser.find(".tsx"):
        print(f"  📄 {path}")

    # --- Largest files ---
    print("\n4. Top 5 largest files:")
    for path, size in browser.largest_files(5):
        print(f"  {browser._format_size(size):>8} — {path}")

    # --- Size report (Composite recursion) ---
    print(f"\n5. {browser.size_report()}")

    # --- Custom iterator: large images ---
    print("\n6. Custom iterator — images over 10KB:")
    for f in by_size(root, min_bytes=10000):
        if f.file_type == "image":
            print(f"  🖼️  {f.path()} ({browser._format_size(f.size())})")

    # --- Stats ---
    print("\n7. Stats:")
    stats = browser.stats()
    for k, v in stats.items():
        if isinstance(v, float):
            print(f"  {k}: {browser._format_size(int(v))}")
        elif isinstance(v, int) and k == "total_size":
            print(f"  {k}: {browser._format_size(v)}")
        else:
            print(f"  {k}: {v}")

    print("\n💡 HOW THEY COMBINE:")
    print("   COMPOSITE creates the tree (Directory contains Files and Directories)")
    print("   ITERATOR provides different ways to walk the tree:")
    print("     • DFS for tree view")
    print("     • BFS for level-by-level")
    print("     • Filtered for find-by-extension")
    print("     • Sorted for top-N queries")
    print("   Same tree structure, many traversal strategies!")


if __name__ == "__main__":
    demo()
