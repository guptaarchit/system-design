# Object-Oriented Programming (OOPs) Concepts in Python

## Table of Contents
1. [Introduction to OOP](#introduction-to-oop)
2. [Classes and Objects](#classes-and-objects)
3. [Encapsulation](#encapsulation)
4. [Inheritance](#inheritance)
5. [Polymorphism](#polymorphism)
6. [Abstraction](#abstraction)
7. [Advanced OOP Concepts](#advanced-oop-concepts)
8. [Special Methods (Magic Methods)](#special-methods-magic-methods)
9. [Property Decorators](#property-decorators)
10. [Composition vs Inheritance](#composition-vs-inheritance)

---

## Introduction to OOP

### What is Object-Oriented Programming?

Object-Oriented Programming (OOP) is a programming paradigm that organizes code around objects and classes. It provides a way to structure programs so that properties and behaviors are bundled into individual objects.

### Core Principles

1. **Encapsulation**: Bundling data and methods that operate on that data
2. **Inheritance**: Creating new classes based on existing classes
3. **Polymorphism**: Using a single interface to represent different types
4. **Abstraction**: Hiding complex implementation details

---

## Classes and Objects

### Basic Class Definition

**Example:**
```python
class Dog:
    """A simple Dog class"""
    
    # Class attribute (shared by all instances)
    species = "Canis familiaris"
    
    def __init__(self, name, age):
        """Constructor - initializes instance attributes"""
        self.name = name  # Instance attribute
        self.age = age    # Instance attribute
    
    def bark(self):
        """Instance method"""
        return f"{self.name} says Woof!"
    
    def get_info(self):
        """Instance method"""
        return f"{self.name} is {self.age} years old"

# Creating objects (instances)
dog1 = Dog("Buddy", 3)
dog2 = Dog("Max", 5)

print(dog1.bark())  # Buddy says Woof!
print(dog2.get_info())  # Max is 5 years old
print(f"Species: {Dog.species}")  # Canis familiaris
```

### Class Methods vs Instance Methods vs Static Methods

**Example:**
```python
class Calculator:
    # Class variable
    operation_count = 0
    
    def __init__(self, value=0):
        self.value = value
    
    # Instance method - works with instance data
    def add(self, num):
        Calculator.operation_count += 1
        self.value += num
        return self.value
    
    # Class method - works with class data, receives class as first parameter
    @classmethod
    def get_operation_count(cls):
        return cls.operation_count
    
    @classmethod
    def create_from_string(cls, value_str):
        """Alternative constructor"""
        return cls(int(value_str))
    
    # Static method - doesn't need class or instance, utility function
    @staticmethod
    def is_even(num):
        return num % 2 == 0

# Usage
calc1 = Calculator(10)
calc2 = Calculator(20)

calc1.add(5)  # Instance method
calc2.add(10)  # Instance method

print(Calculator.get_operation_count())  # 2 (class method)
print(Calculator.is_even(4))  # True (static method)

# Using alternative constructor
calc3 = Calculator.create_from_string("100")
print(calc3.value)  # 100
```

---

## Encapsulation

### Public, Protected, and Private Attributes

**Example:**
```python
class BankAccount:
    def __init__(self, account_number, balance=0):
        # Public attribute (can be accessed directly)
        self.account_number = account_number
        
        # Protected attribute (convention: single underscore)
        # Should not be accessed directly, but Python doesn't enforce this
        self._balance = balance
        
        # Private attribute (double underscore - name mangling)
        # Python changes the name to _BankAccount__pin
        self.__pin = "1234"
    
    # Public method
    def deposit(self, amount):
        if amount > 0:
            self._balance += amount
            return True
        return False
    
    # Public method
    def withdraw(self, amount, pin):
        if self._verify_pin(pin):
            if 0 < amount <= self._balance:
                self._balance -= amount
                return True
        return False
    
    # Protected method
    def _verify_pin(self, pin):
        return pin == self.__pin
    
    # Public method to access private attribute safely
    def get_balance(self):
        return self._balance

# Usage
account = BankAccount("ACC001", 1000)

# Public access
print(account.account_number)  # ACC001

# Protected access (works but not recommended)
print(account._balance)  # 1000

# Private access (name mangling)
# account.__pin  # AttributeError
# But can access via name mangling (not recommended)
print(account._BankAccount__pin)  # 1234 (not recommended!)

# Proper way
account.deposit(500)
print(account.get_balance())  # 1500
account.withdraw(200, "1234")
print(account.get_balance())  # 1300
```

### Property Decorator for Encapsulation

**Example:**
```python
class Temperature:
    def __init__(self, celsius=0):
        self._celsius = celsius
    
    @property
    def celsius(self):
        """Getter for celsius"""
        return self._celsius
    
    @celsius.setter
    def celsius(self, value):
        """Setter for celsius with validation"""
        if value < -273.15:
            raise ValueError("Temperature cannot be below absolute zero")
        self._celsius = value
    
    @property
    def fahrenheit(self):
        """Computed property"""
        return self._celsius * 9/5 + 32
    
    @fahrenheit.setter
    def fahrenheit(self, value):
        """Setter that updates celsius"""
        self._celsius = (value - 32) * 5/9

# Usage
temp = Temperature(25)
print(f"Celsius: {temp.celsius}")  # 25
print(f"Fahrenheit: {temp.fahrenheit}")  # 77.0

temp.celsius = 30
print(f"Fahrenheit: {temp.fahrenheit}")  # 86.0

temp.fahrenheit = 100
print(f"Celsius: {temp.celsius}")  # 37.777...

try:
    temp.celsius = -300  # Raises ValueError
except ValueError as e:
    print(f"Error: {e}")
```

---

## Inheritance

### Single Inheritance

**Example:**
```python
class Animal:
    def __init__(self, name, species):
        self.name = name
        self.species = species
    
    def make_sound(self):
        return "Some generic sound"
    
    def get_info(self):
        return f"{self.name} is a {self.species}"

class Dog(Animal):
    def __init__(self, name, breed):
        # Call parent constructor
        super().__init__(name, "Dog")
        self.breed = breed
    
    # Method overriding
    def make_sound(self):
        return "Woof! Woof!"
    
    def fetch(self):
        return f"{self.name} is fetching the ball"

class Cat(Animal):
    def __init__(self, name, color):
        super().__init__(name, "Cat")
        self.color = color
    
    def make_sound(self):
        return "Meow!"
    
    def climb(self):
        return f"{self.name} is climbing"

# Usage
dog = Dog("Buddy", "Golden Retriever")
cat = Cat("Whiskers", "Orange")

print(dog.get_info())  # Buddy is a Dog
print(dog.make_sound())  # Woof! Woof!
print(dog.fetch())  # Buddy is fetching the ball

print(cat.get_info())  # Whiskers is a Cat
print(cat.make_sound())  # Meow!
print(cat.climb())  # Whiskers is climbing
```

### Multiple Inheritance

**Example:**
```python
class Flyable:
    def fly(self):
        return "Flying high!"

class Swimmable:
    def swim(self):
        return "Swimming!"

class Duck(Animal, Flyable, Swimmable):
    def __init__(self, name):
        super().__init__(name, "Duck")
    
    def make_sound(self):
        return "Quack!"

# Usage
duck = Duck("Donald")
print(duck.make_sound())  # Quack!
print(duck.fly())  # Flying high!
print(duck.swim())  # Swimming!
print(duck.get_info())  # Donald is a Duck
```

### Method Resolution Order (MRO)

**Example:**
```python
class A:
    def method(self):
        print("A.method")

class B(A):
    def method(self):
        print("B.method")
        super().method()

class C(A):
    def method(self):
        print("C.method")
        super().method()

class D(B, C):
    def method(self):
        print("D.method")
        super().method()

# Check MRO
print(D.__mro__)
# Output: (<class '__main__.D'>, <class '__main__.B'>, <class '__main__.C'>, <class '__main__.A'>, <class 'object'>)

d = D()
d.method()
# Output:
# D.method
# B.method
# C.method
# A.method
```

### Method Overriding and super()

**Example:**
```python
class Employee:
    def __init__(self, name, employee_id):
        self.name = name
        self.employee_id = employee_id
    
    def calculate_salary(self):
        return 50000
    
    def get_info(self):
        return f"Employee: {self.name} (ID: {self.employee_id})"

class Manager(Employee):
    def __init__(self, name, employee_id, department):
        super().__init__(name, employee_id)
        self.department = department
    
    def calculate_salary(self):
        # Call parent method and add bonus
        base_salary = super().calculate_salary()
        return base_salary + 20000
    
    def get_info(self):
        # Extend parent method
        info = super().get_info()
        return f"{info}, Department: {self.department}"

class Developer(Employee):
    def __init__(self, name, employee_id, programming_language):
        super().__init__(name, employee_id)
        self.programming_language = programming_language
    
    def calculate_salary(self):
        base_salary = super().calculate_salary()
        return base_salary + 10000

# Usage
manager = Manager("Alice", "M001", "Engineering")
developer = Developer("Bob", "D001", "Python")

print(manager.get_info())
print(f"Salary: ${manager.calculate_salary()}")

print(developer.get_info())
print(f"Salary: ${developer.calculate_salary()}")
```

---

## Polymorphism

### Method Overriding (Runtime Polymorphism)

**Example:**
```python
class Shape:
    def area(self):
        raise NotImplementedError("Subclass must implement area()")
    
    def perimeter(self):
        raise NotImplementedError("Subclass must implement perimeter()")

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height
    
    def perimeter(self):
        return 2 * (self.width + self.height)

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):
        return 3.14159 * self.radius ** 2
    
    def perimeter(self):
        return 2 * 3.14159 * self.radius

class Triangle(Shape):
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c
    
    def area(self):
        # Heron's formula
        s = self.perimeter() / 2
        return (s * (s - self.a) * (s - self.b) * (s - self.c)) ** 0.5
    
    def perimeter(self):
        return self.a + self.b + self.c

# Polymorphic behavior
def print_shape_info(shape):
    """This function works with any Shape subclass"""
    print(f"Area: {shape.area():.2f}")
    print(f"Perimeter: {shape.perimeter():.2f}")

# Usage
shapes = [
    Rectangle(5, 3),
    Circle(4),
    Triangle(3, 4, 5)
]

for shape in shapes:
    print_shape_info(shape)
    print()
```

### Duck Typing (Python's Approach to Polymorphism)

**Example:**
```python
class Dog:
    def speak(self):
        return "Woof!"

class Cat:
    def speak(self):
        return "Meow!"

class Robot:
    def speak(self):
        return "Beep boop!"

# Duck typing: "If it walks like a duck and quacks like a duck, it's a duck"
def make_sound(animal):
    """Works with any object that has a speak() method"""
    return animal.speak()

# Usage
animals = [Dog(), Cat(), Robot()]

for animal in animals:
    print(make_sound(animal))
```

### Operator Overloading

**Example:**
```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        """Overload + operator"""
        return Vector(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        """Overload - operator"""
        return Vector(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        """Overload * operator"""
        return Vector(self.x * scalar, self.y * scalar)
    
    def __eq__(self, other):
        """Overload == operator"""
        return self.x == other.x and self.y == other.y
    
    def __str__(self):
        """String representation"""
        return f"Vector({self.x}, {self.y})"
    
    def __repr__(self):
        """Official string representation"""
        return f"Vector({self.x}, {self.y})"

# Usage
v1 = Vector(2, 3)
v2 = Vector(1, 4)

print(v1 + v2)  # Vector(3, 7)
print(v1 - v2)  # Vector(1, -1)
print(v1 * 3)   # Vector(6, 9)
print(v1 == v2)  # False
```

---

## Abstraction

### Abstract Base Classes (ABC)

**Example:**
```python
from abc import ABC, abstractmethod, abstractproperty

class Vehicle(ABC):
    """Abstract base class for vehicles"""
    
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model
    
    @abstractmethod
    def start_engine(self):
        """Abstract method - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def stop_engine(self):
        """Abstract method - must be implemented by subclasses"""
        pass
    
    @abstractproperty
    def fuel_type(self):
        """Abstract property - must be implemented by subclasses"""
        pass
    
    def get_info(self):
        """Concrete method - can be used by all subclasses"""
        return f"{self.brand} {self.model}"

class Car(Vehicle):
    def __init__(self, brand, model, fuel):
        super().__init__(brand, model)
        self._fuel = fuel
    
    def start_engine(self):
        return f"{self.get_info()} engine started"
    
    def stop_engine(self):
        return f"{self.get_info()} engine stopped"
    
    @property
    def fuel_type(self):
        return self._fuel

class Motorcycle(Vehicle):
    def __init__(self, brand, model):
        super().__init__(brand, model)
    
    def start_engine(self):
        return f"{self.get_info()} engine started"
    
    def stop_engine(self):
        return f"{self.get_info()} engine stopped"
    
    @property
    def fuel_type(self):
        return "Petrol"

# Usage
car = Car("Toyota", "Camry", "Gasoline")
motorcycle = Motorcycle("Honda", "CBR")

print(car.start_engine())
print(car.fuel_type)
print(motorcycle.start_engine())
print(motorcycle.fuel_type)

# Cannot instantiate abstract class
try:
    vehicle = Vehicle("Brand", "Model")  # Raises TypeError
except TypeError as e:
    print(f"Error: {e}")
```

### Interface-like Behavior with ABC

**Example:**
```python
from abc import ABC, abstractmethod

class Drawable(ABC):
    @abstractmethod
    def draw(self):
        pass

class Shape(Drawable):
    def draw(self):
        return "Drawing a shape"

class Circle(Shape):
    def draw(self):
        return "Drawing a circle"

class Rectangle(Shape):
    def draw(self):
        return "Drawing a rectangle"

def render_all(drawables):
    """Function that works with any Drawable object"""
    for drawable in drawables:
        print(drawable.draw())

# Usage
shapes = [Circle(), Rectangle()]
render_all(shapes)
```

---

## Advanced OOP Concepts

### Mixins

**Example:**
```python
class JSONSerializableMixin:
    def to_json(self):
        import json
        return json.dumps(self.__dict__)

class XMLSerializableMixin:
    def to_xml(self):
        import xml.etree.ElementTree as ET
        root = ET.Element(self.__class__.__name__)
        for key, value in self.__dict__.items():
            child = ET.SubElement(root, key)
            child.text = str(value)
        return ET.tostring(root, encoding='unicode')

class LoggableMixin:
    def log(self, message):
        print(f"[{self.__class__.__name__}] {message}")

class Person(JSONSerializableMixin, XMLSerializableMixin, LoggableMixin):
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def greet(self):
        self.log(f"{self.name} says hello")
        return f"Hello, I'm {self.name}"

# Usage
person = Person("Alice", 30)
print(person.greet())
print(person.to_json())
print(person.to_xml())
```

### Descriptors

**Example:**
```python
class ValidatedAttribute:
    """Descriptor for validated attributes"""
    
    def __init__(self, validator, default=None):
        self.validator = validator
        self.default = default
        self.name = None
    
    def __set_name__(self, owner, name):
        self.name = f"_{name}"
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.name, self.default)
    
    def __set__(self, obj, value):
        if self.validator(value):
            setattr(obj, self.name, value)
        else:
            raise ValueError(f"Invalid value: {value}")

class PositiveNumber:
    @staticmethod
    def validate(value):
        return isinstance(value, (int, float)) and value > 0

class Person:
    age = ValidatedAttribute(lambda x: isinstance(x, int) and 0 <= x <= 150)
    salary = ValidatedAttribute(PositiveNumber.validate)
    
    def __init__(self, name, age, salary):
        self.name = name
        self.age = age
        self.salary = salary

# Usage
person = Person("Bob", 30, 50000)
print(f"Age: {person.age}, Salary: {person.salary}")

try:
    person.age = 200  # Raises ValueError
except ValueError as e:
    print(f"Error: {e}")

try:
    person.salary = -1000  # Raises ValueError
except ValueError as e:
    print(f"Error: {e}")
```

### `__slots__` for Memory Optimization

**Example:**
```python
class PointWithoutSlots:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class PointWithSlots:
    __slots__ = ['x', 'y']
    
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Memory comparison
import sys

p1 = PointWithoutSlots(1, 2)
p2 = PointWithSlots(1, 2)

print(f"Without __slots__: {sys.getsizeof(p1)} bytes")
print(f"With __slots__: {sys.getsizeof(p2)} bytes")

# __slots__ prevents dynamic attribute creation
try:
    p2.z = 3  # Raises AttributeError
except AttributeError as e:
    print(f"Error: {e}")

# Performance benefit
import timeit

def create_without_slots():
    return PointWithoutSlots(1, 2)

def create_with_slots():
    return PointWithSlots(1, 2)

print(f"Without slots: {timeit.timeit(create_without_slots, number=1000000):.4f}s")
print(f"With slots: {timeit.timeit(create_with_slots, number=1000000):.4f}s")
```

---

## Special Methods (Magic Methods)

### Common Magic Methods

**Example:**
```python
class Book:
    def __init__(self, title, author, pages):
        self.title = title
        self.author = author
        self.pages = pages
    
    def __str__(self):
        """String representation for users"""
        return f"'{self.title}' by {self.author}"
    
    def __repr__(self):
        """Official string representation"""
        return f"Book('{self.title}', '{self.author}', {self.pages})"
    
    def __len__(self):
        """Length of the book"""
        return self.pages
    
    def __eq__(self, other):
        """Equality comparison"""
        if isinstance(other, Book):
            return self.title == other.title and self.author == other.author
        return False
    
    def __lt__(self, other):
        """Less than comparison"""
        if isinstance(other, Book):
            return self.pages < other.pages
        return NotImplemented
    
    def __hash__(self):
        """Hash for use in sets and dictionaries"""
        return hash((self.title, self.author))
    
    def __getitem__(self, key):
        """Support indexing"""
        if key == 'title':
            return self.title
        elif key == 'author':
            return self.author
        elif key == 'pages':
            return self.pages
        raise KeyError(f"'{key}' not found")
    
    def __contains__(self, item):
        """Support 'in' operator"""
        return item.lower() in self.title.lower() or item.lower() in self.author.lower()

# Usage
book1 = Book("Python Programming", "John Doe", 300)
book2 = Book("Python Programming", "John Doe", 300)
book3 = Book("Java Basics", "Jane Smith", 250)

print(str(book1))  # 'Python Programming' by John Doe
print(repr(book1))  # Book('Python Programming', 'John Doe', 300)
print(len(book1))  # 300
print(book1 == book2)  # True
print(book1 < book3)  # False (300 > 250)
print(book1['title'])  # Python Programming
print("Python" in book1)  # True

# Using in sets (requires __hash__)
books = {book1, book2, book3}
print(len(books))  # 2 (book1 and book2 are equal)
```

### Context Managers (`__enter__` and `__exit__`)

**Example:**
```python
class FileManager:
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.file = None
    
    def __enter__(self):
        """Called when entering 'with' block"""
        self.file = open(self.filename, self.mode)
        print(f"Opened {self.filename}")
        return self.file
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Called when exiting 'with' block"""
        if self.file:
            self.file.close()
            print(f"Closed {self.filename}")
        
        # Return False to propagate exceptions, True to suppress them
        return False

# Usage
with FileManager("test.txt", "w") as f:
    f.write("Hello, World!")

# File is automatically closed even if exception occurs
try:
    with FileManager("test.txt", "r") as f:
        content = f.read()
        raise ValueError("Test exception")
except ValueError:
    print("Exception handled, file was closed")
```

---

## Property Decorators

### Advanced Property Usage

**Example:**
```python
class BankAccount:
    def __init__(self, account_number, initial_balance=0):
        self._account_number = account_number
        self._balance = initial_balance
        self._transaction_history = []
    
    @property
    def account_number(self):
        """Read-only property"""
        return self._account_number
    
    @property
    def balance(self):
        """Read-only balance"""
        return self._balance
    
    @property
    def transaction_history(self):
        """Read-only transaction history"""
        return tuple(self._transaction_history)
    
    def deposit(self, amount):
        if amount > 0:
            self._balance += amount
            self._transaction_history.append(f"Deposit: +${amount}")
            return True
        return False
    
    def withdraw(self, amount):
        if 0 < amount <= self._balance:
            self._balance -= amount
            self._transaction_history.append(f"Withdraw: -${amount}")
            return True
        return False

# Usage
account = BankAccount("ACC001", 1000)
account.deposit(500)
account.withdraw(200)

print(f"Balance: ${account.balance}")
print(f"Transactions: {account.transaction_history}")

# Cannot modify read-only properties
try:
    account.balance = 5000  # Raises AttributeError
except AttributeError:
    print("Cannot modify balance directly")
```

---

## Composition vs Inheritance

### Composition Example

**Example:**
```python
class Engine:
    def __init__(self, horsepower):
        self.horsepower = horsepower
    
    def start(self):
        return "Engine started"
    
    def stop(self):
        return "Engine stopped"

class Wheels:
    def __init__(self, count=4):
        self.count = count
    
    def rotate(self):
        return f"{self.count} wheels rotating"

class Car:
    # Composition: Car HAS-A Engine and HAS-A Wheels
    def __init__(self, brand, engine_horsepower):
        self.brand = brand
        self.engine = Engine(engine_horsepower)  # Composition
        self.wheels = Wheels(4)  # Composition
    
    def start(self):
        return f"{self.brand}: {self.engine.start()}"
    
    def drive(self):
        return f"{self.brand}: {self.wheels.rotate()}"

# Usage
car = Car("Toyota", 200)
print(car.start())
print(car.drive())
```

### When to Use Composition vs Inheritance

**Example:**
```python
# Inheritance: IS-A relationship
class Animal:
    def eat(self):
        return "Eating"

class Dog(Animal):  # Dog IS-A Animal
    def bark(self):
        return "Barking"

# Composition: HAS-A relationship
class Legs:
    def walk(self):
        return "Walking"

class Animal:
    def __init__(self):
        self.legs = Legs()  # Animal HAS-A Legs
    
    def move(self):
        return self.legs.walk()

# Prefer composition for flexibility
class FlyingAnimal:
    def __init__(self):
        self.wings = Wings()
    
    def move(self):
        return self.wings.fly()

class SwimmingAnimal:
    def __init__(self):
        self.fins = Fins()
    
    def move(self):
        return self.fins.swim()
```

---

## Real-World Example: E-Commerce System

**Complete Example:**
```python
from abc import ABC, abstractmethod
from datetime import datetime

class Product(ABC):
    """Abstract base class for products"""
    
    def __init__(self, product_id, name, price):
        self.product_id = product_id
        self.name = name
        self._price = price
    
    @property
    def price(self):
        return self._price
    
    @abstractmethod
    def calculate_discount(self):
        pass
    
    def __str__(self):
        return f"{self.name} - ${self.price}"

class Electronics(Product):
    def __init__(self, product_id, name, price, warranty_years):
        super().__init__(product_id, name, price)
        self.warranty_years = warranty_years
    
    def calculate_discount(self):
        return self.price * 0.1  # 10% discount

class Clothing(Product):
    def __init__(self, product_id, name, price, size):
        super().__init__(product_id, name, price)
        self.size = size
    
    def calculate_discount(self):
        return self.price * 0.15  # 15% discount

class Cart:
    """Shopping cart using composition"""
    
    def __init__(self):
        self.items = []
    
    def add_item(self, product, quantity=1):
        self.items.append({"product": product, "quantity": quantity})
    
    def calculate_total(self):
        total = 0
        for item in self.items:
            product = item["product"]
            quantity = item["quantity"]
            discount = product.calculate_discount()
            total += (product.price - discount) * quantity
        return total
    
    def __len__(self):
        return len(self.items)

class Customer:
    def __init__(self, customer_id, name, email):
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.cart = Cart()  # Composition
    
    def add_to_cart(self, product, quantity=1):
        self.cart.add_item(product, quantity)
    
    def checkout(self):
        total = self.cart.calculate_total()
        return f"Order total: ${total:.2f}"

# Usage
laptop = Electronics("E001", "Laptop", 1000, 2)
shirt = Clothing("C001", "T-Shirt", 50, "M")

customer = Customer("CUST001", "John Doe", "john@example.com")
customer.add_to_cart(laptop, 1)
customer.add_to_cart(shirt, 2)

print(customer.checkout())
print(f"Items in cart: {len(customer.cart)}")
```

---

## Summary

### Key OOP Concepts in Python:

1. **Classes and Objects**: Blueprint for creating objects with attributes and methods
2. **Encapsulation**: Data hiding using private/protected attributes and properties
3. **Inheritance**: Code reuse through class hierarchies
4. **Polymorphism**: Same interface for different implementations
5. **Abstraction**: Hiding complexity using abstract base classes
6. **Special Methods**: Magic methods for operator overloading and special behaviors
7. **Composition**: Building complex objects from simpler ones (HAS-A relationship)

### Best Practices:

- Use `@property` for controlled attribute access
- Prefer composition over inheritance when possible
- Use abstract base classes for defining interfaces
- Leverage `__slots__` for memory optimization when needed
- Implement proper `__str__` and `__repr__` methods
- Use context managers for resource management
- Follow naming conventions (single underscore for protected, double for private)

This comprehensive guide covers all major OOP concepts in Python with practical examples that demonstrate real-world usage patterns.

