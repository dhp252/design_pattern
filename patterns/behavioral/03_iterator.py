"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  ITERATOR — Behavioral Pattern                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  Intent:   Provide a way to access elements of a collection sequentially   ║
║            without exposing its underlying representation.                  ║
║                                                                             ║
║  Problem:  Collections have different internal structures (arrays, trees,  ║
║            graphs), but clients want to traverse them uniformly.           ║
║                                                                             ║
║  Solution: Extract the traversal logic into an iterator object.            ║
║            The collection provides a way to create iterators.              ║
║                                                                             ║
║  Use When:                                                                  ║
║    • You want to traverse a collection without exposing internals          ║
║    • You need multiple traversal strategies for the same collection        ║
║    • You want a uniform interface for traversing different collections     ║
║                                                                             ║
║  Python Bonus:                                                              ║
║    Python's iterator protocol (__iter__, __next__) and generators          ║
║    make this pattern nearly invisible. It's deeply built into the          ║
║    language (for loops, comprehensions, zip, map, etc.)                     ║
║                                                                             ║
║  Related Patterns:                                                          ║
║    • Composite — iterate over tree structures                              ║
║    • Factory Method — collection creates its own iterators                 ║
║    • Visitor — iterator determines WHAT to visit, visitor determines HOW   ║
║                                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from collections.abc import Iterator, Iterable
from typing import Any


# ═══════════════════════════════════════════════════════
#  Classic Iterator (explicit __iter__/__next__)
# ═══════════════════════════════════════════════════════

class PaginatedAPI:
    """
    Simulates paginated API results.
    Internally stores all data but only returns one page at a time.
    """

    def __init__(self, data: list[dict], page_size: int = 3):
        self._data = data
        self._page_size = page_size
        self._total_pages = (len(data) + page_size - 1) // page_size

    def get_page(self, page: int) -> list[dict]:
        """Simulate API call — returns one page of data."""
        start = page * self._page_size
        end = start + self._page_size
        return self._data[start:end]

    @property
    def total_pages(self) -> int:
        return self._total_pages


class PaginatedIterator(Iterator):
    """
    Iterates over ALL pages of a paginated API,
    yielding individual items transparently.

    The client gets a seamless stream of items without
    knowing about pagination.
    """

    def __init__(self, api: PaginatedAPI):
        self._api = api
        self._current_page = 0
        self._current_items: list[dict] = []
        self._item_index = 0
        self._load_page()

    def _load_page(self):
        if self._current_page < self._api.total_pages:
            self._current_items = self._api.get_page(self._current_page)
            self._item_index = 0

    def __next__(self) -> dict:
        # If current page is exhausted, try next page
        while self._item_index >= len(self._current_items):
            self._current_page += 1
            if self._current_page >= self._api.total_pages:
                raise StopIteration
            self._load_page()

        item = self._current_items[self._item_index]
        self._item_index += 1
        return item

    def __iter__(self) -> PaginatedIterator:
        return self


class PaginatedCollection(Iterable):
    """Makes the paginated API iterable."""

    def __init__(self, api: PaginatedAPI):
        self._api = api

    def __iter__(self) -> PaginatedIterator:
        return PaginatedIterator(self._api)


# ═══════════════════════════════════════════════════════
#  Pythonic: Generator-based Iterators
# ═══════════════════════════════════════════════════════

def paginated_fetch(api: PaginatedAPI):
    """
    Generator function — the Pythonic way to create iterators.
    No need for a separate iterator class!
    """
    for page_num in range(api.total_pages):
        page = api.get_page(page_num)
        yield from page  # Yields each item from the page


def fibonacci(limit: int = None):
    """Infinite generator — fibonacci numbers."""
    a, b = 0, 1
    count = 0
    while limit is None or count < limit:
        yield a
        a, b = b, a + b
        count += 1


def flatten(nested):
    """Recursively flatten nested iterables (generator)."""
    for item in nested:
        if isinstance(item, (list, tuple)):
            yield from flatten(item)
        else:
            yield item


# ═══════════════════════════════════════════════════════
#  Multiple Traversal Strategies
# ═══════════════════════════════════════════════════════

