"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  TEMPLATE METHOD — Behavioral Pattern                                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  Intent:   Define the skeleton of an algorithm in a base class, letting    ║
║            subclasses override specific steps without changing the          ║
║            algorithm's structure.                                           ║
║                                                                             ║
║  Problem:  Several classes implement nearly the same algorithm with        ║
║            minor variations. Code is duplicated across classes.             ║
║                                                                             ║
║  Solution: Put the common algorithm structure in a base class "template    ║
║            method" and let subclasses provide the varying steps.           ║
║                                                                             ║
║  Use When:                                                                  ║
║    • Several classes have similar algorithms with slight differences       ║
║    • You want to control the extension points of an algorithm              ║
║    • You have duplicate code across subclasses that differs in details     ║
║                                                                             ║
║  Real-World Analogy:                                                        ║
║    A recipe template: "1. Prepare ingredients → 2. Cook → 3. Serve."     ║
║    Different dishes override each step but follow the same structure.      ║
║                                                                             ║
║  vs Strategy:                                                               ║
║    Template Method uses INHERITANCE — subclass overrides steps.            ║
║    Strategy uses COMPOSITION — swap the algorithm object.                  ║
║                                                                             ║
║  Related Patterns:                                                          ║
║    • Strategy — composition-based alternative                              ║
║    • Factory Method — a specialization of Template Method                 ║
║    • Hook Method — optional steps that subclasses CAN override            ║
║                                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
import time


# ═══════════════════════════════════════════════════════
#  The Template Method
# ═══════════════════════════════════════════════════════

@dataclass
class DataRecord:
    source: str
    raw: str
    cleaned: str = ""
    analyzed: dict = None
    report: str = ""


class DataMiningPipeline(ABC):
    """
    The Template Method: mine() defines the algorithm skeleton.
    Subclasses override specific steps.
    """

    def mine(self, source: str) -> DataRecord:
        """
        THE TEMPLATE METHOD — defines the algorithm structure.
        This method is FINAL (should not be overridden).
        """
        record = DataRecord(source=source, raw="")

        # Step 1: Extract raw data (varies by source type)
        print(f"  📥 Extracting from {source}...")
        record.raw = self.extract(source)

        # Step 2: Transform/clean the data
        print(f"  🔧 Transforming...")
        record.cleaned = self.transform(record.raw)

        # Step 3: Analyze (varies by analysis type)
        print(f"  📊 Analyzing...")
        record.analyzed = self.analyze(record.cleaned)

        # Step 4: Generate report
        print(f"  📝 Generating report...")
        record.report = self.generate_report(record.analyzed)

        # Hook: Optional post-processing
        self.on_complete(record)

        return record

    # --- Abstract steps (MUST be overridden) ---

    @abstractmethod
    def extract(self, source: str) -> str:
        """Step 1: Extract raw data from the source."""
        pass

    @abstractmethod
    def analyze(self, data: str) -> dict:
        """Step 3: Perform analysis on cleaned data."""
        pass

    # --- Concrete steps (CAN be overridden) ---

    def transform(self, raw_data: str) -> str:
        """Step 2: Default transformation — lowercase & strip."""
        return raw_data.lower().strip()

    def generate_report(self, analysis: dict) -> str:
        """Step 4: Default report generation."""
        lines = ["  ── Report ──"]
        for key, value in analysis.items():
            lines.append(f"    {key}: {value}")
        return "\n".join(lines)

    # --- Hook (optional, does nothing by default) ---

    def on_complete(self, record: DataRecord):
        """Hook: subclasses can optionally override for post-processing."""
        pass


# ═══════════════════════════════════════════════════════
#  Concrete Implementations
# ═══════════════════════════════════════════════════════

class CSVDataMiner(DataMiningPipeline):
    """Mines data from CSV files."""

    def extract(self, source: str) -> str:
        # Simulate reading a CSV file
        return "Name,Age,City\nAlice,30,NYC\nBob,25,LA\nCharlie,35,Chicago\nDiana,28,Seattle"

    def analyze(self, data: str) -> dict:
        lines = data.strip().split("\n")
        rows = [line.split(",") for line in lines[1:]]  # Skip header
        ages = [int(row[1]) for row in rows if len(row) > 1 and row[1].isdigit()]
        cities = [row[2] for row in rows if len(row) > 2]
        return {
            "total_records": len(rows),
            "avg_age": sum(ages) / len(ages) if ages else 0,
            "cities": list(set(cities)),
            "source_type": "CSV",
        }


