"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  MEDIATOR — Behavioral Pattern                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  Intent:   Define an object that encapsulates how a set of objects          ║
║            interact. Reduce chaotic many-to-many dependencies by making    ║
║            components communicate only through the mediator.               ║
║                                                                             ║
║  Problem:  When multiple objects interact directly, they become tightly    ║
║            coupled. Adding a new participant requires modifying all the    ║
║            others. The dependency graph becomes "spaghetti."               ║
║                                                                             ║
║  Solution: Instead of direct communication, components send messages      ║
║            to a mediator, which routes them to the right recipients.       ║
║                                                                             ║
║  Use When:                                                                  ║
║    • Objects communicate in complex but well-defined ways                  ║
║    • Reusing a component is hard because it depends on many others         ║
║    • You want a centralized control point for component interactions       ║
║                                                                             ║
║  Real-World Analogy:                                                        ║
║    An air traffic control tower. Planes don't talk to each other —        ║
║    they all communicate through the tower, which coordinates landings     ║
║    and takeoffs.                                                            ║
║                                                                             ║
║  Related Patterns:                                                          ║
║    • Observer — mediator can use observer internally                      ║
║    • Facade — simplifies a subsystem one-way; Mediator is two-way        ║
║    • Command — requests to mediator can be Command objects                ║
║                                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass


# ═══════════════════════════════════════════════════════
#  Mediator Interface
# ═══════════════════════════════════════════════════════

class AirTrafficControl(ABC):
    """Mediator interface — the control tower."""

    @abstractmethod
    def notify(self, sender: Aircraft, event: str, data: dict = None):
        pass

    @abstractmethod
    def register(self, aircraft: Aircraft):
        pass


# ═══════════════════════════════════════════════════════
#  Colleague (Component)
# ═══════════════════════════════════════════════════════

class Aircraft:
    """
    A component that communicates ONLY through the mediator.
    It never talks to other Aircraft directly.
    """

    def __init__(self, call_sign: str, aircraft_type: str = "commercial"):
        self.call_sign = call_sign
        self.aircraft_type = aircraft_type
        self.altitude = 0
        self.runway: str | None = None
        self.status = "airborne"
        self._mediator: AirTrafficControl | None = None

    def set_mediator(self, mediator: AirTrafficControl):
        self._mediator = mediator

    def request_landing(self):
        print(f"  ✈️  {self.call_sign}: Requesting landing clearance")
        if self._mediator:
            self._mediator.notify(self, "request_landing")

    def request_takeoff(self):
        print(f"  ✈️  {self.call_sign}: Requesting takeoff clearance")
        if self._mediator:
            self._mediator.notify(self, "request_takeoff")

    def emergency(self):
        print(f"  🚨 {self.call_sign}: MAYDAY! Declaring emergency!")
        if self._mediator:
            self._mediator.notify(self, "emergency")

    def land(self, runway: str):
        self.runway = runway
        self.status = "landed"
        self.altitude = 0
        print(f"  ✈️  {self.call_sign}: Landing on runway {runway}")

    def takeoff(self, runway: str):
        self.runway = None
        self.status = "airborne"
        self.altitude = 10000
        print(f"  ✈️  {self.call_sign}: Taking off from runway {runway}")

    def hold(self, altitude: int):
        self.altitude = altitude
        self.status = "holding"
        print(f"  ✈️  {self.call_sign}: Holding at {altitude}ft")

    def __repr__(self):
        return f"{self.call_sign}({self.status})"


# ═══════════════════════════════════════════════════════
#  Concrete Mediator
# ═══════════════════════════════════════════════════════

