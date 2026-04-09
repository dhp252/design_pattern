"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  COMMAND — Behavioral Pattern                                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  Intent:   Encapsulate a request as an object, thereby letting you         ║
║            parameterize, queue, log, and undo operations.                  ║
║                                                                             ║
║  Problem:  You need to decouple the object that invokes an operation       ║
║            from the object that performs it. You might also need undo,     ║
║            queuing, or logging of operations.                              ║
║                                                                             ║
║  Solution: Turn requests into stand-alone command objects with             ║
║            execute() and optionally undo() methods.                        ║
║                                                                             ║
║  Use When:                                                                  ║
║    • You need undo/redo functionality                                     ║
║    • You want to queue or schedule operations                              ║
║    • You need to log operations for audit or replay                        ║
║    • You want to parameterize actions (callbacks on steroids)              ║
║                                                                             ║
║  Real-World Analogy:                                                        ║
║    A restaurant order: the waiter writes it down (command object),         ║
║    passes it to the kitchen (receiver). The order can be modified,         ║
║    cancelled, or replayed.                                                  ║
║                                                                             ║
║  Related Patterns:                                                          ║
║    • Memento — store state for undo (Command + Memento = undo/redo)       ║
║    • Strategy — both encapsulate behavior, but Command focuses on          ║
║      requests while Strategy focuses on algorithms                         ║
║    • Chain of Responsibility — commands can be chained                    ║
║                                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


# ═══════════════════════════════════════════════════════
#  Command Interface
# ═══════════════════════════════════════════════════════

class Command(ABC):
    @abstractmethod
    def execute(self) -> str:
        pass

    @abstractmethod
    def undo(self) -> str:
        pass

    @abstractmethod
    def description(self) -> str:
        pass


# ═══════════════════════════════════════════════════════
#  Receiver (the smart home devices)
# ═══════════════════════════════════════════════════════

