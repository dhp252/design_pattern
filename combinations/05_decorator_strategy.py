"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  COMBINATION: Decorator + Strategy                                          ║
║  Real-World App: API Middleware Pipeline                                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  How they combine:                                                          ║
║    • Strategy defines the CORE logic (interchangeable algorithms)          ║
║    • Decorator wraps the strategy with CROSS-CUTTING concerns              ║
║      (logging, caching, retry, metrics) without modifying it              ║
║                                                                             ║
║  Why together:                                                              ║
║    Strategy = WHAT to do (the algorithm).                                  ║
║    Decorator = HOW to enhance it (adding layers transparently).            ║
║                                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
import time
import functools


# ═══════════════════════════════════════════════════════
#  Strategy: Data processing algorithms
# ═══════════════════════════════════════════════════════

@dataclass
class ProcessingResult:
    data: str
    processing_time_ms: float = 0
    metadata: dict = None


class DataProcessor(ABC):
    """Strategy interface — defines the core processing algorithm."""

    @abstractmethod
    def process(self, input_data: str) -> ProcessingResult:
        pass

    @abstractmethod
    def name(self) -> str:
        pass


class JsonProcessor(DataProcessor):
    def process(self, input_data: str) -> ProcessingResult:
        # Simulate JSON processing
        result = input_data.upper()
        return ProcessingResult(data=f'{{"result": "{result}"}}')

    def name(self) -> str:
        return "JSON Processor"


class XmlProcessor(DataProcessor):
    def process(self, input_data: str) -> ProcessingResult:
        result = input_data.upper()
        return ProcessingResult(data=f"<result>{result}</result>")

    def name(self) -> str:
        return "XML Processor"


class CsvProcessor(DataProcessor):
    def process(self, input_data: str) -> ProcessingResult:
        words = input_data.split()
        return ProcessingResult(data=",".join(words))

    def name(self) -> str:
        return "CSV Processor"


# ═══════════════════════════════════════════════════════
#  Decorators: Cross-cutting concerns
# ═══════════════════════════════════════════════════════

class ProcessorDecorator(DataProcessor, ABC):
    """Base decorator — wraps a DataProcessor."""

    def __init__(self, processor: DataProcessor):
        self._wrapped = processor

    def name(self) -> str:
        return self._wrapped.name()


class LoggingDecorator(ProcessorDecorator):
    """Logs input/output of every processing call."""

    def process(self, input_data: str) -> ProcessingResult:
        print(f"    📝 [{self.name()}] Input:  {input_data[:50]}...")
        result = self._wrapped.process(input_data)
        print(f"    📝 [{self.name()}] Output: {result.data[:50]}...")
        return result

    def name(self) -> str:
        return f"{self._wrapped.name()} + Logging"


class TimingDecorator(ProcessorDecorator):
    """Measures and reports processing time."""

    def process(self, input_data: str) -> ProcessingResult:
        start = time.perf_counter()
        result = self._wrapped.process(input_data)
        elapsed_ms = (time.perf_counter() - start) * 1000
        result.processing_time_ms = elapsed_ms
        print(f"    ⏱️  [{self.name()}] Took {elapsed_ms:.2f}ms")
        return result

    def name(self) -> str:
        return f"{self._wrapped.name()} + Timing"


class CachingDecorator(ProcessorDecorator):
    """Caches results for repeated inputs."""

    def __init__(self, processor: DataProcessor):
        super().__init__(processor)
        self._cache: dict[str, ProcessingResult] = {}
        self.hits = 0
        self.misses = 0

    def process(self, input_data: str) -> ProcessingResult:
        if input_data in self._cache:
            self.hits += 1
            print(f"    ⚡ [{self.name()}] Cache HIT")
            return self._cache[input_data]
        self.misses += 1
        print(f"    ⚡ [{self.name()}] Cache MISS")
        result = self._wrapped.process(input_data)
        self._cache[input_data] = result
        return result

    def name(self) -> str:
        return f"{self._wrapped.name()} + Caching"


class ValidationDecorator(ProcessorDecorator):
    """Validates input before processing."""

    def __init__(self, processor: DataProcessor, max_length: int = 1000):
        super().__init__(processor)
        self._max_length = max_length

    def process(self, input_data: str) -> ProcessingResult:
        if not input_data or not input_data.strip():
            raise ValueError("Input data cannot be empty")
        if len(input_data) > self._max_length:
            raise ValueError(f"Input exceeds max length ({len(input_data)} > {self._max_length})")
        print(f"    ✅ [{self.name()}] Validation passed ({len(input_data)} chars)")
        return self._wrapped.process(input_data)

    def name(self) -> str:
        return f"{self._wrapped.name()} + Validation"


