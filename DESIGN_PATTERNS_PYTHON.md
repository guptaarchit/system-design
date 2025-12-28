# Design Patterns in Python - Interview Guide

## Table of Contents
1. [Creational Patterns](#creational-patterns)
   - [Singleton Pattern](#singleton-pattern)
   - [Factory Pattern](#factory-pattern)
   - [Builder Pattern](#builder-pattern)
   - [Prototype Pattern](#prototype-pattern)
2. [Structural Patterns](#structural-patterns)
   - [Adapter Pattern](#adapter-pattern)
   - [Decorator Pattern](#decorator-pattern)
   - [Facade Pattern](#facade-pattern)
   - [Proxy Pattern](#proxy-pattern)
   - [Composite Pattern](#composite-pattern)
3. [Behavioral Patterns](#behavioral-patterns)
   - [Observer Pattern](#observer-pattern)
   - [Strategy Pattern](#strategy-pattern)
   - [Command Pattern](#command-pattern)
   - [Chain of Responsibility](#chain-of-responsibility)
   - [State Pattern](#state-pattern)
   - [Template Method Pattern](#template-method-pattern)
4. [Python-Specific Patterns](#python-specific-patterns)
   - [Context Manager Pattern](#context-manager-pattern)
   - [Generator Pattern](#generator-pattern)
   - [Descriptor Pattern](#descriptor-pattern)
5. [Interview Questions & Answers](#interview-questions--answers)

---

## Creational Patterns

### Singleton Pattern

**Intent**: Ensure a class has only one instance and provide a global point of access to it.

**Use Case**: Database connections, logging, configuration management.

**Python Implementation**:

```python
class Singleton:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

# Usage
s1 = Singleton()
s2 = Singleton()
print(s1 is s2)  # True

# Alternative: Decorator approach
def singleton(cls):
    instances = {}
    lock = threading.Lock()
    
    def get_instance(*args, **kwargs):
        if cls not in instances:
            with lock:
                if cls not in instances:
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
class DatabaseConnection:
    def __init__(self):
        self.connection = "Connected to DB"
```

**Interview Points**:
- Thread-safe implementation
- Lazy initialization
- Memory efficiency

---

### Factory Pattern

**Intent**: Create objects without specifying the exact class of object that will be created.

**Use Case**: Creating different types of payment processors, file parsers, UI components.

**Python Implementation**:

```python
from abc import ABC, abstractmethod

# Product interface
class PaymentProcessor(ABC):
    @abstractmethod
    def process_payment(self, amount: float) -> bool:
        pass

# Concrete products
class CreditCardProcessor(PaymentProcessor):
    def process_payment(self, amount: float) -> bool:
        print(f"Processing ${amount} via Credit Card")
        return True

class PayPalProcessor(PaymentProcessor):
    def process_payment(self, amount: float) -> bool:
        print(f"Processing ${amount} via PayPal")
        return True

class CryptoProcessor(PaymentProcessor):
    def process_payment(self, amount: float) -> bool:
        print(f"Processing ${amount} via Crypto")
        return True

# Factory
class PaymentProcessorFactory:
    @staticmethod
    def create_processor(payment_type: str) -> PaymentProcessor:
        processors = {
            "credit_card": CreditCardProcessor,
            "paypal": PayPalProcessor,
            "crypto": CryptoProcessor
        }
        
        processor_class = processors.get(payment_type)
        if not processor_class:
            raise ValueError(f"Unknown payment type: {payment_type}")
        
        return processor_class()

# Usage
factory = PaymentProcessorFactory()
processor = factory.create_processor("credit_card")
processor.process_payment(100.0)

# Factory Method Pattern (more flexible)
class PaymentProcessorFactory(ABC):
    @abstractmethod
    def create_processor(self) -> PaymentProcessor:
        pass
    
    def process(self, amount: float) -> bool:
        processor = self.create_processor()
        return processor.process_payment(amount)

class CreditCardFactory(PaymentProcessorFactory):
    def create_processor(self) -> PaymentProcessor:
        return CreditCardProcessor()
```

**Interview Points**:
- Decouples object creation from usage
- Open/Closed Principle
- Easy to extend with new types

---

### Builder Pattern

**Intent**: Construct complex objects step by step.

**Use Case**: Building SQL queries, HTTP requests, configuration objects.

**Python Implementation**:

```python
class QueryBuilder:
    def __init__(self):
        self.query = {
            "select": [],
            "from": None,
            "where": [],
            "join": [],
            "order_by": None,
            "limit": None
        }
    
    def select(self, *columns):
        self.query["select"].extend(columns)
        return self
    
    def from_table(self, table: str):
        self.query["from"] = table
        return self
    
    def where(self, condition: str):
        self.query["where"].append(condition)
        return self
    
    def join(self, table: str, condition: str):
        self.query["join"].append(f"JOIN {table} ON {condition}")
        return self
    
    def order_by(self, column: str, direction: str = "ASC"):
        self.query["order_by"] = f"{column} {direction}"
        return self
    
    def limit(self, count: int):
        self.query["limit"] = count
        return self
    
    def build(self) -> str:
        parts = []
        
        # SELECT
        if self.query["select"]:
            parts.append(f"SELECT {', '.join(self.query['select'])}")
        else:
            parts.append("SELECT *")
        
        # FROM
        if self.query["from"]:
            parts.append(f"FROM {self.query['from']}")
        
        # JOIN
        if self.query["join"]:
            parts.extend(self.query["join"])
        
        # WHERE
        if self.query["where"]:
            parts.append(f"WHERE {' AND '.join(self.query['where'])}")
        
        # ORDER BY
        if self.query["order_by"]:
            parts.append(f"ORDER BY {self.query['order_by']}")
        
        # LIMIT
        if self.query["limit"]:
            parts.append(f"LIMIT {self.query['limit']}")
        
        return " ".join(parts)

# Usage
query = (QueryBuilder()
    .select("id", "name", "email")
    .from_table("users")
    .where("age > 18")
    .where("status = 'active'")
    .order_by("created_at", "DESC")
    .limit(10)
    .build())

print(query)
# SELECT id, name, email FROM users WHERE age > 18 AND status = 'active' ORDER BY created_at DESC LIMIT 10
```

**Interview Points**:
- Fluent interface (method chaining)
- Immutable construction
- Complex object creation made simple

---

### Prototype Pattern

**Intent**: Create objects by cloning an existing object (prototype).

**Use Case**: Expensive object creation, configuration templates.

**Python Implementation**:

```python
import copy
from abc import ABC, abstractmethod

class Prototype(ABC):
    @abstractmethod
    def clone(self):
        pass

class Document(Prototype):
    def __init__(self, title: str, content: str, metadata: dict):
        self.title = title
        self.content = content
        self.metadata = metadata
    
    def clone(self):
        # Deep copy to avoid shared references
        return copy.deepcopy(self)
    
    def __str__(self):
        return f"Document(title={self.title}, content_length={len(self.content)})"

# Usage
original = Document(
    title="Template",
    content="This is a template document",
    metadata={"author": "Admin", "version": 1.0}
)

# Clone for new document
new_doc = original.clone()
new_doc.title = "New Document"
new_doc.metadata["author"] = "User"
new_doc.metadata["version"] = 2.0

print(original)  # Document(title=Template, content_length=28)
print(new_doc)    # Document(title=New Document, content_length=28)
```

**Interview Points**:
- Reduces object creation cost
- Deep vs shallow copy considerations
- Useful for expensive initialization

---

## Structural Patterns

### Adapter Pattern

**Intent**: Allow incompatible interfaces to work together.

**Use Case**: Integrating third-party libraries, legacy code integration.

**Python Implementation**:

```python
# Target interface
class PaymentGateway(ABC):
    @abstractmethod
    def pay(self, amount: float) -> bool:
        pass

# Adaptee (incompatible interface)
class LegacyPaymentSystem:
    def make_payment(self, dollars: float, cents: float) -> str:
        total = dollars + (cents / 100)
        return f"Payment of ${total:.2f} processed"

# Adapter
class LegacyPaymentAdapter(PaymentGateway):
    def __init__(self, legacy_system: LegacyPaymentSystem):
        self.legacy_system = legacy_system
    
    def pay(self, amount: float) -> bool:
        dollars = int(amount)
        cents = int((amount - dollars) * 100)
        result = self.legacy_system.make_payment(dollars, cents)
        return "processed" in result.lower()

# Usage
legacy = LegacyPaymentSystem()
adapter = LegacyPaymentAdapter(legacy)
adapter.pay(100.50)  # True
```

**Interview Points**:
- Wrapper pattern
- Enables integration without modifying existing code
- Single Responsibility Principle

---

### Decorator Pattern

**Intent**: Add behavior to objects dynamically without altering their structure.

**Use Case**: Adding features like logging, caching, validation to functions/classes.

**Python Implementation**:

```python
from functools import wraps

# Function decorator
def log_execution(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Executing {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Completed {func.__name__}")
        return result
    return wrapper

def cache_result(func):
    cache = {}
    @wraps(func)
    def wrapper(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    return wrapper

@log_execution
@cache_result
def expensive_operation(n: int) -> int:
    return sum(i * i for i in range(n))

# Class decorator
class Coffee:
    def cost(self) -> float:
        return 2.0
    
    def description(self) -> str:
        return "Coffee"

class CoffeeDecorator(Coffee):
    def __init__(self, coffee: Coffee):
        self._coffee = coffee
    
    def cost(self) -> float:
        return self._coffee.cost()
    
    def description(self) -> str:
        return self._coffee.description()

class Milk(CoffeeDecorator):
    def cost(self) -> float:
        return self._coffee.cost() + 0.5
    
    def description(self) -> str:
        return self._coffee.description() + ", Milk"

class Sugar(CoffeeDecorator):
    def cost(self) -> float:
        return self._coffee.cost() + 0.2
    
    def description(self) -> str:
        return self._coffee.description() + ", Sugar"

# Usage
coffee = Coffee()
coffee_with_milk = Milk(coffee)
coffee_with_milk_sugar = Sugar(coffee_with_milk)
print(coffee_with_milk_sugar.description())  # Coffee, Milk, Sugar
print(coffee_with_milk_sugar.cost())  # 2.7
```

**Interview Points**:
- Python's `@decorator` syntax
- Composition over inheritance
- Runtime behavior modification

---

### Facade Pattern

**Intent**: Provide a simplified interface to a complex subsystem.

**Use Case**: Simplifying API usage, hiding complexity.

**Python Implementation**:

```python
# Complex subsystem
class CPU:
    def freeze(self):
        print("CPU: Freezing...")
    
    def jump(self, position: int):
        print(f"CPU: Jumping to {position}")
    
    def execute(self):
        print("CPU: Executing...")

class Memory:
    def load(self, position: int, data: str):
        print(f"Memory: Loading {data} at {position}")

class HardDrive:
    def read(self, lba: int, size: int) -> str:
        print(f"HardDrive: Reading {size} bytes from {lba}")
        return "boot_data"

# Facade
class ComputerFacade:
    def __init__(self):
        self.cpu = CPU()
        self.memory = Memory()
        self.hard_drive = HardDrive()
    
    def start_computer(self):
        print("Starting computer...")
        self.cpu.freeze()
        boot_data = self.hard_drive.read(0, 1024)
        self.memory.load(0, boot_data)
        self.cpu.jump(0)
        self.cpu.execute()
        print("Computer started!")

# Usage
computer = ComputerFacade()
computer.start_computer()
```

**Interview Points**:
- Simplifies complex interactions
- Reduces coupling
- Single entry point

---

### Proxy Pattern

**Intent**: Provide a placeholder or surrogate for another object to control access.

**Use Case**: Lazy loading, access control, caching, remote proxies.

**Python Implementation**:

```python
from abc import ABC, abstractmethod

# Subject
class Image(ABC):
    @abstractmethod
    def display(self):
        pass

# Real subject
class RealImage(Image):
    def __init__(self, filename: str):
        self.filename = filename
        self._load_from_disk()
    
    def _load_from_disk(self):
        print(f"Loading {self.filename} from disk...")
    
    def display(self):
        print(f"Displaying {self.filename}")

# Proxy
class ProxyImage(Image):
    def __init__(self, filename: str):
        self.filename = filename
        self._real_image = None
    
    def display(self):
        if self._real_image is None:
            self._real_image = RealImage(self.filename)
        self._real_image.display()

# Usage
image = ProxyImage("photo.jpg")
# Image not loaded yet
image.display()  # Now loads and displays
image.display()  # Uses cached instance

# Property-based proxy (Pythonic)
class LazyProperty:
    def __init__(self, func):
        self.func = func
        self.name = func.__name__
    
    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = self.func(obj)
        setattr(obj, self.name, value)
        return value

class DataLoader:
    @LazyProperty
    def expensive_data(self):
        print("Loading expensive data...")
        return list(range(1000000))
```

**Interview Points**:
- Lazy initialization
- Access control
- Virtual proxy vs protection proxy

---

### Composite Pattern

**Intent**: Compose objects into tree structures to represent part-whole hierarchies.

**Use Case**: File systems, UI components, organizational structures.

**Python Implementation**:

```python
from abc import ABC, abstractmethod

class FileSystemComponent(ABC):
    @abstractmethod
    def get_size(self) -> int:
        pass
    
    @abstractmethod
    def display(self, indent: str = ""):
        pass

class File(FileSystemComponent):
    def __init__(self, name: str, size: int):
        self.name = name
        self._size = size
    
    def get_size(self) -> int:
        return self._size
    
    def display(self, indent: str = ""):
        print(f"{indent}File: {self.name} ({self._size} bytes)")

class Directory(FileSystemComponent):
    def __init__(self, name: str):
        self.name = name
        self.children = []
    
    def add(self, component: FileSystemComponent):
        self.children.append(component)
    
    def remove(self, component: FileSystemComponent):
        self.children.remove(component)
    
    def get_size(self) -> int:
        return sum(child.get_size() for child in self.children)
    
    def display(self, indent: str = ""):
        print(f"{indent}Directory: {self.name}")
        for child in self.children:
            child.display(indent + "  ")

# Usage
root = Directory("root")
documents = Directory("Documents")
documents.add(File("resume.pdf", 1024))
documents.add(File("cover_letter.pdf", 512))

pictures = Directory("Pictures")
pictures.add(File("photo1.jpg", 2048))
pictures.add(File("photo2.jpg", 3072))

root.add(documents)
root.add(pictures)
root.add(File("readme.txt", 256))

root.display()
print(f"Total size: {root.get_size()} bytes")
```

**Interview Points**:
- Tree structure
- Uniform interface for leaf and composite
- Recursive operations

---

## Behavioral Patterns

### Observer Pattern

**Intent**: Define a one-to-many dependency between objects so that when one changes, all dependents are notified.

**Use Case**: Event handling, model-view architecture, pub-sub systems.

**Python Implementation**:

```python
from abc import ABC, abstractmethod

class Observer(ABC):
    @abstractmethod
    def update(self, event: str, data: any):
        pass

class Subject:
    def __init__(self):
        self._observers = []
    
    def attach(self, observer: Observer):
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer):
        self._observers.remove(observer)
    
    def notify(self, event: str, data: any):
        for observer in self._observers:
            observer.update(event, data)

class StockPrice(Subject):
    def __init__(self, symbol: str, price: float):
        super().__init__()
        self.symbol = symbol
        self._price = price
    
    @property
    def price(self):
        return self._price
    
    @price.setter
    def price(self, value: float):
        if self._price != value:
            old_price = self._price
            self._price = value
            self.notify("price_changed", {
                "symbol": self.symbol,
                "old_price": old_price,
                "new_price": value
            })

class EmailNotifier(Observer):
    def __init__(self, email: str):
        self.email = email
    
    def update(self, event: str, data: any):
        if event == "price_changed":
            print(f"Email to {self.email}: {data['symbol']} changed from "
                  f"${data['old_price']} to ${data['new_price']}")

class SMSNotifier(Observer):
    def __init__(self, phone: str):
        self.phone = phone
    
    def update(self, event: str, data: any):
        if event == "price_changed":
            print(f"SMS to {self.phone}: {data['symbol']} = ${data['new_price']}")

# Usage
stock = StockPrice("AAPL", 150.0)
email_notifier = EmailNotifier("user@example.com")
sms_notifier = SMSNotifier("+1234567890")

stock.attach(email_notifier)
stock.attach(sms_notifier)

stock.price = 155.0
# Email to user@example.com: AAPL changed from $150.0 to $155.0
# SMS to +1234567890: AAPL = $155.0
```

**Interview Points**:
- Loose coupling
- Event-driven architecture
- Python's `property` decorator for automatic notifications

---

### Strategy Pattern

**Intent**: Define a family of algorithms, encapsulate each one, and make them interchangeable.

**Use Case**: Sorting algorithms, payment methods, compression algorithms.

**Python Implementation**:

```python
from abc import ABC, abstractmethod

class SortingStrategy(ABC):
    @abstractmethod
    def sort(self, data: list) -> list:
        pass

class QuickSort(SortingStrategy):
    def sort(self, data: list) -> list:
        print("Using QuickSort")
        return sorted(data)

class MergeSort(SortingStrategy):
    def sort(self, data: list) -> list:
        print("Using MergeSort")
        # Simplified merge sort
        if len(data) <= 1:
            return data
        mid = len(data) // 2
        left = self.sort(data[:mid])
        right = self.sort(data[mid:])
        return self._merge(left, right)
    
    def _merge(self, left: list, right: list) -> list:
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        result.extend(left[i:])
        result.extend(right[j:])
        return result

class BubbleSort(SortingStrategy):
    def sort(self, data: list) -> list:
        print("Using BubbleSort")
        data = data.copy()
        n = len(data)
        for i in range(n):
            for j in range(0, n - i - 1):
                if data[j] > data[j + 1]:
                    data[j], data[j + 1] = data[j + 1], data[j]
        return data

class Sorter:
    def __init__(self, strategy: SortingStrategy):
        self.strategy = strategy
    
    def set_strategy(self, strategy: SortingStrategy):
        self.strategy = strategy
    
    def sort(self, data: list) -> list:
        return self.strategy.sort(data)

# Usage
data = [64, 34, 25, 12, 22, 11, 90]

sorter = Sorter(QuickSort())
result = sorter.sort(data)
print(result)

sorter.set_strategy(MergeSort())
result = sorter.sort(data)
print(result)
```

**Interview Points**:
- Runtime algorithm selection
- Eliminates conditional statements
- Open/Closed Principle

---

### Command Pattern

**Intent**: Encapsulate a request as an object, allowing parameterization and queuing of requests.

**Use Case**: Undo/redo functionality, job queues, macro recording.

**Python Implementation**:

```python
from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def execute(self):
        pass
    
    @abstractmethod
    def undo(self):
        pass

class Light:
    def __init__(self):
        self.is_on = False
    
    def turn_on(self):
        self.is_on = True
        print("Light is ON")
    
    def turn_off(self):
        self.is_on = False
        print("Light is OFF")

class LightOnCommand(Command):
    def __init__(self, light: Light):
        self.light = light
    
    def execute(self):
        self.light.turn_on()
    
    def undo(self):
        self.light.turn_off()

class LightOffCommand(Command):
    def __init__(self, light: Light):
        self.light = light
    
    def execute(self):
        self.light.turn_off()
    
    def undo(self):
        self.light.turn_on()

class RemoteControl:
    def __init__(self):
        self.commands = []
        self.history = []
    
    def execute_command(self, command: Command):
        command.execute()
        self.history.append(command)
    
    def undo(self):
        if self.history:
            command = self.history.pop()
            command.undo()

# Usage
light = Light()
light_on = LightOnCommand(light)
light_off = LightOffCommand(light)

remote = RemoteControl()
remote.execute_command(light_on)
remote.execute_command(light_off)
remote.undo()  # Undoes light_off, turns light back on
```

**Interview Points**:
- Decouples invoker from receiver
- Supports undo/redo
- Can queue and log commands

---

### Chain of Responsibility

**Intent**: Pass requests along a chain of handlers until one handles it.

**Use Case**: Request processing pipelines, exception handling, middleware.

**Python Implementation**:

```python
from abc import ABC, abstractmethod

class Handler(ABC):
    def __init__(self):
        self._next_handler = None
    
    def set_next(self, handler: 'Handler'):
        self._next_handler = handler
        return handler
    
    @abstractmethod
    def handle(self, request: str) -> str:
        if self._next_handler:
            return self._next_handler.handle(request)
        return None

class AuthenticationHandler(Handler):
    def handle(self, request: str) -> str:
        if "auth_token" not in request:
            return "Authentication failed: No token"
        print("Authentication passed")
        return super().handle(request)

class AuthorizationHandler(Handler):
    def handle(self, request: str) -> str:
        if "admin" not in request:
            return "Authorization failed: Not admin"
        print("Authorization passed")
        return super().handle(request)

class ValidationHandler(Handler):
    def handle(self, request: str) -> str:
        if not request or len(request) < 10:
            return "Validation failed: Request too short"
        print("Validation passed")
        return super().handle(request)

class RequestProcessor(Handler):
    def handle(self, request: str) -> str:
        print("Processing request...")
        return "Request processed successfully"

# Usage
auth = AuthenticationHandler()
authz = AuthorizationHandler()
validation = ValidationHandler()
processor = RequestProcessor()

auth.set_next(authz).set_next(validation).set_next(processor)

result = auth.handle("auth_token=123 admin user data")
print(result)
```

**Interview Points**:
- Dynamic chain construction
- Request can be handled by any handler
- Middleware pattern

---

### State Pattern

**Intent**: Allow an object to alter its behavior when its internal state changes.

**Use Case**: State machines, game character states, workflow management.

**Python Implementation**:

```python
from abc import ABC, abstractmethod

class State(ABC):
    @abstractmethod
    def handle(self, context: 'Context'):
        pass

class Context:
    def __init__(self):
        self._state = None
    
    def set_state(self, state: State):
        self._state = state
    
    def request(self):
        self._state.handle(self)

class ConcreteStateA(State):
    def handle(self, context: Context):
        print("Handling in State A")
        context.set_state(ConcreteStateB())

class ConcreteStateB(State):
    def handle(self, context: Context):
        print("Handling in State B")
        context.set_state(ConcreteStateA())

# Usage
context = Context()
context.set_state(ConcreteStateA())

context.request()  # Handling in State A
context.request()  # Handling in State B
context.request()  # Handling in State A

# Real-world example: Vending Machine
class VendingMachineState(ABC):
    @abstractmethod
    def insert_coin(self, machine: 'VendingMachine'):
        pass
    
    @abstractmethod
    def select_item(self, machine: 'VendingMachine', item: str):
        pass

class NoCoinState(VendingMachineState):
    def insert_coin(self, machine: 'VendingMachine'):
        print("Coin inserted")
        machine.set_state(HasCoinState())
    
    def select_item(self, machine: 'VendingMachine', item: str):
        print("Please insert coin first")

class HasCoinState(VendingMachineState):
    def insert_coin(self, machine: 'VendingMachine'):
        print("Coin already inserted")
    
    def select_item(self, machine: 'VendingMachine', item: str):
        print(f"Dispensing {item}")
        machine.set_state(NoCoinState())

class VendingMachine:
    def __init__(self):
        self._state = NoCoinState()
    
    def set_state(self, state: VendingMachineState):
        self._state = state
    
    def insert_coin(self):
        self._state.insert_coin(self)
    
    def select_item(self, item: str):
        self._state.select_item(self, item)
```

**Interview Points**:
- State transitions
- Eliminates conditional state logic
- State-specific behavior

---

### Template Method Pattern

**Intent**: Define the skeleton of an algorithm, deferring some steps to subclasses.

**Use Case**: Framework design, data processing pipelines, report generation.

**Python Implementation**:

```python
from abc import ABC, abstractmethod

class DataProcessor(ABC):
    def process(self, data: list) -> list:
        """Template method"""
        validated_data = self.validate(data)
        cleaned_data = self.clean(validated_data)
        transformed_data = self.transform(cleaned_data)
        return self.save(transformed_data)
    
    def validate(self, data: list) -> list:
        """Hook method - can be overridden"""
        print("Validating data...")
        return [item for item in data if item is not None]
    
    @abstractmethod
    def clean(self, data: list) -> list:
        pass
    
    @abstractmethod
    def transform(self, data: list) -> list:
        pass
    
    def save(self, data: list) -> list:
        """Hook method - can be overridden"""
        print(f"Saving {len(data)} items...")
        return data

class NumberProcessor(DataProcessor):
    def clean(self, data: list) -> list:
        print("Cleaning numbers...")
        return [x for x in data if isinstance(x, (int, float))]
    
    def transform(self, data: list) -> list:
        print("Transforming numbers...")
        return [x * 2 for x in data]

class StringProcessor(DataProcessor):
    def clean(self, data: list) -> list:
        print("Cleaning strings...")
        return [str(x).strip() for x in data if x]
    
    def transform(self, data: list) -> list:
        print("Transforming strings...")
        return [x.upper() for x in data]

# Usage
numbers = [1, 2, None, 3, 4, "invalid"]
processor = NumberProcessor()
result = processor.process(numbers)
print(result)  # [2, 4, 6, 8]
```

**Interview Points**:
- Code reuse
- Hollywood Principle ("Don't call us, we'll call you")
- Framework pattern

---

## Python-Specific Patterns

### Context Manager Pattern

**Intent**: Manage resources with automatic cleanup using `with` statement.

**Use Case**: File handling, database connections, locks.

**Python Implementation**:

```python
class FileManager:
    def __init__(self, filename: str, mode: str = 'r'):
        self.filename = filename
        self.mode = mode
        self.file = None
    
    def __enter__(self):
        print(f"Opening {self.filename}")
        self.file = open(self.filename, self.mode)
        return self.file
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"Closing {self.filename}")
        if self.file:
            self.file.close()
        return False  # Don't suppress exceptions

# Usage
with FileManager("test.txt", "w") as f:
    f.write("Hello, World!")

# Using contextlib
from contextlib import contextmanager

@contextmanager
def timer():
    import time
    start = time.time()
    try:
        yield
    finally:
        end = time.time()
        print(f"Elapsed time: {end - start:.2f} seconds")

with timer():
    # Some operation
    sum(range(1000000))
```

**Interview Points**:
- `__enter__` and `__exit__` methods
- Exception handling
- Resource management

---

### Generator Pattern

**Intent**: Create iterators using generator functions for memory-efficient iteration.

**Use Case**: Large datasets, infinite sequences, lazy evaluation.

**Python Implementation**:

```python
def fibonacci_generator(n: int):
    """Generate Fibonacci numbers"""
    a, b = 0, 1
    count = 0
    while count < n:
        yield a
        a, b = b, a + b
        count += 1

# Usage
for num in fibonacci_generator(10):
    print(num)

# Generator expression
squares = (x * x for x in range(10))
print(list(squares))

# Infinite generator
def infinite_counter(start: int = 0):
    while True:
        yield start
        start += 1

counter = infinite_counter(10)
print(next(counter))  # 10
print(next(counter))  # 11

# Generator for file processing
def read_large_file(filename: str):
    with open(filename, 'r') as f:
        for line in f:
            yield line.strip()

# Process file line by line without loading entire file
for line in read_large_file("large_file.txt"):
    process(line)
```

**Interview Points**:
- Memory efficiency
- Lazy evaluation
- `yield` keyword
- Generator expressions

---

### Descriptor Pattern

**Intent**: Define how attribute access works using `__get__`, `__set__`, `__delete__`.

**Use Case**: Property validation, lazy attributes, computed properties.

**Python Implementation**:

```python
class ValidatedProperty:
    def __init__(self, validator=None):
        self.validator = validator
        self.name = None
    
    def __set_name__(self, owner, name):
        self.name = f"_{name}"
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.name, None)
    
    def __set__(self, obj, value):
        if self.validator and not self.validator(value):
            raise ValueError(f"Invalid value: {value}")
        setattr(obj, self.name, value)

class PositiveNumber:
    def __init__(self):
        self.name = None
    
    def __set_name__(self, owner, name):
        self.name = f"_{name}"
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.name, None)
    
    def __set__(self, obj, value):
        if value <= 0:
            raise ValueError("Value must be positive")
        setattr(obj, self.name, value)

class BankAccount:
    balance = PositiveNumber()
    
    def __init__(self, initial_balance: float):
        self.balance = initial_balance

# Usage
account = BankAccount(100.0)
print(account.balance)  # 100.0
# account.balance = -50  # Raises ValueError
```

**Interview Points**:
- `__get__`, `__set__`, `__delete__`
- Property validation
- Data descriptors vs non-data descriptors

---

## Interview Questions & Answers

### Q1: When would you use Singleton pattern?

**Answer**: 
- When you need exactly one instance (database connections, logging)
- When global access point is needed
- When instance creation is expensive

**Trade-offs**:
- Pros: Controlled access, memory efficient
- Cons: Global state, testing difficulties, thread safety concerns

### Q2: Difference between Factory and Abstract Factory?

**Answer**:
- **Factory Method**: Creates objects of one type, uses inheritance
- **Abstract Factory**: Creates families of related objects, uses composition

```python
# Factory Method
class AnimalFactory:
    def create_animal(self, animal_type):
        if animal_type == "dog":
            return Dog()
        elif animal_type == "cat":
            return Cat()

# Abstract Factory
class PetFactory(ABC):
    @abstractmethod
    def create_food(self):
        pass
    
    @abstractmethod
    def create_toy(self):
        pass

class DogFactory(PetFactory):
    def create_food(self):
        return DogFood()
    
    def create_toy(self):
        return DogToy()
```

### Q3: How does Decorator differ from Inheritance?

**Answer**:
- **Inheritance**: Static, compile-time behavior change
- **Decorator**: Dynamic, runtime behavior addition
- Decorator allows adding multiple behaviors without class explosion

### Q4: Observer vs Pub-Sub Pattern?

**Answer**:
- **Observer**: Direct communication, subject knows observers
- **Pub-Sub**: Indirect communication via message broker, decoupled

### Q5: When to use Strategy vs State Pattern?

**Answer**:
- **Strategy**: Algorithm selection, client chooses strategy
- **State**: Behavior changes based on internal state, state transitions

### Q6: How to implement thread-safe Singleton in Python?

**Answer**:

```python
import threading

class ThreadSafeSingleton:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
```

### Q7: Explain Python's MRO (Method Resolution Order) in context of patterns?

**Answer**:
- MRO determines method lookup order in multiple inheritance
- Uses C3 linearization algorithm
- Important for understanding how patterns work with inheritance

```python
class A:
    def method(self):
        return "A"

class B(A):
    def method(self):
        return "B"

class C(A):
    def method(self):
        return "C"

class D(B, C):
    pass

print(D.__mro__)  # Shows method resolution order
d = D()
print(d.method())  # "B" (first in MRO)
```

### Q8: How would you implement a caching decorator?

**Answer**:

```python
from functools import wraps

def cache(func):
    cache_dict = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        key = str(args) + str(sorted(kwargs.items()))
        if key not in cache_dict:
            cache_dict[key] = func(*args, **kwargs)
        return cache_dict[key]
    
    wrapper.cache_clear = cache_dict.clear
    return wrapper

@cache
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

### Q9: Design a logger using multiple patterns?

**Answer**:

```python
# Singleton + Strategy + Decorator
class Logger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.handlers = []
        return cls._instance
    
    def add_handler(self, handler):
        self.handlers.append(handler)
    
    def log(self, level, message):
        for handler in self.handlers:
            handler.log(level, message)

class LogHandler(ABC):
    @abstractmethod
    def log(self, level, message):
        pass

class ConsoleHandler(LogHandler):
    def log(self, level, message):
        print(f"[{level}] {message}")

class FileHandler(LogHandler):
    def log(self, level, message):
        with open("app.log", "a") as f:
            f.write(f"[{level}] {message}\n")

def log_execution(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = Logger()
        logger.log("INFO", f"Executing {func.__name__}")
        result = func(*args, **kwargs)
        logger.log("INFO", f"Completed {func.__name__}")
        return result
    return wrapper
```

### Q10: How to implement undo/redo using Command pattern?

**Answer**:

```python
class Command(ABC):
    @abstractmethod
    def execute(self):
        pass
    
    @abstractmethod
    def undo(self):
        pass

class CommandHistory:
    def __init__(self):
        self.history = []
        self.current = -1
    
    def execute(self, command: Command):
        # Remove any commands after current position
        self.history = self.history[:self.current + 1]
        command.execute()
        self.history.append(command)
        self.current += 1
    
    def undo(self):
        if self.current >= 0:
            self.history[self.current].undo()
            self.current -= 1
    
    def redo(self):
        if self.current < len(self.history) - 1:
            self.current += 1
            self.history[self.current].execute()
```

---

## Best Practices

1. **Prefer Composition over Inheritance**: Use decorators, strategies
2. **Use Python's Built-in Features**: `@property`, `@staticmethod`, `@classmethod`
3. **Keep It Simple**: Don't over-engineer; Python's dynamism reduces need for some patterns
4. **Document Patterns**: Explain why you're using a pattern
5. **Test Patterns**: Ensure patterns work correctly, especially with concurrency

---

**Document Version**: 1.0  
**Last Updated**: January 2024

