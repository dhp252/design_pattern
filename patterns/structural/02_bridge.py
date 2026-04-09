"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  BRIDGE — Structural Pattern                                                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  Intent:   Decouple an abstraction from its implementation so that the     ║
║            two can vary independently.                                      ║
║                                                                             ║
║  Problem:  You have a class hierarchy that grows in TWO dimensions.         ║
║            E.g., Shape × Color → RedCircle, BlueCircle, RedSquare, etc.   ║
║            The number of classes explodes combinatorially.                  ║
║                                                                             ║
║  Solution: Split into two separate hierarchies (abstraction + impl)        ║
║            connected by a "bridge" (composition). Each hierarchy can       ║
║            evolve independently.                                            ║
║                                                                             ║
║  Use When:                                                                  ║
║    • A class has variations along multiple independent dimensions          ║
║    • You want to switch implementations at runtime                         ║
║    • Both abstraction and implementation should be extensible               ║
║                                                                             ║
║  Real-World Analogy:                                                        ║
║    A remote control (abstraction) works with different devices              ║
║    (implementation). A basic remote and an advanced remote both control     ║
║    a TV or a radio — 2 × 2 = 4 combos, but only 4 classes not 4.         ║
║                                                                             ║
║  vs Adapter:                                                                ║
║    Adapter is used AFTER the design to make incompatible things work.      ║
║    Bridge is designed UPFRONT to let abstraction and impl vary.            ║
║                                                                             ║
║  Related Patterns:                                                          ║
║    • Adapter — similar structure, but Bridge is designed proactively       ║
║    • Abstract Factory — can create platform-specific bridge impls          ║
║    • Strategy — Bridge is structural; Strategy is behavioral              ║
║                                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from abc import ABC, abstractmethod


# ═══════════════════════════════════════════════════════
#  Implementation Interface (one dimension)
# ═══════════════════════════════════════════════════════

class MediaRenderer(ABC):
    """
    The Implementation hierarchy.
    Different renderers know HOW to play media.
    """

    @abstractmethod
    def render_audio(self, filename: str) -> str:
        pass

    @abstractmethod
    def render_video(self, filename: str, resolution: str) -> str:
        pass

    @abstractmethod
    def name(self) -> str:
        pass


class DesktopRenderer(MediaRenderer):
    def render_audio(self, filename: str) -> str:
        return f"🖥️  Desktop: Playing {filename} via system audio driver"

    def render_video(self, filename: str, resolution: str) -> str:
        return f"🖥️  Desktop: Rendering {filename} at {resolution} (hardware accelerated)"

    def name(self) -> str:
        return "Desktop Renderer"


class MobileRenderer(MediaRenderer):
    def render_audio(self, filename: str) -> str:
        return f"📱 Mobile: Streaming {filename} (optimized for battery)"

    def render_video(self, filename: str, resolution: str) -> str:
        # Mobile might downscale
        mobile_res = "720p" if resolution in ("4K", "1080p") else resolution
        return f"📱 Mobile: Streaming {filename} at {mobile_res} (adaptive bitrate)"

    def name(self) -> str:
        return "Mobile Renderer"


class WebRenderer(MediaRenderer):
    def render_audio(self, filename: str) -> str:
        return f"🌐 Web: <audio src='{filename}'> via HTML5 Audio API"

    def render_video(self, filename: str, resolution: str) -> str:
        return f"🌐 Web: <video src='{filename}'> at {resolution} via HTML5 Video API"

    def name(self) -> str:
        return "Web Renderer"


# ═══════════════════════════════════════════════════════
#  Abstraction (the other dimension)
# ═══════════════════════════════════════════════════════

class MediaPlayer(ABC):
    """
    The Abstraction hierarchy.
    Different players define WHAT to play and control the experience.
    The 'renderer' field is the BRIDGE to the implementation.
    """

    def __init__(self, renderer: MediaRenderer):
        # This is the BRIDGE — composition, not inheritance
        self._renderer = renderer

    @abstractmethod
    def play(self, filename: str) -> str:
        pass

    @abstractmethod
    def description(self) -> str:
        pass


class AudioPlayer(MediaPlayer):
    """A simple audio player — plays music/podcasts."""

    def play(self, filename: str) -> str:
        return self._renderer.render_audio(filename)

    def description(self) -> str:
        return f"Audio Player ({self._renderer.name()})"


