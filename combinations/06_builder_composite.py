"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  COMBINATION: Builder + Composite                                           ║
║  Real-World App: HTML Document Builder                                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  How they combine:                                                          ║
║    • Composite defines the tree structure (HTML elements)                   ║
║    • Builder provides a fluent API to construct the tree step by step      ║
║    Building a complex tree manually is error-prone — the builder           ║
║    makes it clean and readable.                                             ║
║                                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from abc import ABC, abstractmethod


# ═══════════════════════════════════════════════════════
#  Composite: HTML element tree
# ═══════════════════════════════════════════════════════

class HTMLNode(ABC):
    """Component interface for the HTML tree."""

    @abstractmethod
    def render(self, indent: int = 0) -> str:
        pass


class TextNode(HTMLNode):
    """Leaf — plain text content."""

    def __init__(self, text: str):
        self.text = text

    def render(self, indent: int = 0) -> str:
        return "  " * indent + self.text


class Element(HTMLNode):
    """Composite — can contain other elements and text."""

    def __init__(self, tag: str, attributes: dict[str, str] | None = None):
        self.tag = tag
        self.attributes = attributes or {}
        self.children: list[HTMLNode] = []

    def add_child(self, child: HTMLNode) -> Element:
        self.children.append(child)
        return self

    def render(self, indent: int = 0) -> str:
        prefix = "  " * indent
        attrs = ""
        if self.attributes:
            attrs = " " + " ".join(f'{k}="{v}"' for k, v in self.attributes.items())

        if not self.children:
            return f"{prefix}<{self.tag}{attrs}/>"

        # Single text child — inline
        if len(self.children) == 1 and isinstance(self.children[0], TextNode):
            return f"{prefix}<{self.tag}{attrs}>{self.children[0].text}</{self.tag}>"

        lines = [f"{prefix}<{self.tag}{attrs}>"]
        for child in self.children:
            lines.append(child.render(indent + 1))
        lines.append(f"{prefix}</{self.tag}>")
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════
#  Builder: Fluent API for constructing HTML
# ═══════════════════════════════════════════════════════

class HTMLBuilder:
    """
    Builder makes constructing the Composite tree clean and intuitive.

    Without the builder, you'd have to manually create Elements,
    add children, track parent references, etc.
    """

    def __init__(self):
        self._root: Element | None = None
        self._stack: list[Element] = []  # Track current nesting level

    @property
    def _current(self) -> Element:
        return self._stack[-1] if self._stack else None

    def document(self, title: str = "Document") -> HTMLBuilder:
        """Start an HTML document."""
        html = Element("html", {"lang": "en"})
        head = Element("head")
        head.add_child(Element("title").add_child(TextNode(title)))
        head.add_child(Element("meta", {"charset": "utf-8"}))
        html.add_child(head)
        body = Element("body")
        html.add_child(body)
        self._root = html
        self._stack = [body]  # Start building inside <body>
        return self

    def open(self, tag: str, **attrs) -> HTMLBuilder:
        """Open a new element (push onto stack)."""
        elem = Element(tag, attrs if attrs else None)
        if self._current:
            self._current.add_child(elem)
        else:
            self._root = elem
        self._stack.append(elem)
        return self

    def close(self) -> HTMLBuilder:
        """Close the current element (pop from stack)."""
        if self._stack:
            self._stack.pop()
        return self

    def text(self, content: str) -> HTMLBuilder:
        """Add text content to the current element."""
        if self._current:
            self._current.add_child(TextNode(content))
        return self

    # --- Convenience methods ---

    def h(self, level: int, text: str, **attrs) -> HTMLBuilder:
        """Heading shorthand."""
        heading = Element(f"h{level}", attrs if attrs else None)
        heading.add_child(TextNode(text))
        if self._current:
            self._current.add_child(heading)
        return self

    def p(self, text: str, **attrs) -> HTMLBuilder:
        """Paragraph shorthand."""
        para = Element("p", attrs if attrs else None)
        para.add_child(TextNode(text))
        if self._current:
            self._current.add_child(para)
        return self

    def img(self, src: str, alt: str = "", **attrs) -> HTMLBuilder:
        all_attrs = {"src": src, "alt": alt, **attrs}
        if self._current:
            self._current.add_child(Element("img", all_attrs))
        return self

    def link(self, href: str, text: str, **attrs) -> HTMLBuilder:
        a = Element("a", {"href": href, **attrs})
        a.add_child(TextNode(text))
        if self._current:
            self._current.add_child(a)
        return self

    def ul(self, items: list[str]) -> HTMLBuilder:
        """Unordered list shorthand."""
        ul = Element("ul")
        for item in items:
            li = Element("li")
            li.add_child(TextNode(item))
            ul.add_child(li)
        if self._current:
            self._current.add_child(ul)
        return self

    def table(self, headers: list[str], rows: list[list[str]]) -> HTMLBuilder:
        """Table shorthand."""
        table = Element("table", {"class": "data-table"})
        # Header row
        thead = Element("thead")
        tr = Element("tr")
        for h in headers:
            th = Element("th")
            th.add_child(TextNode(h))
            tr.add_child(th)
        thead.add_child(tr)
        table.add_child(thead)
        # Data rows
        tbody = Element("tbody")
        for row in rows:
            tr = Element("tr")
            for cell in row:
                td = Element("td")
                td.add_child(TextNode(cell))
                tr.add_child(td)
            tbody.add_child(tr)
        table.add_child(tbody)
        if self._current:
            self._current.add_child(table)
        return self

    def build(self) -> Element:
        return self._root