class TreeNode:
    def __init__(self, value: str, children: list[TreeNode] | None = None):
        self.value = value
        self.children = children or []

    def add(self, *nodes: TreeNode) -> TreeNode:
        self.children.extend(nodes)
        return self


def depth_first(node: TreeNode):
    """DFS traversal using a generator."""
    yield node.value
    for child in node.children:
        yield from depth_first(child)


def breadth_first(node: TreeNode):
    """BFS traversal using a generator."""
    queue = [node]
    while queue:
        current = queue.pop(0)
        yield current.value
        queue.extend(current.children)


def leaves_only(node: TreeNode):
    """Yield only leaf nodes."""
    if not node.children:
        yield node.value
    else:
        for child in node.children:
            yield from leaves_only(child)


# ═══════════════════════════════════════════════════════
#  Custom Iterable Collection
# ═══════════════════════════════════════════════════════

class SortedCollection:
    """A collection that always iterates in sorted order."""

    def __init__(self):
        self._items: list[Any] = []

    def add(self, item: Any):
        self._items.append(item)

    def __iter__(self):
        """Iterate in sorted order without mutating internal list."""
        return iter(sorted(self._items))

    def __reversed__(self):
        """Reverse sorted order."""
        return iter(sorted(self._items, reverse=True))

    def __len__(self):
        return len(self._items)

    def __contains__(self, item):
        return item in self._items


# ─────────────────────────────────────────────────────
#  Demo
# ─────────────────────────────────────────────────────

def demo():
    print("=" * 60)
    print("  ITERATOR PATTERN DEMO")
    print("=" * 60)

    # --- Paginated API ---
    data = [{"id": i, "name": f"User-{i}"} for i in range(1, 11)]
    api = PaginatedAPI(data, page_size=3)

    print(f"\n1. Paginated API ({len(data)} items, page_size=3):")
    print("   Classic iterator:")
    for item in PaginatedCollection(api):
        print(f"     {item}")

    print("\n   Generator version (same result, less code):")
    for item in paginated_fetch(api):
        print(f"     {item}")

    # --- Generators ---
    print("\n2. Fibonacci Generator (first 10):")
    print(f"   {list(fibonacci(10))}")

    print("\n3. Flatten Nested Lists:")
    nested = [1, [2, 3, [4, 5]], [6, [7, [8, 9]]], 10]
    print(f"   Input:   {nested}")
    print(f"   Flatten: {list(flatten(nested))}")

    # --- Tree traversal ---
    print("\n4. Tree Traversal Strategies:")
    tree = TreeNode("CEO")
    tree.add(
        TreeNode("CTO").add(
            TreeNode("Dev Lead").add(TreeNode("Dev-1"), TreeNode("Dev-2")),
            TreeNode("QA Lead").add(TreeNode("QA-1")),
        ),
        TreeNode("CFO").add(
            TreeNode("Accountant"),
        ),
    )
    print(f"   DFS:    {list(depth_first(tree))}")
    print(f"   BFS:    {list(breadth_first(tree))}")
    print(f"   Leaves: {list(leaves_only(tree))}")

    # --- Sorted collection ---
    print("\n5. SortedCollection (always iterates in order):")
    sc = SortedCollection()
    for name in ["Charlie", "Alice", "Eve", "Bob", "Dana"]:
        sc.add(name)
    print(f"   Forward: {list(sc)}")
    print(f"   Reverse: {list(reversed(sc))}")
    print(f"   Contains 'Bob': {'Bob' in sc}")

    # --- Iterator protocol integration ---
    print("\n6. Python Iterator Protocol (built-in power):")
    numbers = fibonacci(20)
    evens = filter(lambda x: x % 2 == 0, numbers)
    first_5 = list(zip(range(5), evens))
    print(f"   First 5 even Fibonacci: {[v for _, v in first_5]}")

    print("\n💡 KEY INSIGHT:")
    print("   In Python, the Iterator pattern is built into the language.")
    print("   __iter__ + __next__ = class-based iterator.")
    print("   yield = generator-based iterator (preferred for simplicity).")
    print("   Same collection, different traversals — just swap the generator!")


if __name__ == "__main__":
    demo()
