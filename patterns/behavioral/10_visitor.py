"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  VISITOR — Behavioral Pattern                                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  Intent:   Add new operations to existing object structures without        ║
║            modifying their classes.                                         ║
║                                                                             ║
║  Problem:  You have a stable class hierarchy (e.g., AST nodes) and need   ║
║            to add new operations (export to HTML, PDF, etc.) without      ║
║            changing the node classes every time.                           ║
║                                                                             ║
║  Solution: Define a Visitor interface with a visit method for each node    ║
║            type. Nodes accept visitors via double dispatch. New operations ║
║            = new Visitor, zero changes to node classes.                    ║
║                                                                             ║
║  Use When:                                                                  ║
║    • You need to add operations to a stable class hierarchy frequently    ║
║    • You want to keep related operations together (in one visitor)         ║
║    • The class hierarchy rarely changes but operations do                  ║
║                                                                             ║
║  Trade-off:                                                                 ║
║    Adding new node types is HARD (must update ALL visitors).               ║
║    Adding new operations is EASY (just add a new visitor).                 ║
║                                                                             ║
║  Real-World Analogy:                                                        ║
║    A tax inspector "visits" different properties (house, apartment, land)  ║
║    and applies different calculations to each, without the properties      ║
║    needing to know about tax calculations.                                  ║
║                                                                             ║
║  Related Patterns:                                                          ║
║    • Iterator — traverse the structure to apply the visitor               ║
║    • Composite — visitors often work on composite trees                   ║
║    • Strategy — Visitor adds operations externally; Strategy does it      ║
║      internally                                                            ║
║                                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from abc import ABC, abstractmethod


# ═══════════════════════════════════════════════════════
#  Element Interface (stable hierarchy — rarely changes)
# ═══════════════════════════════════════════════════════

class DocumentNode(ABC):
    """
    Each node has an accept() method that takes a visitor.
    This is the "double dispatch" mechanism.
    """

    @abstractmethod
    def accept(self, visitor: DocumentVisitor) -> str:
        pass


class Heading(DocumentNode):
    def __init__(self, text: str, level: int = 1):
        self.text = text
        self.level = level

    def accept(self, visitor: DocumentVisitor) -> str:
        return visitor.visit_heading(self)


class Paragraph(DocumentNode):
    def __init__(self, text: str):
        self.text = text

    def accept(self, visitor: DocumentVisitor) -> str:
        return visitor.visit_paragraph(self)


class Bold(DocumentNode):
    def __init__(self, text: str):
        self.text = text

    def accept(self, visitor: DocumentVisitor) -> str:
        return visitor.visit_bold(self)


class CodeBlock(DocumentNode):
    def __init__(self, code: str, language: str = "python"):
        self.code = code
        self.language = language

    def accept(self, visitor: DocumentVisitor) -> str:
        return visitor.visit_code_block(self)


class Link(DocumentNode):
    def __init__(self, text: str, url: str):
        self.text = text
        self.url = url

    def accept(self, visitor: DocumentVisitor) -> str:
        return visitor.visit_link(self)


class Image(DocumentNode):
    def __init__(self, alt_text: str, url: str):
        self.alt_text = alt_text
        self.url = url

    def accept(self, visitor: DocumentVisitor) -> str:
        return visitor.visit_image(self)


class Document:
    """A document is a list of nodes."""

    def __init__(self):
        self.nodes: list[DocumentNode] = []

    def add(self, node: DocumentNode) -> Document:
        self.nodes.append(node)
        return self

    def accept(self, visitor: DocumentVisitor) -> str:
        results = [node.accept(visitor) for node in self.nodes]
        return visitor.join(results)


# ═══════════════════════════════════════════════════════
#  Visitor Interface
# ═══════════════════════════════════════════════════════

class DocumentVisitor(ABC):
    """
    A visit method for each concrete element type.
    Adding a new OPERATION = adding a new Visitor class.
    No changes to the element classes needed!
    """

    @abstractmethod
    def visit_heading(self, heading: Heading) -> str:
        pass

    @abstractmethod
    def visit_paragraph(self, paragraph: Paragraph) -> str:
        pass

    @abstractmethod
    def visit_bold(self, bold: Bold) -> str:
        pass

    @abstractmethod
    def visit_code_block(self, code: CodeBlock) -> str:
        pass

    @abstractmethod
    def visit_link(self, link: Link) -> str:
        pass

    @abstractmethod
    def visit_image(self, image: Image) -> str:
        pass

    def join(self, parts: list[str]) -> str:
        return "\n".join(parts)


# ═══════════════════════════════════════════════════════
#  Concrete Visitors (operations)
# ═══════════════════════════════════════════════════════

class HTMLVisitor(DocumentVisitor):
    """Export document to HTML."""

    def visit_heading(self, h: Heading) -> str:
        return f"<h{h.level}>{h.text}</h{h.level}>"

    def visit_paragraph(self, p: Paragraph) -> str:
        return f"<p>{p.text}</p>"

    def visit_bold(self, b: Bold) -> str:
        return f"<strong>{b.text}</strong>"

    def visit_code_block(self, c: CodeBlock) -> str:
        return f'<pre><code class="{c.language}">{c.code}</code></pre>'

    def visit_link(self, l: Link) -> str:
        return f'<a href="{l.url}">{l.text}</a>'

    def visit_image(self, i: Image) -> str:
        return f'<img src="{i.url}" alt="{i.alt_text}"/>'

    def join(self, parts: list[str]) -> str:
        return "\n".join(parts)