class ControlTower(AirTrafficControl):
    """
    Concrete Mediator — coordinates all aircraft.

    Without the mediator, each aircraft would need to know
    about all other aircraft to avoid conflicts. With the
    mediator, they only know about the tower.
    """

    def __init__(self):
        self._aircraft: list[Aircraft] = []
        self._runways: dict[str, Aircraft | None] = {
            "28L": None,
            "28R": None,
            "10L": None,
        }
        self._holding_queue: list[Aircraft] = []

    def register(self, aircraft: Aircraft):
        aircraft.set_mediator(self)
        self._aircraft.append(aircraft)
        print(f"  🗼 Tower: Registered {aircraft.call_sign}")

    def notify(self, sender: Aircraft, event: str, data: dict = None):
        """The central coordination logic."""
        if event == "request_landing":
            self._handle_landing_request(sender)
        elif event == "request_takeoff":
            self._handle_takeoff_request(sender)
        elif event == "emergency":
            self._handle_emergency(sender)

    def _handle_landing_request(self, aircraft: Aircraft):
        # Find an available runway
        available = [rw for rw, occupant in self._runways.items()
                     if occupant is None]

        if available:
            runway = available[0]
            self._runways[runway] = aircraft
            print(f"  🗼 Tower: {aircraft.call_sign} cleared to land, runway {runway}")
            aircraft.land(runway)
        else:
            # No runway available — hold
            self._holding_queue.append(aircraft)
            print(f"  🗼 Tower: {aircraft.call_sign} — no runway available, enter holding pattern")
            aircraft.hold(5000 + len(self._holding_queue) * 1000)

    def _handle_takeoff_request(self, aircraft: Aircraft):
        # Find which runway the aircraft is on
        for runway, occupant in self._runways.items():
            if occupant is aircraft:
                self._runways[runway] = None
                print(f"  🗼 Tower: {aircraft.call_sign} cleared for takeoff, runway {runway}")
                aircraft.takeoff(runway)
                # Check waiting queue
                self._process_holding_queue()
                return
        print(f"  🗼 Tower: {aircraft.call_sign} — not on any runway!")

    def _handle_emergency(self, aircraft: Aircraft):
        # Emergency: clear a runway immediately
        print(f"  🗼 Tower: ⚠️ EMERGENCY — clearing runway for {aircraft.call_sign}")
        # Tell others to hold
        for other in self._aircraft:
            if other is not aircraft and other.status == "airborne":
                other.hold(8000)
        # Find or clear a runway
        for runway in self._runways:
            if self._runways[runway] is None:
                self._runways[runway] = aircraft
                aircraft.land(runway)
                return
        # Force clear first runway
        first_rw = list(self._runways.keys())[0]
        displaced = self._runways[first_rw]
        if displaced:
            displaced.hold(6000)
        self._runways[first_rw] = aircraft
        aircraft.land(first_rw)

    def _process_holding_queue(self):
        if self._holding_queue:
            next_aircraft = self._holding_queue.pop(0)
            print(f"  🗼 Tower: Processing waiting aircraft {next_aircraft.call_sign}")
            self._handle_landing_request(next_aircraft)

    def display_status(self):
        print(f"\n  🗼 === Airport Status ===")
        for runway, occupant in self._runways.items():
            status = occupant.call_sign if occupant else "EMPTY"
            print(f"     Runway {runway}: {status}")
        if self._holding_queue:
            names = [a.call_sign for a in self._holding_queue]
            print(f"     Holding: {', '.join(names)}")


# ─────────────────────────────────────────────────────
#  Demo
# ─────────────────────────────────────────────────────

def demo():
    print("=" * 60)
    print("  MEDIATOR PATTERN DEMO")
    print("=" * 60)

    tower = ControlTower()

    # Create aircraft
    planes = [
        Aircraft("AA-101", "commercial"),
        Aircraft("UA-202", "commercial"),
        Aircraft("DL-303", "commercial"),
        Aircraft("BA-404", "commercial"),
        Aircraft("MED-911", "medical"),
    ]

    print("\n1. Register aircraft:")
    for plane in planes:
        tower.register(plane)

    # --- Landing requests ---
    print("\n2. Landing requests (3 runways, 4 planes):")
    planes[0].request_landing()
    planes[1].request_landing()
    planes[2].request_landing()
    planes[3].request_landing()  # Will hold — all runways full!
    tower.display_status()

    # --- Takeoff frees a runway ---
    print("\n3. First plane takes off → waiting plane lands:")
    planes[0].request_takeoff()
    tower.display_status()

    # --- Emergency ---
    print("\n4. Medical emergency:")
    planes[4].emergency()
    tower.display_status()

    print("\n💡 KEY INSIGHT:")
    print("   Planes NEVER communicate with each other directly.")
    print("   The tower (mediator) handles ALL coordination logic.")
    print("   Adding a new plane type requires ZERO changes to existing planes.")
    print("   The complexity lives in the mediator, not scattered across components.")


if __name__ == "__main__":
    demo()