# ═══════════════════════════════════════════════════════
#  Director: Pre-built document templates
# ═══════════════════════════════════════════════════════

class HTMLDirector:
    """Pre-built templates using the builder."""

    @staticmethod
    def landing_page(builder: HTMLBuilder, company: str, tagline: str) -> Element:
        return (builder
                .document(f"{company} — {tagline}")
                .open("header", id="main-header")
                    .open("nav", **{"class": "navbar"})
                        .link("#", company, **{"class": "logo"})
                        .open("div", **{"class": "nav-links"})
                            .link("#features", "Features")
                            .link("#pricing", "Pricing")
                            .link("#contact", "Contact")
                        .close()
                    .close()
                .close()
                .open("main")
                    .open("section", id="hero", **{"class": "hero-section"})
                        .h(1, tagline)
                        .p("Start building amazing things today.")
                        .link("#signup", "Get Started →", **{"class": "cta-button"})
                    .close()
                    .open("section", id="features")
                        .h(2, "Features")
                        .ul(["⚡ Lightning Fast", "🔒 Secure by Default", "📱 Mobile First"])
                    .close()
                .close()
                .open("footer")
                    .p(f"© 2024 {company}. All rights reserved.")
                .close()
                .build())

    @staticmethod
    def report_page(builder: HTMLBuilder, title: str, data: list[list[str]]) -> Element:
        return (builder
                .document(title)
                .h(1, title)
                .p(f"Generated report with {len(data)} rows of data.")
                .table(["ID", "Name", "Value", "Status"], data)
                .open("footer")
                    .p("Report generated automatically.")
                .close()
                .build())


# ─────────────────────────────────────────────────────
#  Demo
# ─────────────────────────────────────────────────────

def demo():
    print("=" * 60)
    print("  BUILDER + COMPOSITE COMBINATION DEMO")
    print("  HTML Document Builder")
    print("=" * 60)

    # --- Manual building ---
    print("\n1. Build a page with fluent API:")
    page = (HTMLBuilder()
            .document("My Blog")
            .h(1, "Welcome to My Blog")
            .p("This is a post about design patterns.")
            .open("div", **{"class": "content"})
                .h(2, "What are Design Patterns?")
                .p("Design patterns are reusable solutions to common problems.")
                .ul(["Creational", "Structural", "Behavioral"])
                .link("https://example.com", "Learn more")
            .close()
            .build())
    print(page.render())

    # --- Director: Landing page ---
    print(f"\n{'═' * 50}")
    print("2. Director — Landing Page Template:")
    landing = HTMLDirector.landing_page(
        HTMLBuilder(), "Acme Inc", "Build the Future"
    )
    print(landing.render())

    # --- Director: Report ---
    print(f"\n{'═' * 50}")
    print("3. Director — Report Page:")
    report = HTMLDirector.report_page(
        HTMLBuilder(),
        "Q4 Sales Report",
        [
            ["1", "Widget A", "$15,000", "✅"],
            ["2", "Widget B", "$22,500", "✅"],
            ["3", "Widget C", "$8,200", "⚠️"],
        ]
    )
    print(report.render())

    # --- Composite operations ---
    print(f"\n{'═' * 50}")
    print("4. Composite tree operations:")
    simple = (HTMLBuilder()
              .open("div", id="root")
                .open("section")
                    .h(1, "Title")
                    .p("Paragraph 1")
                    .p("Paragraph 2")
                .close()
                .open("section")
                    .p("Another section")
                .close()
              .close()
              .build())

    def count_nodes(node: HTMLNode) -> int:
        if isinstance(node, TextNode):
            return 1
        elif isinstance(node, Element):
            return 1 + sum(count_nodes(c) for c in node.children)
        return 0

    print(f"  Total nodes: {count_nodes(simple)}")
    print(f"  Rendered:\n{simple.render()}")

    print("\n💡 HOW THEY COMBINE:")
    print("   COMPOSITE = the HTML element tree (Element → children → Element...)")
    print("   BUILDER = fluent API to construct the tree step by step")
    print("   Without Builder, constructing nested HTML trees is painful:")
    print("     div = Element('div')")
    print("     section = Element('section')")
    print("     div.add_child(section)")
    print("     h1 = Element('h1')")
    print("     h1.add_child(TextNode('Title'))")
    print("     section.add_child(h1)  # 😩 So much nesting!")
    print("   With Builder: .open('div').open('section').h(1, 'Title')  # 😊")


if __name__ == "__main__":
    demo()
