"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  ABSTRACT FACTORY — Creational Pattern                                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  Intent:   Provide an interface for creating FAMILIES of related objects    ║
║            without specifying their concrete classes.                       ║
║                                                                             ║
║  Problem:  You have multiple families of related products (e.g. Dark UI    ║
║            vs Light UI), and you need to ensure products from one family   ║
║            aren't mixed with products from another.                        ║
║                                                                             ║
║  Solution: Declare interfaces for each product type, then create an        ║
║            abstract factory with creation methods for each product.         ║
║            Concrete factories produce products of a single family.         ║
║                                                                             ║
║  Use When:                                                                  ║
║    • Your code needs to work with multiple families of related products    ║
║    • You want to ensure compatibility within a product family              ║
║    • You want to hide construction details from client code                ║
║                                                                             ║
║  Real-World Analogy:                                                        ║
║    An interior designer offers "Modern" or "Victorian" style packages.     ║
║    Each package includes matching furniture, lighting, and decor.           ║
║    You pick a style and everything coordinates perfectly.                   ║
║                                                                             ║
║  vs Factory Method:                                                         ║
║    Factory Method creates ONE product. Abstract Factory creates a FAMILY   ║
║    of related products using multiple factory methods.                      ║
║                                                                             ║
║  Related Patterns:                                                          ║
║    • Factory Method — Abstract Factory uses Factory Methods internally     ║
║    • Singleton — factories are often singletons                            ║
║    • Builder — can be used alongside to construct complex products         ║
║                                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from abc import ABC, abstractmethod


# ═══════════════════════════════════════════════════════
#  Product Interfaces
# ═══════════════════════════════════════════════════════

class Button(ABC):
    @abstractmethod
    def render(self) -> str:
        pass

    @abstractmethod
    def on_click(self) -> str:
        pass


class Input(ABC):
    @abstractmethod
    def render(self) -> str:
        pass

    @abstractmethod
    def get_value(self) -> str:
        pass


class Card(ABC):
    @abstractmethod
    def render(self, title: str, content: str) -> str:
        pass


# ═══════════════════════════════════════════════════════
#  Concrete Products — Dark Theme Family
# ═══════════════════════════════════════════════════════

class DarkButton(Button):
    def render(self) -> str:
        return "🌙 [████ BUTTON ████] bg:#1a1a2e, text:#e94560"

    def on_click(self) -> str:
        return "Dark button clicked — ripple effect ✨"


class DarkInput(Input):
    def render(self) -> str:
        return "🌙 [______________] bg:#16213e, border:#e94560"

    def get_value(self) -> str:
        return "dark_input_value"


class DarkCard(Card):
    def render(self, title: str, content: str) -> str:
        return (f"🌙 ┌─── {title} ───┐\n"
                f"   │ {content:<16} │  bg:#0f3460\n"
                f"   └──────────────────┘")


# ═══════════════════════════════════════════════════════
#  Concrete Products — Light Theme Family
# ═══════════════════════════════════════════════════════

class LightButton(Button):
    def render(self) -> str:
        return "☀️  [████ BUTTON ████] bg:#f5f5f5, text:#2d3436"

    def on_click(self) -> str:
        return "Light button clicked — shadow lift 📤"


class LightInput(Input):
    def render(self) -> str:
        return "☀️  [______________] bg:#ffffff, border:#dfe6e9"

    def get_value(self) -> str:
        return "light_input_value"


class LightCard(Card):
    def render(self, title: str, content: str) -> str:
        return (f"☀️  ┌─── {title} ───┐\n"
                f"   │ {content:<16} │  bg:#ffffff\n"
                f"   └──────────────────┘")


# ═══════════════════════════════════════════════════════
#  Abstract Factory
# ═══════════════════════════════════════════════════════

