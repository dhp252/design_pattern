"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  COMBINATION: Strategy + Factory Method                                     ║
║  Real-World App: Payment Processing System                                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  How they combine:                                                          ║
║    • Factory Method selects WHICH payment strategy to create                ║
║    • Strategy defines HOW each payment method processes payments           ║
║                                                                             ║
║  Why together:                                                              ║
║    The client says "pay with credit card" → the Factory creates the        ║
║    right Strategy → the system processes the payment through the           ║
║    Strategy interface. Neither the client nor the core logic knows         ║
║    the implementation details.                                              ║
║                                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


# ═══════════════════════════════════════════════════════
#  Strategy: Payment processing algorithms
# ═══════════════════════════════════════════════════════

@dataclass
class PaymentResult:
    success: bool
    transaction_id: str
    message: str
    fee: float


class PaymentStrategy(ABC):
    """Strategy interface — each payment method implements this."""

    @abstractmethod
    def process(self, amount: float, currency: str = "USD") -> PaymentResult:
        pass

    @abstractmethod
    def validate(self, details: dict) -> bool:
        pass

    @abstractmethod
    def name(self) -> str:
        pass


class CreditCardPayment(PaymentStrategy):
    def __init__(self, card_number: str, expiry: str, cvv: str):
        self.card_number = card_number
        self.expiry = expiry
        self.cvv = cvv

    def process(self, amount: float, currency: str = "USD") -> PaymentResult:
        fee = amount * 0.029  # 2.9% processing fee
        return PaymentResult(
            success=True,
            transaction_id=f"CC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            message=f"💳 Charged ${amount:.2f} + ${fee:.2f} fee to card ending {self.card_number[-4:]}",
            fee=fee,
        )

    def validate(self, details: dict) -> bool:
        return len(self.card_number) >= 13 and len(self.cvv) == 3

    def name(self) -> str:
        return f"Credit Card (****{self.card_number[-4:]})"


class PayPalPayment(PaymentStrategy):
    def __init__(self, email: str):
        self.email = email

    def process(self, amount: float, currency: str = "USD") -> PaymentResult:
        fee = amount * 0.034 + 0.30  # 3.4% + $0.30
        return PaymentResult(
            success=True,
            transaction_id=f"PP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            message=f"🅿️  PayPal charged ${amount:.2f} + ${fee:.2f} fee to {self.email}",
            fee=fee,
        )

    def validate(self, details: dict) -> bool:
        return "@" in self.email

    def name(self) -> str:
        return f"PayPal ({self.email})"


class CryptoPayment(PaymentStrategy):
    def __init__(self, wallet_address: str, coin: str = "BTC"):
        self.wallet = wallet_address
        self.coin = coin

    def process(self, amount: float, currency: str = "USD") -> PaymentResult:
        fee = 1.50  # Flat network fee
        return PaymentResult(
            success=True,
            transaction_id=f"CRYPTO-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            message=f"₿ Sent ${amount:.2f} in {self.coin} + ${fee:.2f} network fee to {self.wallet[:8]}...",
            fee=fee,
        )

    def validate(self, details: dict) -> bool:
        return len(self.wallet) > 20

    def name(self) -> str:
        return f"Crypto ({self.coin}: {self.wallet[:8]}...)"


class BankTransferPayment(PaymentStrategy):
    def __init__(self, account: str, routing: str):
        self.account = account
        self.routing = routing

    def process(self, amount: float, currency: str = "USD") -> PaymentResult:
        fee = 0.25  # Minimal fee
        return PaymentResult(
            success=True,
            transaction_id=f"ACH-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            message=f"🏦 Bank transfer: ${amount:.2f} + ${fee:.2f} fee from account ****{self.account[-4:]}",
            fee=fee,
        )

    def validate(self, details: dict) -> bool:
        return len(self.account) >= 8 and len(self.routing) >= 9

    def name(self) -> str:
        return f"Bank Transfer (****{self.account[-4:]})"


# ═══════════════════════════════════════════════════════
#  Factory: Creates the right strategy based on input
# ═══════════════════════════════════════════════════════

class PaymentFactory:
    """
    Factory creates the correct PaymentStrategy based on
    the payment method and user-provided details.

    This decouples the checkout flow from knowing HOW to
    create each payment processor.
    """

    _registry: dict[str, type] = {
        "credit_card": CreditCardPayment,
        "paypal": PayPalPayment,
        "crypto": CryptoPayment,
        "bank_transfer": BankTransferPayment,
    }

    @classmethod
    def create(cls, method: str, details: dict) -> PaymentStrategy:
        creator = cls._registry.get(method)
        if creator is None:
            raise ValueError(f"Unknown payment method: {method!r}. "
                             f"Available: {list(cls._registry.keys())}")

        # Map details to constructor arguments
        if method == "credit_card":
            return creator(details["card_number"], details["expiry"], details["cvv"])
        elif method == "paypal":
            return creator(details["email"])
        elif method == "crypto":
            return creator(details["wallet"], details.get("coin", "BTC"))
        elif method == "bank_transfer":
            return creator(details["account"], details["routing"])
        raise ValueError(f"Unhandled method: {method}")

    @classmethod
    def available_methods(cls) -> list[str]:
        return list(cls._registry.keys())

    @classmethod
    def register(cls, method: str, strategy_cls: type):
        cls._registry[method] = strategy_cls


