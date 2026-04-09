"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  FACADE — Structural Pattern                                                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  Intent:   Provide a simplified interface to a complex subsystem.          ║
║                                                                             ║
║  Problem:  A subsystem has many classes with complex interactions.          ║
║            Client code needs to understand too many details to use it.      ║
║                                                                             ║
║  Solution: Create a facade class that wraps the subsystem and exposes      ║
║            a few simple high-level methods. The subsystem still works      ║
║            behind the scenes, but clients only talk to the facade.         ║
║                                                                             ║
║  Use When:                                                                  ║
║    • You want a simple interface to a complex subsystem                    ║
║    • You want to layer your subsystem (facade for each layer)              ║
║    • You want to reduce coupling between client and subsystem              ║
║                                                                             ║
║  Real-World Analogy:                                                        ║
║    A universal remote for a home theater. One button press triggers        ║
║    the TV, sound system, streaming box, and dims the lights — you          ║
║    don't need to operate each device separately.                           ║
║                                                                             ║
║  Related Patterns:                                                          ║
║    • Adapter — wraps ONE object's interface; Facade wraps a SUBSYSTEM     ║
║    • Singleton — facade is often implemented as a singleton               ║
║    • Mediator — similar to facade but handles two-way communication       ║
║                                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass


# ═══════════════════════════════════════════════════════
#  Complex Subsystem Classes
# ═══════════════════════════════════════════════════════

class VideoProjector:
    """Manages the projector hardware."""

    def power_on(self) -> str:
        return "📽️  Projector: Warming up lamp... ON"

    def power_off(self) -> str:
        return "📽️  Projector: Cooling down... OFF"

    def set_input(self, source: str) -> str:
        return f"📽️  Projector: Input set to {source}"

    def set_aspect_ratio(self, ratio: str) -> str:
        return f"📽️  Projector: Aspect ratio → {ratio}"