class Light:
    def __init__(self, room: str):
        self.room = room
        self.brightness = 0
        self.is_on = False

    def on(self, brightness: int = 100):
        self.is_on = True
        self.brightness = brightness

    def off(self):
        self.is_on = False
        self.brightness = 0

    def status(self) -> str:
        if self.is_on:
            bars = "█" * (self.brightness // 10) + "░" * (10 - self.brightness // 10)
            return f"💡 {self.room}: ON [{bars}] {self.brightness}%"
        return f"💡 {self.room}: OFF"


class Thermostat:
    def __init__(self):
        self.temperature = 22.0

    def set_temp(self, temp: float):
        self.temperature = temp

    def status(self) -> str:
        return f"🌡️  Thermostat: {self.temperature}°C"


class MusicPlayer:
    def __init__(self):
        self.playing = False
        self.track = ""
        self.volume = 50

    def play(self, track: str, volume: int = 50):
        self.playing = True
        self.track = track
        self.volume = volume

    def stop(self):
        self.playing = False

    def status(self) -> str:
        if self.playing:
            return f"🎵 Music: Playing '{self.track}' at {self.volume}%"
        return "🎵 Music: Stopped"


# ═══════════════════════════════════════════════════════
#  Concrete Commands
# ═══════════════════════════════════════════════════════

class LightOnCommand(Command):
    def __init__(self, light: Light, brightness: int = 100):
        self._light = light
        self._brightness = brightness
        self._prev_state: tuple[bool, int] = (False, 0)

    def execute(self) -> str:
        self._prev_state = (self._light.is_on, self._light.brightness)
        self._light.on(self._brightness)
        return self._light.status()

    def undo(self) -> str:
        was_on, prev_brightness = self._prev_state
        if was_on:
            self._light.on(prev_brightness)
        else:
            self._light.off()
        return f"↩️  Undo: {self._light.status()}"

    def description(self) -> str:
        return f"Turn on {self._light.room} light at {self._brightness}%"


class LightOffCommand(Command):
    def __init__(self, light: Light):
        self._light = light
        self._prev_state: tuple[bool, int] = (False, 0)

    def execute(self) -> str:
        self._prev_state = (self._light.is_on, self._light.brightness)
        self._light.off()
        return self._light.status()

    def undo(self) -> str:
        was_on, prev_brightness = self._prev_state
        if was_on:
            self._light.on(prev_brightness)
        else:
            self._light.off()
        return f"↩️  Undo: {self._light.status()}"

    def description(self) -> str:
        return f"Turn off {self._light.room} light"


class SetTemperatureCommand(Command):
    def __init__(self, thermostat: Thermostat, temperature: float):
        self._thermostat = thermostat
        self._target = temperature
        self._prev_temp = thermostat.temperature

    def execute(self) -> str:
        self._prev_temp = self._thermostat.temperature
        self._thermostat.set_temp(self._target)
        return self._thermostat.status()

    def undo(self) -> str:
        self._thermostat.set_temp(self._prev_temp)
        return f"↩️  Undo: {self._thermostat.status()}"

    def description(self) -> str:
        return f"Set thermostat to {self._target}°C"


class PlayMusicCommand(Command):
    def __init__(self, player: MusicPlayer, track: str, volume: int = 50):
        self._player = player
        self._track = track
        self._volume = volume
        self._was_playing = False
        self._prev_track = ""

    def execute(self) -> str:
        self._was_playing = self._player.playing
        self._prev_track = self._player.track
        self._player.play(self._track, self._volume)
        return self._player.status()

    def undo(self) -> str:
        if self._was_playing:
            self._player.play(self._prev_track)
        else:
            self._player.stop()
        return f"↩️  Undo: {self._player.status()}"

    def description(self) -> str:
        return f"Play '{self._track}' at {self._volume}%"


# ═══════════════════════════════════════════════════════
#  Macro Command (composite of commands)
# ═══════════════════════════════════════════════════════

class MacroCommand(Command):
    """Execute multiple commands as one unit."""

    def __init__(self, name: str, commands: list[Command]):
        self._name = name
        self._commands = commands

    def execute(self) -> str:
        results = [f"🏠 Macro '{self._name}':"]
        for cmd in self._commands:
            results.append(f"  → {cmd.execute()}")
        return "\n".join(results)

    def undo(self) -> str:
        results = [f"↩️  Undoing macro '{self._name}':"]
        for cmd in reversed(self._commands):
            results.append(f"  {cmd.undo()}")
        return "\n".join(results)

    def description(self) -> str:
        return f"Macro '{self._name}' ({len(self._commands)} commands)"


# ═══════════════════════════════════════════════════════
#  Invoker (the remote control)
# ═══════════════════════════════════════════════════════

class SmartHomeRemote:
    """
    The Invoker — accepts commands, executes them,
    and maintains a history for undo/redo.
    """

    def __init__(self):
        self._history: list[Command] = []
        self._undo_stack: list[Command] = []
        self._log: list[tuple[str, str, str]] = []

    def execute(self, command: Command) -> str:
        result = command.execute()
        self._history.append(command)
        self._undo_stack.clear()  # New action clears redo stack
        self._log.append((
            datetime.now().strftime("%H:%M:%S"),
            command.description(),
            "executed"
        ))
        return result

    def undo(self) -> str:
        if not self._history:
            return "Nothing to undo!"
        command = self._history.pop()
        self._undo_stack.append(command)
        result = command.undo()
        self._log.append((
            datetime.now().strftime("%H:%M:%S"),
            command.description(),
            "undone"
        ))
        return result

    def redo(self) -> str:
        if not self._undo_stack:
            return "Nothing to redo!"
        command = self._undo_stack.pop()
        self._history.append(command)
        result = command.execute()
        self._log.append((
            datetime.now().strftime("%H:%M:%S"),
            command.description(),
            "redone"
        ))
        return result

    def show_log(self) -> str:
        lines = ["📋 Command Log:"]
        for time_str, desc, action in self._log:
            lines.append(f"  [{time_str}] {desc} — {action}")
        return "\n".join(lines)


# ─────────────────────────────────────────────────────
#  Demo
# ─────────────────────────────────────────────────────

def demo():
    print("=" * 60)
    print("  COMMAND PATTERN DEMO")
    print("=" * 60)

    # Setup devices
    living_room_light = Light("Living Room")
    bedroom_light = Light("Bedroom")
    thermostat = Thermostat()
    music = MusicPlayer()

    # Setup remote
    remote = SmartHomeRemote()

    # --- Individual commands ---
    print("\n1. Individual Commands:")
    print(f"  {remote.execute(LightOnCommand(living_room_light, 75))}")
    print(f"  {remote.execute(SetTemperatureCommand(thermostat, 24))}")
    print(f"  {remote.execute(PlayMusicCommand(music, 'Chill Vibes', 40))}")

    # --- Undo ---
    print("\n2. Undo (reverse order):")
    print(f"  {remote.undo()}")
    print(f"  {remote.undo()}")

    # --- Redo ---
    print("\n3. Redo:")
    print(f"  {remote.redo()}")

    # --- Macro command ---
    print("\n4. Macro Command — 'Movie Night':")
    movie_night = MacroCommand("Movie Night", [
        LightOffCommand(living_room_light),
        LightOnCommand(bedroom_light, 20),
        SetTemperatureCommand(thermostat, 22),
        PlayMusicCommand(music, "Movie Soundtrack", 60),
    ])
    print(f"  {remote.execute(movie_night)}")

    # --- Undo entire macro ---
    print("\n5. Undo Macro:")
    print(f"  {remote.undo()}")

    # --- Show log ---
    print(f"\n6. {remote.show_log()}")

    print("\n💡 KEY INSIGHT:")
    print("   Commands turn operations into OBJECTS that can be:")
    print("     • Stored (history for undo/redo)")
    print("     • Queued (scheduled execution)")
    print("     • Composed (macro commands)")
    print("     • Logged (audit trail)")
    print("   The invoker never knows what device it's controlling!")


if __name__ == "__main__":
    demo()