class UIFactory(ABC):
    """
    Each concrete factory produces a FAMILY of UI components
    that are guaranteed to be visually compatible.
    """

    @abstractmethod
    def create_button(self) -> Button:
        pass

    @abstractmethod
    def create_input(self) -> Input:
        pass

    @abstractmethod
    def create_card(self) -> Card:
        pass


class DarkThemeFactory(UIFactory):
    def create_button(self) -> Button:
        return DarkButton()

    def create_input(self) -> Input:
        return DarkInput()

    def create_card(self) -> Card:
        return DarkCard()


class LightThemeFactory(UIFactory):
    def create_button(self) -> Button:
        return LightButton()

    def create_input(self) -> Input:
        return LightInput()

    def create_card(self) -> Card:
        return LightCard()


# ═══════════════════════════════════════════════════════
#  Client Code — Works with ANY factory
# ═══════════════════════════════════════════════════════

class LoginPage:
    """
    The client code works with factories and products only through
    abstract interfaces. This lets you pass any factory subclass
    without breaking the client code.
    """

    def __init__(self, factory: UIFactory):
        self.button = factory.create_button()
        self.username_input = factory.create_input()
        self.password_input = factory.create_input()
        self.info_card = factory.create_card()

    def render(self) -> str:
        lines = [
            "  ╔══════════ LOGIN PAGE ══════════╗",
            f"  ║  {self.info_card.render('Welcome', 'Sign in below')}",
            f"  ║  Username: {self.username_input.render()}",
            f"  ║  Password: {self.password_input.render()}",
            f"  ║  Submit:   {self.button.render()}",
            "  ╚═════════════════════════════════╝",
        ]
        return "\n".join(lines)


# ─────────────────────────────────────────────────────
#  Pythonic Alternative: Factory Registry
# ─────────────────────────────────────────────────────

class ThemeRegistry:
    """
    Register theme factories by name — no if/elif chains needed.
    """
    _factories: dict[str, type[UIFactory]] = {}

    @classmethod
    def register(cls, name: str, factory_cls: type[UIFactory]):
        cls._factories[name] = factory_cls

    @classmethod
    def get_factory(cls, name: str) -> UIFactory:
        factory_cls = cls._factories.get(name)
        if factory_cls is None:
            raise ValueError(f"Unknown theme: {name!r}. "
                             f"Available: {list(cls._factories.keys())}")
        return factory_cls()

    @classmethod
    def available_themes(cls) -> list[str]:
        return list(cls._factories.keys())


# Register the built-in themes
ThemeRegistry.register("dark", DarkThemeFactory)
ThemeRegistry.register("light", LightThemeFactory)


# ─────────────────────────────────────────────────────
#  Demo
# ─────────────────────────────────────────────────────

def demo():
    print("=" * 60)
    print("  ABSTRACT FACTORY PATTERN DEMO")
    print("=" * 60)

    # --- Dark Theme ---
    print("\n1. Login Page — Dark Theme:")
    dark_page = LoginPage(DarkThemeFactory())
    print(dark_page.render())
    print(f"\n   Click: {dark_page.button.on_click()}")

    # --- Light Theme ---
    print("\n2. Login Page — Light Theme:")
    light_page = LoginPage(LightThemeFactory())
    print(light_page.render())
    print(f"\n   Click: {light_page.button.on_click()}")

    # --- Theme Registry ---
    print("\n3. Using Theme Registry:")
    print(f"   Available themes: {ThemeRegistry.available_themes()}")
    for theme_name in ThemeRegistry.available_themes():
        factory = ThemeRegistry.get_factory(theme_name)
        btn = factory.create_button()
        print(f"   {theme_name}: {btn.render()}")

    # --- Key insight ---
    print("\n💡 KEY INSIGHT:")
    print("   The LoginPage class never mentions DarkButton or LightInput.")
    print("   It works entirely through the UIFactory interface.")
    print("   To add a new theme, create new products + factory — zero")
    print("   changes to LoginPage needed!")


if __name__ == "__main__":
    demo()