class SurroundSoundSystem:
    """Manages the audio system."""

    def power_on(self) -> str:
        return "🔊 Audio: System powered ON"

    def power_off(self) -> str:
        return "🔊 Audio: System powered OFF"

    def set_volume(self, level: int) -> str:
        bars = "█" * (level // 10) + "░" * (10 - level // 10)
        return f"🔊 Audio: Volume [{bars}] {level}%"

    def set_mode(self, mode: str) -> str:
        return f"🔊 Audio: Mode → {mode}"

    def set_input(self, source: str) -> str:
        return f"🔊 Audio: Input → {source}"


class StreamingPlayer:
    """Manages the streaming device."""

    def power_on(self) -> str:
        return "📺 Streamer: Booting up... ON"

    def power_off(self) -> str:
        return "📺 Streamer: Shutting down... OFF"

    def connect_to_service(self, service: str) -> str:
        return f"📺 Streamer: Connected to {service}"

    def search(self, title: str) -> str:
        return f"📺 Streamer: Found '{title}' — ready to play"

    def play(self) -> str:
        return "📺 Streamer: ▶️  Playing..."

    def pause(self) -> str:
        return "📺 Streamer: ⏸️  Paused"

    def stop(self) -> str:
        return "📺 Streamer: ⏹️  Stopped"


class SmartLights:
    """Manages ambient lighting."""

    def set_brightness(self, level: int) -> str:
        return f"💡 Lights: Brightness → {level}%"

    def set_color(self, color: str) -> str:
        return f"💡 Lights: Color → {color}"

    def off(self) -> str:
        return "💡 Lights: OFF"

    def on(self) -> str:
        return "💡 Lights: ON"


class Thermostat:
    """Manages room temperature."""

    def set_temperature(self, celsius: float) -> str:
        return f"🌡️  Thermostat: Set to {celsius}°C"


# ═══════════════════════════════════════════════════════
#  The Facade
# ═══════════════════════════════════════════════════════

class HomeTheaterFacade:
    """
    THE FACADE — simplifies the complex home theater subsystem.

    Without this facade, starting a movie would require the client
    to know about ALL 5 subsystem classes and their initialization
    sequences. The facade encapsulates this complexity.
    """

    def __init__(self):
        # The facade owns all subsystem components
        self._projector = VideoProjector()
        self._audio = SurroundSoundSystem()
        self._streamer = StreamingPlayer()
        self._lights = SmartLights()
        self._thermostat = Thermostat()

    def watch_movie(self, title: str, service: str = "Netflix") -> list[str]:
        """One method to start an entire movie experience."""
        log = ["🎬 Starting Movie Night..."]
        log.append(self._thermostat.set_temperature(22))
        log.append(self._lights.set_brightness(15))
        log.append(self._lights.set_color("warm amber"))
        log.append(self._projector.power_on())
        log.append(self._projector.set_input("HDMI-1"))
        log.append(self._projector.set_aspect_ratio("16:9"))
        log.append(self._audio.power_on())
        log.append(self._audio.set_input("HDMI-ARC"))
        log.append(self._audio.set_mode("Surround 7.1"))
        log.append(self._audio.set_volume(60))
        log.append(self._streamer.power_on())
        log.append(self._streamer.connect_to_service(service))
        log.append(self._streamer.search(title))
        log.append(self._streamer.play())
        log.append("🎬 Enjoy the show! 🍿")
        return log

    def pause(self) -> list[str]:
        """Pause everything and bring lights up."""
        return [
            "⏸️  Pausing...",
            self._streamer.pause(),
            self._lights.set_brightness(50),
        ]

    def resume(self) -> list[str]:
        """Resume playback and dim lights."""
        return [
            "▶️  Resuming...",
            self._lights.set_brightness(15),
            self._streamer.play(),
        ]

    def end_movie(self) -> list[str]:
        """Shut everything down gracefully."""
        log = ["🎬 Ending Movie Night..."]
        log.append(self._streamer.stop())
        log.append(self._streamer.power_off())
        log.append(self._audio.power_off())
        log.append(self._projector.power_off())
        log.append(self._lights.set_brightness(100))
        log.append(self._lights.set_color("daylight"))
        log.append(self._thermostat.set_temperature(24))
        log.append("🎬 Good night! 🌙")
        return log

    def listen_to_music(self, genre: str = "Jazz") -> list[str]:
        """Another scenario — just music, no video."""
        return [
            f"🎵 Music Mode: {genre}",
            self._lights.set_brightness(40),
            self._lights.set_color("soft blue"),
            self._audio.power_on(),
            self._audio.set_mode("Stereo Hi-Fi"),
            self._audio.set_volume(45),
            f"🎵 Playing {genre} playlist...",
        ]


# ─────────────────────────────────────────────────────
#  Demo
# ─────────────────────────────────────────────────────

def demo():
    print("=" * 60)
    print("  FACADE PATTERN DEMO")
    print("=" * 60)

    theater = HomeTheaterFacade()

    # --- Watch a movie ---
    print("\n1. Watch Movie (one method call for 14 operations!):")
    for line in theater.watch_movie("Inception", "Netflix"):
        print(f"   {line}")

    # --- Pause ---
    print("\n2. Pause:")
    for line in theater.pause():
        print(f"   {line}")

    # --- Resume ---
    print("\n3. Resume:")
    for line in theater.resume():
        print(f"   {line}")

    # --- End ---
    print("\n4. End Movie:")
    for line in theater.end_movie():
        print(f"   {line}")

    # --- Music mode ---
    print("\n5. Music Mode:")
    for line in theater.listen_to_music("Lo-Fi Hip Hop"):
        print(f"   {line}")

    # --- Comparison ---
    print("\n6. Without Facade (client must do all this manually):")
    print("   projector = VideoProjector()")
    print("   audio = SurroundSoundSystem()")
    print("   streamer = StreamingPlayer()")
    print("   lights = SmartLights()")
    print("   thermostat = Thermostat()")
    print("   thermostat.set_temperature(22)")
    print("   lights.set_brightness(15)  ")
    print("   lights.set_color('warm amber')")
    print("   projector.power_on()")
    print("   projector.set_input('HDMI-1')")
    print("   ... (10+ more calls you need to remember!)")

    print("\n💡 KEY INSIGHT:")
    print("   The Facade doesn't prevent direct access to subsystems —")
    print("   it provides a convenient shortcut for common scenarios.")
    print("   Clients CAN still use subsystem classes directly if needed.")
    print("   Think of it as a 'convenience layer', not a restriction.")


if __name__ == "__main__":
    demo()