# ═══════════════════════════════════════════════════════
#  Checkout Service (uses both patterns)
# ═══════════════════════════════════════════════════════

@dataclass
class CartItem:
    name: str
    price: float
    quantity: int = 1


class CheckoutService:
    """
    The checkout service doesn't know about specific payment methods.
    It uses:
      1. Factory to create the right strategy
      2. Strategy to process the payment
    """

    def __init__(self):
        self._cart: list[CartItem] = []

    def add_item(self, item: CartItem):
        self._cart.append(item)

    def get_total(self) -> float:
        return sum(item.price * item.quantity for item in self._cart)

    def checkout(self, method: str, payment_details: dict) -> str:
        if not self._cart:
            return "❌ Cart is empty!"

        total = self.get_total()

        # FACTORY creates the strategy
        strategy = PaymentFactory.create(method, payment_details)

        # Validate
        if not strategy.validate(payment_details):
            return f"❌ Invalid payment details for {strategy.name()}"

        # STRATEGY processes the payment
        result = strategy.process(total)

        lines = [
            f"  🛒 Checkout Summary:",
            f"  {'─' * 40}",
        ]
        for item in self._cart:
            lines.append(f"    {item.name} × {item.quantity}: ${item.price * item.quantity:.2f}")
        lines.extend([
            f"  {'─' * 40}",
            f"    Subtotal:    ${total:.2f}",
            f"    Fee:         ${result.fee:.2f}",
            f"    Total:       ${total + result.fee:.2f}",
            f"    Method:      {strategy.name()}",
            f"    Transaction: {result.transaction_id}",
            f"    Status:      {'✅ Success' if result.success else '❌ Failed'}",
            f"    {result.message}",
        ])

        if result.success:
            self._cart.clear()

        return "\n".join(lines)


# ─────────────────────────────────────────────────────
#  Demo
# ─────────────────────────────────────────────────────

def demo():
    print("=" * 60)
    print("  STRATEGY + FACTORY COMBINATION DEMO")
    print("  Payment Processing System")
    print("=" * 60)

    print(f"\n  Available methods: {PaymentFactory.available_methods()}")

    # --- Purchase 1: Credit Card ---
    print(f"\n{'═' * 50}")
    checkout1 = CheckoutService()
    checkout1.add_item(CartItem("Python Book", 49.99))
    checkout1.add_item(CartItem("Keyboard", 129.99))
    checkout1.add_item(CartItem("Mouse Pad", 15.00, 2))
    print(checkout1.checkout("credit_card", {
        "card_number": "4111111111111234",
        "expiry": "12/25",
        "cvv": "123",
    }))

    # --- Purchase 2: PayPal ---
    print(f"\n{'═' * 50}")
    checkout2 = CheckoutService()
    checkout2.add_item(CartItem("Design Patterns Course", 199.00))
    print(checkout2.checkout("paypal", {
        "email": "buyer@example.com",
    }))

    # --- Purchase 3: Crypto ---
    print(f"\n{'═' * 50}")
    checkout3 = CheckoutService()
    checkout3.add_item(CartItem("VPN Annual Plan", 59.99))
    print(checkout3.checkout("crypto", {
        "wallet": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
        "coin": "ETH",
    }))

    # --- Fee comparison ---
    print(f"\n\n{'═' * 50}")
    print("  💡 Fee Comparison for $100 purchase:")
    print("  " + "─" * 40)
    test_methods = [
        ("credit_card", {"card_number": "4111111111111234", "expiry": "12/25", "cvv": "123"}),
        ("paypal", {"email": "test@test.com"}),
        ("crypto", {"wallet": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"}),
        ("bank_transfer", {"account": "12345678", "routing": "987654321"}),
    ]
    for method, details in test_methods:
        strategy = PaymentFactory.create(method, details)
        result = strategy.process(100.00)
        print(f"    {strategy.name():<35} Fee: ${result.fee:.2f}")

    print("\n\n💡 HOW THEY COMBINE:")
    print("   Factory decides WHICH strategy to create")
    print("   Strategy decides HOW to process the payment")
    print("   Checkout service knows NEITHER — just interface + factory call")


if __name__ == "__main__":
    demo()
