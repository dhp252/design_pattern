"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  ADAPTER — Structural Pattern                                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  Intent:   Allow objects with incompatible interfaces to collaborate        ║
║            by wrapping one with a translator.                               ║
║                                                                             ║
║  Problem:  You need to use an existing class, but its interface doesn't    ║
║            match what your code expects. You can't modify the existing     ║
║            class (it's from a 3rd-party library or legacy code).           ║
║                                                                             ║
║  Solution: Create an adapter class that wraps the incompatible object      ║
║            and exposes the expected interface.                              ║
║                                                                             ║
║  Two Flavors:                                                               ║
║    • Object Adapter — uses composition (wraps the adaptee)                ║
║    • Class Adapter — uses multiple inheritance (Python supports this)      ║
║                                                                             ║
║  Use When:                                                                  ║
║    • You need to integrate a legacy/3rd-party class with new code          ║
║    • You want to create a reusable wrapper for format conversion           ║
║    • You're migrating from one API to another                              ║
║                                                                             ║
║  Real-World Analogy:                                                        ║
║    A power adapter lets you plug a US device into a European outlet.       ║
║    The adapter doesn't change the device or the outlet — it translates.   ║
║                                                                             ║
║  Related Patterns:                                                          ║
║    • Bridge — designed upfront for separation; Adapter is retrofitted      ║
║    • Decorator — same wrapping structure, but adds behavior (not changes)  ║
║    • Facade — defines a NEW simplified interface; Adapter reuses existing  ║
║    • Proxy — same interface; Adapter uses a DIFFERENT interface            ║
║                                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from abc import ABC, abstractmethod
import json


# ═══════════════════════════════════════════════════════
#  The Target Interface (what our code expects)
# ═══════════════════════════════════════════════════════

class DataSource(ABC):
    """Our application works with JSON-like data sources."""

    @abstractmethod
    def fetch(self, query: str) -> list[dict]:
        """Return data as a list of dictionaries."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Return the total number of records."""
        pass


# ═══════════════════════════════════════════════════════
#  Legacy/3rd-party classes with INCOMPATIBLE interfaces
# ═══════════════════════════════════════════════════════

class LegacyXMLService:
    """
    An old service that only speaks XML.
    We can't modify it (pretend it's a compiled library).
    """

    def __init__(self, data: list[dict]):
        self._data = data

    def xml_request(self, xpath: str) -> str:
        """Returns data as an XML string (incompatible with our DataSource!)."""
        items = [self._dict_to_xml(d) for d in self._data]
        return f"<results query='{xpath}'>\n" + "\n".join(items) + "\n</results>"

    def total_records(self) -> str:
        """Returns count as a string (not int!)."""
        return str(len(self._data))

    @staticmethod
    def _dict_to_xml(d: dict) -> str:
        fields = " ".join(f'{k}="{v}"' for k, v in d.items())
        return f"  <record {fields}/>"


class CSVFileReader:
    """
    A CSV reader that returns raw strings.
    Also incompatible with our DataSource interface.
    """

    def __init__(self, csv_content: str):
        lines = csv_content.strip().split("\n")
        self._headers = lines[0].split(",")
        self._rows = [line.split(",") for line in lines[1:]]

    def read_all(self) -> list[list[str]]:
        """Returns raw rows (list of lists, no dict keys)."""
        return self._rows

    def get_headers(self) -> list[str]:
        return self._headers

    def row_count(self) -> int:
        return len(self._rows)


# ═══════════════════════════════════════════════════════
#  Object Adapter (composition — RECOMMENDED)
# ═══════════════════════════════════════════════════════

class XMLToJSONAdapter(DataSource):
    """
    Adapts the LegacyXMLService to work as a DataSource.
    Uses COMPOSITION — wraps the adaptee as a private field.
    """

    def __init__(self, xml_service: LegacyXMLService):
        self._adaptee = xml_service

    def fetch(self, query: str) -> list[dict]:
        """
        Calls the XML service, then converts XML → dict list.
        In reality, you'd use an XML parser. We simulate it here.
        """
        # Get the raw XML
        xml = self._adaptee.xml_request(query)
        # Simple parse (simulation): extract record attributes
        records = []
        for line in xml.split("\n"):
            if "<record" in line:
                record = self._parse_record(line)
                records.append(record)
        return records

    def count(self) -> int:
        """Convert string count to int."""
        return int(self._adaptee.total_records())

    @staticmethod
    def _parse_record(xml_line: str) -> dict:
        """Simulate extracting key=value pairs from XML attributes."""
        import re
        pairs = re.findall(r'(\w+)="([^"]*)"', xml_line)
        return dict(pairs)


class CSVAdapter(DataSource):
    """Adapts CSVFileReader to work as a DataSource."""

    def __init__(self, csv_reader: CSVFileReader):
        self._adaptee = csv_reader

    def fetch(self, query: str) -> list[dict]:
        """Convert raw CSV rows into list of dicts using headers as keys."""
        headers = self._adaptee.get_headers()
        rows = self._adaptee.read_all()
        return [dict(zip(headers, row)) for row in rows]

    def count(self) -> int:
        return self._adaptee.row_count()


# ═══════════════════════════════════════════════════════
#  Class Adapter (multiple inheritance)
# ═══════════════════════════════════════════════════════

class CSVClassAdapter(CSVFileReader, DataSource):
    """
    Class Adapter: inherits from BOTH the adaptee and the target.
    Less common, but Python supports it via multiple inheritance.
    """

    def fetch(self, query: str) -> list[dict]:
        headers = self.get_headers()
        rows = self.read_all()
        return [dict(zip(headers, row)) for row in rows]

    def count(self) -> int:
        return self.row_count()


# ═══════════════════════════════════════════════════════
#  Client Code — works with any DataSource
# ═══════════════════════════════════════════════════════

class DataAnalyzer:
    """
    Client code that only knows about the DataSource interface.
    Doesn't know or care whether the data comes from XML, CSV, or JSON.
    """

    def __init__(self, source: DataSource):
        self._source = source

    def summary(self, query: str = "*") -> str:
        records = self._source.fetch(query)
        count = self._source.count()
        if records:
            fields = list(records[0].keys())
            sample = json.dumps(records[0], indent=2)
        else:
            fields = []
            sample = "{}"
        return (f"  Records: {count}\n"
                f"  Fields:  {fields}\n"
                f"  Sample:\n{self._indent(sample, 4)}")

    @staticmethod
    def _indent(text: str, spaces: int) -> str:
        prefix = " " * spaces
        return "\n".join(prefix + line for line in text.split("\n"))


# ─────────────────────────────────────────────────────
#  Demo
# ─────────────────────────────────────────────────────

def demo():
    print("=" * 60)
    print("  ADAPTER PATTERN DEMO")
    print("=" * 60)

    # --- Legacy XML service ---
    xml_data = [
        {"id": "1", "name": "Alice", "role": "Engineer"},
        {"id": "2", "name": "Bob", "role": "Designer"},
        {"id": "3", "name": "Charlie", "role": "Manager"},
    ]
    xml_service = LegacyXMLService(xml_data)

    print("\n1. Raw XML service (incompatible):")
    print(f"  {xml_service.xml_request('/users')[:80]}...")

    print("\n2. XML → JSON Adapter (object adapter):")
    adapted_xml = XMLToJSONAdapter(xml_service)
    analyzer = DataAnalyzer(adapted_xml)
    print(analyzer.summary())

    # --- CSV reader ---
    csv_content = "id,name,department,salary\n1,Dana,Engineering,95000\n2,Eve,Marketing,72000\n3,Frank,Sales,68000"

    print("\n3. CSV Adapter (object adapter):")
    csv_reader = CSVFileReader(csv_content)
    adapted_csv = CSVAdapter(csv_reader)
    analyzer2 = DataAnalyzer(adapted_csv)
    print(analyzer2.summary())

    print("\n4. CSV Class Adapter (multiple inheritance):")
    class_adapted = CSVClassAdapter(csv_content)
    analyzer3 = DataAnalyzer(class_adapted)
    print(analyzer3.summary())

    print("\n💡 KEY INSIGHT:")
    print("   The DataAnalyzer works with ANY data source — XML, CSV, JSON —")
    print("   as long as it's wrapped in an adapter that speaks DataSource.")
    print("   Object adapters (composition) are preferred over class adapters")
    print("   because they're more flexible and don't create tight coupling.")


if __name__ == "__main__":
    demo()