class MarkdownVisitor(DocumentVisitor):
    """Export document to Markdown."""

    def visit_heading(self, h: Heading) -> str:
        return f"{'#' * h.level} {h.text}"

    def visit_paragraph(self, p: Paragraph) -> str:
        return p.text

    def visit_bold(self, b: Bold) -> str:
        return f"**{b.text}**"

    def visit_code_block(self, c: CodeBlock) -> str:
        return f"```{c.language}\n{c.code}\n```"

    def visit_link(self, l: Link) -> str:
        return f"[{l.text}]({l.url})"

    def visit_image(self, i: Image) -> str:
        return f"![{i.alt_text}]({i.url})"

    def join(self, parts: list[str]) -> str:
        return "\n\n".join(parts)


class PlainTextVisitor(DocumentVisitor):
    """Export document to plain text."""

    def visit_heading(self, h: Heading) -> str:
        underline = "=" if h.level == 1 else "-"
        return f"{h.text}\n{underline * len(h.text)}"

    def visit_paragraph(self, p: Paragraph) -> str:
        return p.text

    def visit_bold(self, b: Bold) -> str:
        return b.text.upper()

    def visit_code_block(self, c: CodeBlock) -> str:
        indented = "\n".join(f"    {line}" for line in c.code.split("\n"))
        return f"Code ({c.language}):\n{indented}"

    def visit_link(self, l: Link) -> str:
        return f"{l.text} ({l.url})"

    def visit_image(self, i: Image) -> str:
        return f"[Image: {i.alt_text}] ({i.url})"

    def join(self, parts: list[str]) -> str:
        return "\n\n".join(parts)


class WordCountVisitor(DocumentVisitor):
    """Analyze the document — not an export, but a computation."""

    def __init__(self):
        self.total_words = 0
        self.total_chars = 0
        self.node_counts: dict[str, int] = {}

    def _count(self, text: str, node_type: str) -> str:
        words = len(text.split())
        self.total_words += words
        self.total_chars += len(text)
        self.node_counts[node_type] = self.node_counts.get(node_type, 0) + 1
        return ""

    def visit_heading(self, h: Heading) -> str:
        return self._count(h.text, "heading")

    def visit_paragraph(self, p: Paragraph) -> str:
        return self._count(p.text, "paragraph")

    def visit_bold(self, b: Bold) -> str:
        return self._count(b.text, "bold")

    def visit_code_block(self, c: CodeBlock) -> str:
        return self._count(c.code, "code")

    def visit_link(self, l: Link) -> str:
        return self._count(l.text, "link")

    def visit_image(self, i: Image) -> str:
        self.node_counts["image"] = self.node_counts.get("image", 0) + 1
        return ""

    def join(self, parts: list[str]) -> str:
        return (f"Words: {self.total_words} | "
                f"Chars: {self.total_chars} | "
                f"Nodes: {self.node_counts}")


# ─────────────────────────────────────────────────────
#  Demo
# ─────────────────────────────────────────────────────

def demo():
    print("=" * 60)
    print("  VISITOR PATTERN DEMO")
    print("=" * 60)

    # Build a document (the structure — stable)
    doc = Document()
    doc.add(Heading("Design Patterns in Python", level=1))
    doc.add(Paragraph("A comprehensive guide to understanding design patterns."))
    doc.add(Heading("Getting Started", level=2))
    doc.add(Paragraph("First, understand the problem each pattern solves."))
    doc.add(Bold("Key concept: favor composition over inheritance."))
    doc.add(CodeBlock("class Strategy(ABC):\n    @abstractmethod\n    def execute(self): pass"))
    doc.add(Link("Full Reference", "https://refactoring.guru"))
    doc.add(Image("Pattern diagram", "https://example.com/diagram.png"))

    # Export to different formats (the operations — frequently added)
    visitors = [
        ("HTML", HTMLVisitor()),
        ("Markdown", MarkdownVisitor()),
        ("Plain Text", PlainTextVisitor()),
    ]

    for name, visitor in visitors:
        print(f"\n{'─' * 40}")
        print(f"  Export to {name}:")
        print(f"{'─' * 40}")
        result = doc.accept(visitor)
        for line in result.split("\n"):
            print(f"  {line}")

    # Analytical visitor (not an export — shows visitor flexibility)
    print(f"\n{'─' * 40}")
    print(f"  Document Analysis:")
    print(f"{'─' * 40}")
    counter = WordCountVisitor()
    stats = doc.accept(counter)
    print(f"  {stats}")

    print("\n💡 KEY INSIGHT:")
    print("   The Document nodes NEVER change when we add new operations.")
    print("   HTMLVisitor, MarkdownVisitor, PlainTextVisitor, WordCountVisitor —")
    print("   each is a NEW OPERATION added WITHOUT modifying any node class.")
    print("   Trade-off: adding a new node type DOES require updating all visitors.")


if __name__ == "__main__":
    demo()
