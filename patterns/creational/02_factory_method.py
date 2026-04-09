"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  FACTORY METHOD — Creational Pattern                                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  Intent:   Define an interface for creating an object, but let subclasses   ║
║            decide which class to instantiate.                               ║
║                                                                             ║
║  Problem:  Your code needs to create objects, but you don't know ahead     ║
║            of time what type of object you'll need. Hard-coding the         ║
║            class name makes the code rigid and hard to extend.             ║
║                                                                             ║
║  Solution: Replace direct construction calls with calls to a special       ║
║            factory method. Subclasses override the factory method to        ║
║            change the type of objects being created.                        ║
║                                                                             ║
║  Use When:                                                                  ║
║    • You don't know the exact types of objects your code will work with    ║
║    • You want to provide users a way to extend your library's components   ║
║    • You want to save system resources by reusing existing objects          ║
║                                                                             ║
║  Real-World Analogy:                                                        ║
║    A logistics company has trucks and ships. Instead of hard-coding         ║
║    "create a Truck", they use a factory that produces the right vehicle    ║
║    depending on the delivery type.                                          ║
║                                                                             ║
║  Python Bonus:                                                              ║
║    Python doesn't need abstract classes to do this — you can use a simple  ║
║    dictionary mapping or the __init_subclass__ hook to auto-register.      ║
║                                                                             ║
║  Related Patterns:                                                          ║
║    • Abstract Factory — often implemented with Factory Methods             ║
║    • Template Method — Factory Method is a specialization of it            ║
║    • Prototype — doesn't require subclassing, uses cloning instead         ║
║                                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from abc import ABC, abstractmethod


# ─────────────────────────────────────────────────────
#  Approach 1: Classic Factory Method (GoF style)
# ─────────────────────────────────────────────────────

class Notification(ABC):
    """Product interface — all notifications can send messages."""

    @abstractmethod
    def send(self, recipient: str, message: str) -> str:
        pass


class EmailNotification(Notification):
    def send(self, recipient: str, message: str) -> str:
        return f"📧 Email to {recipient}: {message}"


class SMSNotification(Notification):
    def send(self, recipient: str, message: str) -> str:
        return f"📱 SMS to {recipient}: {message}"


class PushNotification(Notification):
    def send(self, recipient: str, message: str) -> str:
        return f"🔔 Push to {recipient}: {message}"


class NotificationService(ABC):
    """
    Creator — declares the factory method that subclasses override.

    Note: The creator's primary responsibility isn't creating objects.
    It usually has core business logic that USES the products.
    """

    @abstractmethod
    def create_notification(self) -> Notification:
        """Factory method — subclasses decide which Notification to create."""
        pass

    def notify_user(self, recipient: str, message: str) -> str:
        """
        Business logic that uses the factory method.
        This method doesn't care WHICH notification type it gets.
        """
        notification = self.create_notification()
        return notification.send(recipient, message)


class EmailService(NotificationService):
    def create_notification(self) -> Notification:
        return EmailNotification()


class SMSService(NotificationService):
    def create_notification(self) -> Notification:
        return SMSNotification()


class PushService(NotificationService):
    def create_notification(self) -> Notification:
        return PushNotification()


# ─────────────────────────────────────────────────────
#  Approach 2: Pythonic — Dict-based factory
# ─────────────────────────────────────────────────────

class NotificationFactory:
    """
    A simple factory using a dictionary dispatch.
    No subclassing needed — just register and create.
    """
    _creators: dict[str, type[Notification]] = {
        "email": EmailNotification,
        "sms": SMSNotification,
        "push": PushNotification,
    }

    @classmethod
    def register(cls, channel: str, notification_cls: type[Notification]):
        """Register a new notification type at runtime."""
        cls._creators[channel] = notification_cls

    @classmethod
    def create(cls, channel: str) -> Notification:
        creator = cls._creators.get(channel)
        if creator is None:
            raise ValueError(f"Unknown channel: {channel!r}. "
                             f"Available: {list(cls._creators.keys())}")
        return creator()


# ─────────────────────────────────────────────────────
#  Approach 3: Auto-registration via __init_subclass__
# ─────────────────────────────────────────────────────

class AutoNotification(ABC):
    """
    Subclasses automatically register themselves!
    Just define the class and it's available.
    """
    _registry: dict[str, type[AutoNotification]] = {}

    def __init_subclass__(cls, channel: str = "", **kwargs):
        super().__init_subclass__(**kwargs)
        if channel:
            AutoNotification._registry[channel] = cls

    @classmethod
    def create(cls, channel: str) -> AutoNotification:
        klass = cls._registry.get(channel)
        if klass is None:
            raise ValueError(f"No notification registered for '{channel}'")
        return klass()

    @abstractmethod
    def send(self, recipient: str, message: str) -> str:
        pass


class SlackNotification(AutoNotification, channel="slack"):
    def send(self, recipient: str, message: str) -> str:
        return f"💬 Slack to #{recipient}: {message}"


class WebhookNotification(AutoNotification, channel="webhook"):
    def send(self, recipient: str, message: str) -> str:
        return f"🌐 Webhook to {recipient}: {message}"


# ═══════════════════════════════════════════════════════
#  REAL-WORLD SCENARIO: Cross-Platform Notification Sender
# ═══════════════════════════════════════════════════════

class NotificationDispatcher:
    """
    A dispatcher that sends notifications through multiple channels.
    It doesn't know or care what specific notification types exist.
    """

    def __init__(self):
        self._services: list[NotificationService] = []

    def add_service(self, service: NotificationService):
        self._services.append(service)

    def broadcast(self, recipient: str, message: str) -> list[str]:
        """Send a message through ALL registered services."""
        return [service.notify_user(recipient, message)
                for service in self._services]


# ─────────────────────────────────────────────────────
#  Demo
# ─────────────────────────────────────────────────────

def demo():
    print("=" * 60)
    print("  FACTORY METHOD PATTERN DEMO")
    print("=" * 60)

    # --- Classic Factory Method ---
    print("\n1. Classic Factory Method:")
    services: list[NotificationService] = [
        EmailService(),
        SMSService(),
        PushService(),
    ]
    for service in services:
        result = service.notify_user("alice@example.com", "Meeting at 3pm")
        print(f"   {result}")

    # --- Dict-based Factory ---
    print("\n2. Dict-based Factory (Pythonic):")
    for channel in ["email", "sms", "push"]:
        notification = NotificationFactory.create(channel)
        print(f"   {notification.send('bob@example.com', 'Deadline tomorrow')}")

    # Try adding a custom type at runtime
    class DiscordNotification(Notification):
        def send(self, recipient: str, message: str) -> str:
            return f"🎮 Discord to @{recipient}: {message}"

    NotificationFactory.register("discord", DiscordNotification)
    discord = NotificationFactory.create("discord")
    print(f"   {discord.send('gamers', 'Server maintenance at midnight')}")

    # --- Auto-registration ---
    print("\n3. Auto-Registration via __init_subclass__:")
    for channel in AutoNotification._registry:
        notif = AutoNotification.create(channel)
        print(f"   {notif.send('team-updates', 'Deploy v2.1 complete')}")

    # --- Real-world: Broadcast ---
    print("\n4. Broadcast Dispatcher (real-world scenario):")
    dispatcher = NotificationDispatcher()
    dispatcher.add_service(EmailService())
    dispatcher.add_service(SMSService())
    dispatcher.add_service(PushService())
    results = dispatcher.broadcast("ops-team", "🚨 Server CPU at 95%!")
    for r in results:
        print(f"   {r}")


if __name__ == "__main__":
    demo()