class RetryDecorator(ProcessorDecorator):
    """Retries on failure."""

    def __init__(self, processor: DataProcessor, max_retries: int = 3):
        super().__init__(processor)
        self._max_retries = max_retries

    def process(self, input_data: str) -> ProcessingResult:
        last_error = None
        for attempt in range(1, self._max_retries + 1):
            try:
                return self._wrapped.process(input_data)
            except Exception as e:
                last_error = e
                print(f"    🔄 [{self.name()}] Attempt {attempt}/{self._max_retries} failed: {e}")
        raise last_error

    def name(self) -> str:
        return f"{self._wrapped.name()} + Retry"


# ═══════════════════════════════════════════════════════
#  Pipeline builder (fluent API)
# ═══════════════════════════════════════════════════════

class PipelineBuilder:
    """Builds a decorated processor pipeline with a fluent API."""

    def __init__(self, base: DataProcessor):
        self._processor = base

    def with_logging(self) -> PipelineBuilder:
        self._processor = LoggingDecorator(self._processor)
        return self

    def with_timing(self) -> PipelineBuilder:
        self._processor = TimingDecorator(self._processor)
        return self

    def with_caching(self) -> PipelineBuilder:
        self._processor = CachingDecorator(self._processor)
        return self

    def with_validation(self, max_length: int = 1000) -> PipelineBuilder:
        self._processor = ValidationDecorator(self._processor, max_length)
        return self

    def with_retry(self, max_retries: int = 3) -> PipelineBuilder:
        self._processor = RetryDecorator(self._processor, max_retries)
        return self

    def build(self) -> DataProcessor:
        return self._processor


# ─────────────────────────────────────────────────────
#  Demo
# ─────────────────────────────────────────────────────

def demo():
    print("=" * 60)
    print("  DECORATOR + STRATEGY COMBINATION DEMO")
    print("  API Middleware Pipeline")
    print("=" * 60)

    # --- Different strategies ---
    print("\n1. Same decorators, different strategies:")
    for strategy in [JsonProcessor(), XmlProcessor(), CsvProcessor()]:
        pipeline = (PipelineBuilder(strategy)
                    .with_validation()
                    .with_timing()
                    .build())
        print(f"\n  Strategy: {strategy.name()}")
        result = pipeline.process("hello world from design patterns")
        print(f"  Result: {result.data}")

    # --- Stacking decorators ---
    print(f"\n{'═' * 50}")
    print("2. Full pipeline with all decorators:")
    full_pipeline = (PipelineBuilder(JsonProcessor())
                     .with_validation(max_length=500)
                     .with_caching()
                     .with_logging()
                     .with_timing()
                     .build())

    print("\n  First call (cache miss):")
    result1 = full_pipeline.process("test data")
    print(f"  Result: {result1.data}")

    print("\n  Second call (cache hit):")
    result2 = full_pipeline.process("test data")
    print(f"  Result: {result2.data}")

    # --- Validation failure ---
    print(f"\n{'═' * 50}")
    print("3. Validation decorator catches bad input:")
    try:
        full_pipeline.process("")
    except ValueError as e:
        print(f"  ❌ Caught: {e}")

    # --- Minimal vs maximal pipeline ---
    print(f"\n{'═' * 50}")
    print("4. Minimal vs Maximal pipeline:")

    minimal = JsonProcessor()
    maximal = (PipelineBuilder(JsonProcessor())
               .with_validation()
               .with_retry(max_retries=2)
               .with_caching()
               .with_logging()
               .with_timing()
               .build())

    print(f"\n  Minimal pipeline name: {minimal.name()}")
    print(f"  Maximal pipeline name: {maximal.name()}")

    print(f"\n  Minimal:")
    r1 = minimal.process("quick test")
    print(f"  → {r1.data}")

    print(f"\n  Maximal:")
    r2 = maximal.process("quick test")
    print(f"  → {r2.data}")

    print("\n💡 HOW THEY COMBINE:")
    print("   STRATEGY = the core algorithm (JSON, XML, CSV processing)")
    print("   DECORATOR = layers around it (logging, caching, validation)")
    print("   You can mix ANY strategy with ANY combination of decorators.")
    print("   The PipelineBuilder provides a clean fluent API for assembly.")


if __name__ == "__main__":
    demo()