class APIDataMiner(DataMiningPipeline):
    """Mines data from API endpoints."""

    def extract(self, source: str) -> str:
        # Simulate API response
        return '{"users": [{"name": "Eve", "score": 92}, {"name": "Frank", "score": 87}, {"name": "Grace", "score": 95}]}'

    def transform(self, raw_data: str) -> str:
        """Override: API data needs JSON parsing, not just lowercase."""
        # In reality, parse JSON. Here we simulate.
        return raw_data.replace('"', '').replace('{', '').replace('}', '')

    def analyze(self, data: str) -> dict:
        # Simple analysis of the "parsed" API data
        scores = []
        import re
        for match in re.finditer(r'score:\s*(\d+)', data):
            scores.append(int(match.group(1)))
        return {
            "total_records": len(scores),
            "avg_score": sum(scores) / len(scores) if scores else 0,
            "max_score": max(scores) if scores else 0,
            "min_score": min(scores) if scores else 0,
            "source_type": "API",
        }

    def on_complete(self, record: DataRecord):
        """Hook: Log API access for auditing."""
        print(f"  📋 Hook: Logged API access to {record.source}")


class LogDataMiner(DataMiningPipeline):
    """Mines data from server log files."""

    def extract(self, source: str) -> str:
        # Simulate log file
        return """[INFO] 2024-01-15 10:00:01 GET /api/users 200 45ms
[WARN] 2024-01-15 10:00:02 POST /api/upload 413 120ms
[ERROR] 2024-01-15 10:00:03 GET /api/data 500 2ms
[INFO] 2024-01-15 10:00:04 GET /api/users 200 38ms
[INFO] 2024-01-15 10:00:05 DELETE /api/users/1 204 15ms
[ERROR] 2024-01-15 10:00:06 POST /api/auth 401 5ms"""

    def analyze(self, data: str) -> dict:
        lines = data.strip().split("\n")
        levels = {"info": 0, "warn": 0, "error": 0}
        status_codes = []
        response_times = []
        import re
        for line in lines:
            for level in levels:
                if f"[{level}]" in line:
                    levels[level] += 1
            # Extract status codes and times
            code_match = re.search(r'\s(\d{3})\s', line)
            time_match = re.search(r'(\d+)ms', line)
            if code_match:
                status_codes.append(int(code_match.group(1)))
            if time_match:
                response_times.append(int(time_match.group(1)))

        return {
            "total_entries": len(lines),
            "by_level": levels,
            "error_rate": f"{levels['error'] / len(lines) * 100:.0f}%",
            "avg_response_ms": sum(response_times) / len(response_times) if response_times else 0,
            "source_type": "Log File",
        }

    def generate_report(self, analysis: dict) -> str:
        """Override: Custom report format for logs."""
        return (f"  ── Log Analysis Report ──\n"
                f"    Entries: {analysis['total_entries']}\n"
                f"    Levels: {analysis['by_level']}\n"
                f"    Error Rate: {analysis['error_rate']}\n"
                f"    Avg Response: {analysis['avg_response_ms']:.0f}ms")


# ─────────────────────────────────────────────────────
#  Demo
# ─────────────────────────────────────────────────────

def demo():
    print("=" * 60)
    print("  TEMPLATE METHOD PATTERN DEMO")
    print("=" * 60)

    miners = [
        ("CSV File", CSVDataMiner()),
        ("REST API", APIDataMiner()),
        ("Log File", LogDataMiner()),
    ]

    for name, miner in miners:
        print(f"\n{'─' * 40}")
        print(f"  Mining: {name}")
        print(f"{'─' * 40}")
        record = miner.mine(f"source_{name.lower().replace(' ', '_')}")
        print(record.report)

    print(f"\n\n📐 Algorithm structure (same for all):")
    print("   mine()")
    print("     ├── extract()        ← varies by source")
    print("     ├── transform()      ← has default, can override")
    print("     ├── analyze()        ← varies by data type")
    print("     ├── generate_report()← has default, can override")
    print("     └── on_complete()    ← hook (optional)")

    print("\n💡 KEY INSIGHT:")
    print("   The TEMPLATE METHOD (mine) is in the base class — untouched.")
    print("   Subclasses customize SPECIFIC STEPS without changing the flow.")
    print("   Template Method = inheritance-based algorithm customization.")
    print("   Strategy = composition-based algorithm swap.")


if __name__ == "__main__":
    demo()