class VideoPlayer(MediaPlayer):
    """A video player with resolution settings."""

    def __init__(self, renderer: MediaRenderer, resolution: str = "1080p"):
        super().__init__(renderer)
        self._resolution = resolution

    def play(self, filename: str) -> str:
        return self._renderer.render_video(filename, self._resolution)

    def set_resolution(self, resolution: str):
        self._resolution = resolution

    def description(self) -> str:
        return f"Video Player @ {self._resolution} ({self._renderer.name()})"


class StreamingPlayer(MediaPlayer):
    """An advanced streaming player with playlist support."""

    def __init__(self, renderer: MediaRenderer):
        super().__init__(renderer)
        self._playlist: list[str] = []
        self._current_index = 0

    def add_to_playlist(self, *filenames: str):
        self._playlist.extend(filenames)

    def play(self, filename: str = "") -> str:
        if filename:
            return self._renderer.render_audio(filename)
        if not self._playlist:
            return "  Playlist is empty!"
        results = []
        for i, track in enumerate(self._playlist):
            prefix = "▶️ " if i == self._current_index else "  "
            results.append(f"{prefix}{self._renderer.render_audio(track)}")
        return "\n".join(results)

    def next_track(self):
        if self._playlist:
            self._current_index = (self._current_index + 1) % len(self._playlist)

    def description(self) -> str:
        return f"Streaming Player ({self._renderer.name()}) [{len(self._playlist)} tracks]"


# ═══════════════════════════════════════════════════════
#  Why Bridge matters — what WITHOUT Bridge looks like
# ═══════════════════════════════════════════════════════

# WITHOUT Bridge, you'd need:
#
#   DesktopAudioPlayer
#   DesktopVideoPlayer
#   DesktopStreamingPlayer
#   MobileAudioPlayer
#   MobileVideoPlayer
#   MobileStreamingPlayer
#   WebAudioPlayer
#   WebVideoPlayer
#   WebStreamingPlayer
#
# That's 3 × 3 = 9 classes! Adding a 4th renderer means 3 more classes.
#
# WITH Bridge: 3 players + 3 renderers = 6 classes, and they combine freely.
# Adding a 4th renderer means just 1 new class.


# ─────────────────────────────────────────────────────
#  Demo
# ─────────────────────────────────────────────────────

def demo():
    print("=" * 60)
    print("  BRIDGE PATTERN DEMO")
    print("=" * 60)

    renderers = [DesktopRenderer(), MobileRenderer(), WebRenderer()]

    # --- Audio player on all platforms ---
    print("\n1. Audio Player across platforms:")
    for renderer in renderers:
        player = AudioPlayer(renderer)
        print(f"  [{player.description()}]")
        print(f"    {player.play('bohemian_rhapsody.mp3')}")

    # --- Video player with different resolutions ---
    print("\n2. Video Player — Desktop vs Mobile at 4K:")
    desktop_video = VideoPlayer(DesktopRenderer(), "4K")
    mobile_video = VideoPlayer(MobileRenderer(), "4K")
    print(f"  {desktop_video.play('inception.mp4')}")
    print(f"  {mobile_video.play('inception.mp4')}")

    # --- Streaming player ---
    print("\n3. Streaming Player with playlist:")
    streamer = StreamingPlayer(WebRenderer())
    streamer.add_to_playlist("track1.mp3", "track2.mp3", "track3.mp3")
    print(f"  {streamer.description()}")
    print(streamer.play())
    print("\n  [Next track]")
    streamer.next_track()
    print(streamer.play())

    # --- Swap renderer at runtime ---
    print("\n4. Runtime renderer swap:")
    player = AudioPlayer(DesktopRenderer())
    print(f"  Before: {player.play('song.mp3')}")
    player._renderer = MobileRenderer()  # Swap implementation!
    print(f"  After:  {player.play('song.mp3')}")

    # --- Class count comparison ---
    print("\n5. Bridge vs No-Bridge class count:")
    n_abstractions = 3  # Audio, Video, Streaming
    n_implementations = 3  # Desktop, Mobile, Web
    print(f"  Without Bridge: {n_abstractions} × {n_implementations} = "
          f"{n_abstractions * n_implementations} classes")
    print(f"  With Bridge:    {n_abstractions} + {n_implementations} = "
          f"{n_abstractions + n_implementations} classes")
    print(f"  Adding 1 new renderer:")
    print(f"    Without Bridge: +{n_abstractions} classes")
    print(f"    With Bridge:    +1 class")

    print("\n💡 KEY INSIGHT:")
    print("   Bridge prevents combinatorial explosion by splitting a class")
    print("   hierarchy into TWO independent hierarchies connected by")
    print("   composition. Each side can be extended without affecting the other.")


if __name__ == "__main__":
    demo()
