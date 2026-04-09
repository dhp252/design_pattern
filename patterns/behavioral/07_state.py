"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  STATE — Behavioral Pattern                                                 ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  Intent:   Allow an object to alter its behavior when its internal state   ║
║            changes. The object will appear to change its class.            ║
║                                                                             ║
║  Problem:  An object behaves differently based on its state, leading to    ║
║            complex if/elif chains that grow with every new state.          ║
║                                                                             ║
║  Solution: Create a State class for each possible state. The context       ║
║            object delegates state-specific behavior to the current         ║
║            state object. State transitions change which state object       ║
║            is referenced.                                                   ║
║                                                                             ║
║  Use When:                                                                  ║
║    • Object behavior depends on its state and changes at runtime          ║
║    • Operations have large conditional logic based on state                ║
║    • You're implementing a finite state machine (FSM)                      ║
║                                                                             ║
║  Real-World Analogy:                                                        ║
║    A vending machine: its behavior (accept coin, dispense, show error)    ║
║    depends entirely on its current state (idle, has-money, dispensing).    ║
║                                                                             ║
║  Related Patterns:                                                          ║
║    • Strategy — same structure, but Strategy is chosen by client;         ║
║      State changes itself automatically based on transitions              ║
║    • Flyweight — states can be shared (they're often stateless)           ║
║    • Singleton — each state class is often a singleton                    ║
║                                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from abc import ABC, abstractmethod


# ═══════════════════════════════════════════════════════
#  State Interface
# ═══════════════════════════════════════════════════════

class VendingState(ABC):
    """
    Each state defines how the vending machine behaves
    when an action is performed.
    """

    @abstractmethod
    def insert_coin(self, machine: VendingMachine, amount: float) -> str:
        pass

    @abstractmethod
    def select_product(self, machine: VendingMachine, product: str) -> str:
        pass

    @abstractmethod
    def dispense(self, machine: VendingMachine) -> str:
        pass

    @abstractmethod
    def cancel(self, machine: VendingMachine) -> str:
        pass

    @abstractmethod
    def name(self) -> str:
        pass


# ═══════════════════════════════════════════════════════
#  Concrete States
# ═══════════════════════════════════════════════════════

class IdleState(VendingState):
    """Waiting for a coin. No money inserted yet."""

    def insert_coin(self, machine: VendingMachine, amount: float) -> str:
        machine.balance += amount
        machine.set_state(HasMoneyState())
        return f"💰 Inserted ${amount:.2f}. Balance: ${machine.balance:.2f}"

    def select_product(self, machine: VendingMachine, product: str) -> str:
        return "❌ Please insert coins first!"

    def dispense(self, machine: VendingMachine) -> str:
        return "❌ Insert coins and select a product first!"

    def cancel(self, machine: VendingMachine) -> str:
        return "Nothing to cancel."

    def name(self) -> str:
        return "IDLE"


class HasMoneyState(VendingState):
    """Money inserted, waiting for product selection."""

    def insert_coin(self, machine: VendingMachine, amount: float) -> str:
        machine.balance += amount
        return f"💰 Added ${amount:.2f}. Balance: ${machine.balance:.2f}"

    def select_product(self, machine: VendingMachine, product: str) -> str:
        price = machine.get_price(product)
        if price is None:
            return f"❌ Unknown product: {product}"

        stock = machine.get_stock(product)
        if stock <= 0:
            return f"❌ {product} is out of stock!"

        if machine.balance < price:
            return (f"❌ Insufficient funds for {product} (${price:.2f}). "
                    f"Balance: ${machine.balance:.2f}")

        machine.selected_product = product
        machine.set_state(DispensingState())
        return f"✅ Selected {product} (${price:.2f}). Dispensing..."

    def dispense(self, machine: VendingMachine) -> str:
        return "❌ Please select a product first!"

    def cancel(self, machine: VendingMachine) -> str:
        refund = machine.balance
        machine.balance = 0
        machine.set_state(IdleState())
        return f"💵 Refunded ${refund:.2f}. Transaction cancelled."

    def name(self) -> str:
        return "HAS_MONEY"


class DispensingState(VendingState):
    """Product selected, dispensing it."""

    def insert_coin(self, machine: VendingMachine, amount: float) -> str:
        return "⏳ Please wait, dispensing in progress..."

    def select_product(self, machine: VendingMachine, product: str) -> str:
        return "⏳ Please wait, dispensing in progress..."

    def dispense(self, machine: VendingMachine) -> str:
        product = machine.selected_product
        price = machine.get_price(product)

        # Deduct price and dispense
        machine.balance -= price
        machine.reduce_stock(product)
        change = machine.balance

        result = f"🎁 Dispensed: {product}!"
        if change > 0:
            result += f"\n  💵 Change: ${change:.2f}"
            machine.balance = 0

        machine.selected_product = None

        # Check if stock is depleted
        total_stock = sum(machine._stock.values())
        if total_stock == 0:
            machine.set_state(OutOfStockState())
            result += "\n  ⚠️  Machine is now out of stock!"
        else:
            machine.set_state(IdleState())

        return result

    def cancel(self, machine: VendingMachine) -> str:
        return "⏳ Cannot cancel — dispensing in progress!"

    def name(self) -> str:
        return "DISPENSING"


class OutOfStockState(VendingState):
    """Machine has no products left."""

    def insert_coin(self, machine: VendingMachine, amount: float) -> str:
        return "⚠️  Machine is out of stock. Coins not accepted."

    def select_product(self, machine: VendingMachine, product: str) -> str:
        return "⚠️  Machine is out of stock."

    def dispense(self, machine: VendingMachine) -> str:
        return "⚠️  Machine is out of stock."

    def cancel(self, machine: VendingMachine) -> str:
        return "⚠️  Machine is out of stock. Nothing to cancel."

    def name(self) -> str:
        return "OUT_OF_STOCK"


# ═══════════════════════════════════════════════════════
#  Context (the vending machine itself)
# ═══════════════════════════════════════════════════════

class VendingMachine:
    """
    CONTEXT — delegates behavior to its current State object.
    The machine doesn't have if/elif for each state.
    """

    def __init__(self):
        self._state: VendingState = IdleState()
        self.balance: float = 0
        self.selected_product: str | None = None
        self._products: dict[str, float] = {
            "Cola": 1.50,
            "Water": 1.00,
            "Chips": 2.00,
            "Candy": 0.75,
        }
        self._stock: dict[str, int] = {
            "Cola": 3,
            "Water": 5,
            "Chips": 2,
            "Candy": 1,
        }

    def set_state(self, state: VendingState):
        old = self._state.name()
        self._state = state
        print(f"  ⚙️  State: {old} → {state.name()}")

    # --- Delegated actions ---

    def insert_coin(self, amount: float) -> str:
        return self._state.insert_coin(self, amount)

    def select_product(self, product: str) -> str:
        return self._state.select_product(self, product)

    def dispense(self) -> str:
        return self._state.dispense(self)

    def cancel(self) -> str:
        return self._state.cancel(self)

    # --- Internal helpers ---

    def get_price(self, product: str) -> float | None:
        return self._products.get(product)

    def get_stock(self, product: str) -> int:
        return self._stock.get(product, 0)

    def reduce_stock(self, product: str):
        if product in self._stock:
            self._stock[product] -= 1

    def status(self) -> str:
        lines = [f"  🏧 Vending Machine | State: {self._state.name()} | Balance: ${self.balance:.2f}"]
        for product, price in self._products.items():
            stock = self._stock[product]
            indicator = "✅" if stock > 0 else "❌"
            lines.append(f"    {indicator} {product}: ${price:.2f} (stock: {stock})")
        return "\n".join(lines)


# ─────────────────────────────────────────────────────
#  Demo
# ─────────────────────────────────────────────────────

def demo():
    print("=" * 60)
    print("  STATE PATTERN DEMO")
    print("=" * 60)

    machine = VendingMachine()

    print("\n1. Initial status:")
    print(machine.status())

    # --- Normal purchase ---
    print("\n2. Normal Purchase:")
    print(f"  {machine.insert_coin(1.00)}")
    print(f"  {machine.insert_coin(1.00)}")
    print(f"  {machine.select_product('Cola')}")
    print(f"  {machine.dispense()}")

    # --- Try without money ---
    print("\n3. Try without money:")
    print(f"  {machine.select_product('Water')}")

    # --- Cancel ---
    print("\n4. Insert then cancel:")
    print(f"  {machine.insert_coin(2.00)}")
    print(f"  {machine.cancel()}")

    # --- Insufficient funds ---
    print("\n5. Insufficient funds:")
    print(f"  {machine.insert_coin(0.50)}")
    print(f"  {machine.select_product('Chips')}")  # Needs 2.00
    print(f"  {machine.insert_coin(1.50)}")
    print(f"  {machine.select_product('Chips')}")
    print(f"  {machine.dispense()}")

    # --- Current status ---
    print("\n6. Updated status:")
    print(machine.status())

    # --- Key comparison ---
    print("\n\n7. State vs If/Elif:")
    print("   WITHOUT State pattern:")
    print("     def insert_coin(amount):")
    print("       if self.state == 'idle':   ...")
    print("       elif self.state == 'has_money':  ...")
    print("       elif self.state == 'dispensing': ...")
    print("       elif self.state == 'out_of_stock': ...")
    print("   • Every method has this SAME switch — duplicated 4x!")
    print("   • Adding a new state means editing ALL methods.")
    print()
    print("   WITH State pattern:")
    print("   • Each state is a self-contained class.")
    print("   • Adding a new state = adding one new class.")
    print("   • No method needs to know about the other states.")

    print("\n💡 KEY INSIGHT:")
    print("   The State pattern replaces conditional logic with polymorphism.")
    print("   Each state is a class that handles ALL actions for that state.")
    print("   Transitions happen by swapping the state object.")


if __name__ == "__main__":
    demo()
