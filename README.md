# 🏗️ Design Patterns in Python

A comprehensive, hands-on repository for learning all **22 GoF (Gang of Four) design patterns** in Python — with real-world scenarios, Pythonic idioms, and pattern combination recipes.

> Every file is **self-contained and runnable**: `python patterns/creational/01_singleton.py`

---

## 📖 Quick Reference

### Creational Patterns — *How objects are created*

| # | Pattern | One-Line Description | Real-World Example | Related |
|---|---------|---------------------|--------------------|---------|
| 1 | [**Singleton**](patterns/creational/01_singleton.py) | Ensure only ONE instance exists | Database connection pool | Factory, Facade |
| 2 | [**Factory Method**](patterns/creational/02_factory_method.py) | Let subclasses decide what to create | Cross-platform notifications | Abstract Factory, Template |
| 3 | [**Abstract Factory**](patterns/creational/03_abstract_factory.py) | Create families of related objects | UI theme toolkit (Dark/Light) | Factory Method, Singleton |
| 4 | [**Builder**](patterns/creational/04_builder.py) | Build complex objects step by step | SQL query builder | Abstract Factory, Composite |
| 5 | [**Prototype**](patterns/creational/05_prototype.py) | Clone objects instead of building | Game entity spawner | Factory, Memento |

### Structural Patterns — *How objects are composed*

| # | Pattern | One-Line Description | Real-World Example | Related |
|---|---------|---------------------|--------------------|---------|
| 1 | [**Adapter**](patterns/structural/01_adapter.py) | Make incompatible interfaces work together | XML→JSON API converter | Bridge, Decorator, Facade |
| 2 | [**Bridge**](patterns/structural/02_bridge.py) | Split abstraction from implementation | Media player × Renderer | Adapter, Strategy |
| 3 | [**Composite**](patterns/structural/03_composite.py) | Tree structures with uniform interface | File system, org charts | Iterator, Visitor, Builder |
| 4 | [**Decorator**](patterns/structural/04_decorator.py) | Add behavior dynamically via wrapping | Coffee toppings, API middleware | Adapter, Composite, Proxy |
| 5 | [**Facade**](patterns/structural/05_facade.py) | Simple interface to complex subsystem | Home theater one-button start | Adapter, Singleton, Mediator |
| 6 | [**Flyweight**](patterns/structural/06_flyweight.py) | Share state to save memory | Game forest (10K trees, 4 types) | Singleton, Composite |
| 7 | [**Proxy**](patterns/structural/07_proxy.py) | Control access via a surrogate | Lazy-loading, access control, caching | Decorator, Adapter |

### Behavioral Patterns — *How objects communicate*

| # | Pattern | One-Line Description | Real-World Example | Related |
|---|---------|---------------------|--------------------|---------|
| 1 | [**Chain of Responsibility**](patterns/behavioral/01_chain_of_responsibility.py) | Pass request along a handler chain | HTTP middleware pipeline | Decorator, Command |
| 2 | [**Command**](patterns/behavioral/02_command.py) | Encapsulate requests as objects | Smart home remote with undo | Memento, Strategy |
| 3 | [**Iterator**](patterns/behavioral/03_iterator.py) | Traverse collections without exposing internals | Paginated API, tree traversal | Composite, Visitor |
| 4 | [**Mediator**](patterns/behavioral/04_mediator.py) | Centralize complex communication | Air traffic control tower | Observer, Facade |
| 5 | [**Memento**](patterns/behavioral/05_memento.py) | Save/restore object state | Game save system | Command, Prototype |
| 6 | [**Observer**](patterns/behavioral/06_observer.py) | Notify dependents of state changes | Stock ticker with displays | Mediator, Command |
| 7 | [**State**](patterns/behavioral/07_state.py) | Alter behavior when state changes | Vending machine FSM | Strategy, Flyweight |
| 8 | [**Strategy**](patterns/behavioral/08_strategy.py) | Swap algorithms at runtime | Route navigation strategies | State, Factory |
| 9 | [**Template Method**](patterns/behavioral/09_template_method.py) | Algorithm skeleton with customizable steps | Data mining pipeline | Strategy, Factory Method |
| 10 | [**Visitor**](patterns/behavioral/10_visitor.py) | Add operations without modifying classes | Document export (HTML/MD/Text) | Iterator, Composite |

---

## 🔗 Pattern Combinations

Real-world applications rarely use a single pattern. These mini-apps demonstrate how patterns synergize:

| # | Combination | Application | Key Insight |
|---|-------------|-------------|-------------|
| 1 | [**Strategy + Factory**](combinations/01_strategy_factory.py) | Payment processing | Factory selects *which* strategy; Strategy defines *how* |
| 2 | [**Command + Memento**](combinations/02_command_memento.py) | Text editor with undo/redo | Commands store mementos for state restoration |
| 3 | [**Observer + Mediator**](combinations/03_observer_mediator.py) | Event-driven dashboard | Mediator routes; Observer subscribes |
| 4 | [**Composite + Iterator**](combinations/04_composite_iterator.py) | File system browser | Same tree, different traversal strategies |
| 5 | [**Decorator + Strategy**](combinations/05_decorator_strategy.py) | API middleware pipeline | Strategy = core logic; Decorator = cross-cutting layers |
| 6 | [**Builder + Composite**](combinations/06_builder_composite.py) | HTML document builder | Builder makes tree construction readable |
| 7 | [**Factory + Observer + Strategy**](combinations/07_factory_observer_strategy.py) | Plugin system | Factory creates; Observer tracks lifecycle; Strategy executes |
| 8 | [**MVC (3 patterns)**](combinations/08_mvc_full_stack.py) | Todo app | Model(Observer) + View(Composite) + Controller(Strategy) |

---

## 🗺️ Pattern Relationship Map

```
                          ┌──────────────────────────────┐
                          │       CREATIONAL             │
                          │                              │
                          │  Singleton ←── Facade        │
                          │      ↕                       │
                          │  Factory Method              │
                          │      ↕                       │
                          │  Abstract Factory            │
                          │      ↕                       │
                          │  Builder ──→ Composite       │
                          │      ↕                       │
                          │  Prototype ──→ Memento       │
                          └──────────┬───────────────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
    ┌─────────▼──────────┐  ┌───────▼────────────┐  ┌──────▼───────────┐
    │    STRUCTURAL       │  │    BEHAVIORAL       │  │   COMBINATIONS   │
    │                     │  │                     │  │                  │
    │  Adapter            │  │  Chain of Resp.     │  │  Strategy        │
    │    ↕                │  │    ↕                │  │    + Factory     │
    │  Bridge             │  │  Command ──→ Memento│  │                  │
    │    ↕                │  │    ↕                │  │  Command         │
    │  Composite ←→ Iterator│  │  Iterator          │  │    + Memento     │
    │    ↕                │  │    ↕                │  │                  │
    │  Decorator          │  │  Mediator ←→ Observer│  │  Observer        │
    │    ↕                │  │    ↕                │  │    + Mediator     │
    │  Facade             │  │  State ←→ Strategy  │  │                  │
    │    ↕                │  │    ↕                │  │  Composite       │
    │  Flyweight          │  │  Template Method    │  │    + Iterator    │
    │    ↕                │  │    ↕                │  │                  │
    │  Proxy              │  │  Visitor            │  │  Decorator       │
    │                     │  │                     │  │    + Strategy    │
    └─────────────────────┘  └─────────────────────┘  │                  │
                                                       │  Builder        │
                                                       │    + Composite  │
                                                       │                  │
                                                       │  MVC (3-pattern │
                                                       │   architecture) │
                                                       └──────────────────┘
```

---

## 🤔 Which Pattern Should I Use?

```
Need to create objects?
├── One instance only?                    → Singleton
├── Don't know the exact type yet?        → Factory Method
├── Need a family of related objects?     → Abstract Factory
├── Object has many optional parts?       → Builder
└── Clone existing configured objects?    → Prototype

Need to structure/compose objects?
├── Incompatible interface?               → Adapter
├── Two independent dimensions of change? → Bridge
├── Tree/hierarchy with uniform ops?      → Composite
├── Add behavior without modifying?       → Decorator
├── Simplify a complex subsystem?         → Facade
├── Too many similar objects (memory)?    → Flyweight
└── Control access to an object?          → Proxy

Need to manage communication/behavior?
├── Request through a handler chain?      → Chain of Responsibility
├── Encapsulate operations (undo/queue)?  → Command
├── Traverse a collection uniformly?      → Iterator
├── Reduce many-to-many dependencies?     → Mediator
├── Save/restore object state?            → Memento
├── React to state changes (pub/sub)?     → Observer
├── Behavior changes based on state?      → State
├── Swap algorithms at runtime?           → Strategy
├── Algorithm skeleton + custom steps?    → Template Method
└── Add operations to a class hierarchy?  → Visitor
```

---

## 🚀 Getting Started

```bash
# Run any individual pattern
python patterns/creational/01_singleton.py
python patterns/structural/04_decorator.py
python patterns/behavioral/06_observer.py

# Run a pattern combination
python combinations/02_command_memento.py
python combinations/08_mvc_full_stack.py

# Run all patterns at once
for f in patterns/*/*.py; do [[ "$f" != *"__init__"* ]] && echo "=== $f ===" && python "$f"; done

# Open the interactive catalog
open catalog/index.html  # or: xdg-open catalog/index.html
```

---

## 📚 File Format

Every pattern file follows a consistent structure:

```python
"""
╔═══════════════════════════════════╗
║  PATTERN NAME — Category          ║
╠═══════════════════════════════════╣
║  Intent / Problem / Solution      ║
║  Use When / Analogy / Related     ║
╚═══════════════════════════════════╝
"""

# 1. Classic OOP implementation
# 2. Pythonic alternative (where applicable)
# 3. Real-world scenario demo

if __name__ == "__main__":
    demo()  # Run directly to see the pattern in action
```

---

## 📄 License

This is an educational repository. Use these patterns to build amazing things! 🎉
