# Python Advanced Interview Questions with Examples

## Table of Contents
1. [Memory Management & Garbage Collection](#memory-management--garbage-collection)
2. [Decorators & Metaclasses](#decorators--metaclasses)
3. [Generators & Iterators](#generators--iterators)
4. [Concurrency & Parallelism](#concurrency--parallelism)
5. [Advanced Data Structures](#advanced-data-structures)
6. [Python Internals](#python-internals)
7. [Design Patterns](#design-patterns)
8. [Performance Optimization](#performance-optimization)
9. [Error Handling & Debugging](#error-handling--debugging)
10. [Advanced OOP Concepts](#advanced-oop-concepts)

---

## Memory Management & Garbage Collection

### Q1: Explain Python's memory management and garbage collection mechanism.

**Answer:**
Python uses automatic memory management through reference counting and a cyclic garbage collector.

**Example:**
```python
import sys
import gc

class Node:
    def __init__(self, value):
        self.value = value
        self.next = None
    
    def __del__(self):
        print(f"Node {self.value} is being deleted")

# Reference counting
a = Node(1)
print(f"Reference count: {sys.getrefcount(a)}")  # 2 (a + getrefcount's temp ref)

b = a
print(f"Reference count: {sys.getrefcount(a)}")  # 3 (a, b + temp ref)

del b
print(f"Reference count: {sys.getrefcount(a)}")  # 2

# Circular reference
node1 = Node(1)
node2 = Node(2)
node1.next = node2
node2.next = node1  # Circular reference

del node1
del node2
# Objects not deleted immediately due to circular reference

# Force garbage collection
gc.collect()  # Will detect and clean circular references
```

### Q2: What is the difference between `__del__` and `__delete__`?

**Answer:**
- `__del__`: Destructor method called when object is garbage collected
- `__delete__`: Descriptor method for attribute deletion

**Example:**
```python
class Descriptor:
    def __get__(self, obj, objtype=None):
        return obj._value
    
    def __set__(self, obj, value):
        obj._value = value
    
    def __delete__(self, obj):
        print("Deleting attribute")
        del obj._value

class MyClass:
    x = Descriptor()
    
    def __init__(self, value):
        self._value = value
    
    def __del__(self):
        print("MyClass instance is being deleted")

obj = MyClass(10)
print(obj.x)  # 10

del obj.x  # Calls __delete__
# Output: Deleting attribute

del obj  # Calls __del__
# Output: MyClass instance is being deleted
```

### Q3: Explain memory views and when to use them.

**Answer:**
Memory views provide a way to access the internal data of an object without copying it.

**Example:**
```python
import array

# Create array
arr = array.array('i', [1, 2, 3, 4, 5])
print(f"Original array: {arr}")

# Create memory view (no copy)
mv = memoryview(arr)
print(f"Memory view: {mv.tolist()}")

# Modify through memory view
mv[0] = 99
print(f"Modified array: {arr}")  # Original array is modified

# Slicing memory view (still no copy)
mv_slice = mv[1:4]
print(f"Slice: {mv_slice.tolist()}")

# Compare memory usage
import sys
print(f"Array size: {sys.getsizeof(arr)}")
print(f"Memory view size: {sys.getsizeof(mv)}")  # Much smaller
```

---

## Decorators & Metaclasses

### Q4: Write a decorator that measures function execution time and caches results.

**Answer:**
```python
import time
from functools import wraps

def timed_cache(seconds=60):
    """Decorator that caches results for specified seconds and times execution"""
    cache = {}
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            key = str(args) + str(sorted(kwargs.items()))
            
            # Check cache
            if key in cache:
                result, timestamp = cache[key]
                if time.time() - timestamp < seconds:
                    print(f"Cache hit for {func.__name__}")
                    return result
            
            # Execute function
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            
            # Cache result
            cache[key] = (result, time.time())
            print(f"{func.__name__} executed in {elapsed:.4f}s")
            
            return result
        return wrapper
    return decorator

@timed_cache(seconds=5)
def expensive_operation(n):
    time.sleep(1)
    return n * 2

print(expensive_operation(5))  # Executes and caches
print(expensive_operation(5))  # Uses cache
time.sleep(6)
print(expensive_operation(5))  # Cache expired, executes again
```

### Q5: Create a class decorator that adds logging to all methods.

**Answer:**
```python
import logging
from functools import wraps

logging.basicConfig(level=logging.INFO)

def log_methods(cls):
    """Class decorator that adds logging to all methods"""
    for attr_name in dir(cls):
        if not attr_name.startswith('_'):
            attr = getattr(cls, attr_name)
            if callable(attr):
                @wraps(attr)
                def wrapper(original_method):
                    def logged_method(self, *args, **kwargs):
                        logging.info(f"Calling {cls.__name__}.{original_method.__name__} with args={args}, kwargs={kwargs}")
                        result = original_method(self, *args, **kwargs)
                        logging.info(f"{cls.__name__}.{original_method.__name__} returned: {result}")
                        return result
                    return logged_method
                setattr(cls, attr_name, wrapper(attr))
    return cls

@log_methods
class Calculator:
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b
    
    def divide(self, a, b):
        return a / b

calc = Calculator()
calc.add(5, 3)
calc.multiply(4, 7)
```

### Q6: Explain metaclasses and create a metaclass that enforces method naming conventions.

**Answer:**
```python
class NamingConventionMeta(type):
    """Metaclass that enforces method naming conventions"""
    
    def __new__(cls, name, bases, namespace):
        # Check all methods follow naming convention
        for attr_name, attr_value in namespace.items():
            if callable(attr_value) and not attr_name.startswith('_'):
                if not attr_name.islower() or '_' in attr_name:
                    raise TypeError(
                        f"Method '{attr_name}' must be lowercase without underscores. "
                        f"Use camelCase or snake_case is not allowed."
                    )
        
        return super().__new__(cls, name, bases, namespace)

class MyClass(metaclass=NamingConventionMeta):
    def validMethod(self):  # Valid
        pass
    
    def invalid_method(self):  # Raises TypeError
        pass
    
    def AnotherMethod(self):  # Raises TypeError
        pass

# Usage
try:
    obj = MyClass()
except TypeError as e:
    print(f"Error: {e}")
```

### Q7: Create a decorator that retries a function on failure.

**Answer:**
```python
import time
from functools import wraps
from random import random

def retry(max_attempts=3, delay=1, backoff=2, exceptions=(Exception,)):
    """Decorator that retries function on failure"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay
            
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        raise
                    
                    print(f"Attempt {attempt} failed: {e}. Retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff
            
        return wrapper
    return decorator

@retry(max_attempts=3, delay=1, exceptions=(ValueError,))
def unreliable_function():
    if random() < 0.7:
        raise ValueError("Random failure!")
    return "Success!"

print(unreliable_function())
```

---

## Generators & Iterators

### Q8: Implement a generator that produces Fibonacci numbers and explain generator expressions vs list comprehensions.

**Answer:**
```python
def fibonacci_generator(n):
    """Generator that produces Fibonacci numbers"""
    a, b = 0, 1
    count = 0
    while count < n:
        yield a
        a, b = b, a + b
        count += 1

# Using generator
fib_gen = fibonacci_generator(10)
print("Fibonacci using generator:")
for num in fib_gen:
    print(num, end=" ")
print()

# Generator expression (lazy evaluation)
squares_gen = (x**2 for x in range(10))
print(f"Generator object: {squares_gen}")
print(f"First value: {next(squares_gen)}")

# List comprehension (eager evaluation)
squares_list = [x**2 for x in range(10)]
print(f"List: {squares_list}")

# Memory comparison
import sys
gen = (x for x in range(1000))
lst = [x for x in range(1000)]
print(f"Generator size: {sys.getsizeof(gen)} bytes")
print(f"List size: {sys.getsizeof(lst)} bytes")
```

### Q9: Create a coroutine using generators and implement a simple pipeline.

**Answer:**
```python
def producer():
    """Producer coroutine"""
    while True:
        value = yield
        print(f"Produced: {value}")

def filter_even(target):
    """Filter coroutine that only passes even numbers"""
    while True:
        value = yield
        if value % 2 == 0:
            target.send(value)

def consumer():
    """Consumer coroutine"""
    while True:
        value = yield
        print(f"Consumed: {value}")

# Setup pipeline
cons = consumer()
next(cons)  # Prime consumer

filt = filter_even(cons)
next(filt)  # Prime filter

# Send values through pipeline
for i in range(10):
    filt.send(i)
```

### Q10: Implement a generator that reads large files line by line efficiently.

**Answer:**
```python
def read_large_file(filepath, chunk_size=8192):
    """Generator that reads large files efficiently"""
    with open(filepath, 'r', encoding='utf-8') as file:
        buffer = ''
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                if buffer:
                    yield buffer
                break
            
            buffer += chunk
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                yield line

# Usage
# for line in read_large_file('large_file.txt'):
#     process(line)
```

---

## Concurrency & Parallelism

### Q11: Explain the difference between threading, multiprocessing, and asyncio. Provide examples.

**Answer:**
```python
import threading
import multiprocessing
import asyncio
import time

# 1. Threading (I/O-bound tasks)
def io_bound_task(name, delay):
    print(f"Thread {name} starting")
    time.sleep(delay)  # Simulating I/O
    print(f"Thread {name} finished")

def threading_example():
    threads = []
    for i in range(3):
        t = threading.Thread(target=io_bound_task, args=(i, 2))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()

# 2. Multiprocessing (CPU-bound tasks)
def cpu_bound_task(n):
    result = sum(i*i for i in range(n))
    return result

def multiprocessing_example():
    with multiprocessing.Pool(processes=4) as pool:
        results = pool.map(cpu_bound_task, [1000000] * 4)
    return results

# 3. Asyncio (I/O-bound concurrent tasks)
async def async_io_task(name, delay):
    print(f"Async task {name} starting")
    await asyncio.sleep(delay)
    print(f"Async task {name} finished")

async def asyncio_example():
    tasks = [async_io_task(i, 2) for i in range(3)]
    await asyncio.gather(*tasks)

# Run examples
print("Threading example:")
threading_example()

print("\nMultiprocessing example:")
multiprocessing_example()

print("\nAsyncio example:")
asyncio.run(asyncio_example())
```

### Q12: Implement a thread-safe counter using locks.

**Answer:**
```python
import threading

class ThreadSafeCounter:
    def __init__(self, initial_value=0):
        self._value = initial_value
        self._lock = threading.Lock()
    
    def increment(self):
        with self._lock:
            self._value += 1
            return self._value
    
    def decrement(self):
        with self._lock:
            self._value -= 1
            return self._value
    
    def get_value(self):
        with self._lock:
            return self._value

def worker(counter, iterations):
    for _ in range(iterations):
        counter.increment()

# Test thread safety
counter = ThreadSafeCounter()
threads = []

for _ in range(5):
    t = threading.Thread(target=worker, args=(counter, 1000))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print(f"Final counter value: {counter.get_value()}")  # Should be 5000
```

### Q13: Create an async context manager and explain async/await.

**Answer:**
```python
import asyncio
import aiohttp

class AsyncResource:
    """Async context manager example"""
    
    async def __aenter__(self):
        print("Acquiring resource...")
        await asyncio.sleep(0.1)  # Simulate async initialization
        self.resource = "Resource acquired"
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("Releasing resource...")
        await asyncio.sleep(0.1)  # Simulate async cleanup
        self.resource = None
        return False
    
    async def do_work(self):
        print(f"Working with {self.resource}")

async def main():
    async with AsyncResource() as resource:
        await resource.do_work()

# Run
asyncio.run(main())
```

---

## Advanced Data Structures

### Q14: Implement a custom dictionary that maintains insertion order and has a size limit.

**Answer:**
```python
from collections import OrderedDict

class LimitedOrderedDict(OrderedDict):
    """Dictionary that maintains order and has size limit"""
    
    def __init__(self, max_size=10, *args, **kwargs):
        self.max_size = max_size
        super().__init__(*args, **kwargs)
    
    def __setitem__(self, key, value):
        if key in self:
            # Move to end (most recently used)
            self.move_to_end(key)
        elif len(self) >= self.max_size:
            # Remove oldest item
            self.popitem(last=False)
        
        super().__setitem__(key, value)

# Usage
d = LimitedOrderedDict(max_size=3)
d['a'] = 1
d['b'] = 2
d['c'] = 3
print(dict(d))  # {'a': 1, 'b': 2, 'c': 3}

d['d'] = 4  # 'a' is removed
print(dict(d))  # {'b': 2, 'c': 3, 'd': 4}

d['b'] = 20  # 'b' moved to end
print(dict(d))  # {'c': 3, 'd': 4, 'b': 20}
```

### Q15: Implement a Trie data structure for prefix matching.

**Answer:**
```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
    
    def search(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end_of_word
    
    def starts_with(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return False
            node = node.children[char]
        return True
    
    def get_all_with_prefix(self, prefix):
        """Get all words with given prefix"""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        
        words = []
        self._collect_words(node, prefix, words)
        return words
    
    def _collect_words(self, node, prefix, words):
        if node.is_end_of_word:
            words.append(prefix)
        for char, child_node in node.children.items():
            self._collect_words(child_node, prefix + char, words)

# Usage
trie = Trie()
trie.insert("apple")
trie.insert("app")
trie.insert("application")
trie.insert("banana")

print(trie.search("app"))  # True
print(trie.starts_with("app"))  # True
print(trie.get_all_with_prefix("app"))  # ['app', 'apple', 'application']
```

---

## Python Internals

### Q16: Explain the MRO (Method Resolution Order) and demonstrate with examples.

**Answer:**
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

# MRO for D
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

### Q17: Explain `__slots__` and when to use it.

**Answer:**
```python
class WithoutSlots:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class WithSlots:
    __slots__ = ['x', 'y']
    
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Memory comparison
import sys

obj1 = WithoutSlots(1, 2)
obj2 = WithSlots(1, 2)

print(f"Without __slots__: {sys.getsizeof(obj1)} bytes")
print(f"With __slots__: {sys.getsizeof(obj2)} bytes")

# __slots__ prevents dynamic attribute creation
try:
    obj2.z = 3  # Raises AttributeError
except AttributeError as e:
    print(f"Error: {e}")

# Performance benefit
import timeit

def create_without_slots():
    return WithoutSlots(1, 2)

def create_with_slots():
    return WithSlots(1, 2)

print(f"Without slots: {timeit.timeit(create_without_slots, number=1000000):.4f}s")
print(f"With slots: {timeit.timeit(create_with_slots, number=1000000):.4f}s")
```

### Q18: Explain descriptor protocol and create a property descriptor.

**Answer:**
```python
class Property:
    """Custom property descriptor"""
    
    def __init__(self, getter=None, setter=None, deleter=None):
        self.getter = getter
        self.setter = setter
        self.deleter = deleter
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.getter is None:
            raise AttributeError("unreadable attribute")
        return self.getter(obj)
    
    def __set__(self, obj, value):
        if self.setter is None:
            raise AttributeError("can't set attribute")
        self.setter(obj, value)
    
    def __delete__(self, obj):
        if self.deleter is None:
            raise AttributeError("can't delete attribute")
        self.deleter(obj)
    
    def getter_func(self, func):
        self.getter = func
        return self
    
    def setter_func(self, func):
        self.setter = func
        return self

class Temperature:
    def __init__(self):
        self._celsius = 0
    
    @Property
    def celsius(self):
        return self._celsius
    
    @celsius.setter_func
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("Temperature below absolute zero")
        self._celsius = value
    
    @Property
    def fahrenheit(self):
        return self._celsius * 9/5 + 32
    
    @fahrenheit.setter_func
    def fahrenheit(self, value):
        self._celsius = (value - 32) * 5/9

temp = Temperature()
temp.celsius = 25
print(f"Celsius: {temp.celsius}, Fahrenheit: {temp.fahrenheit}")
temp.fahrenheit = 100
print(f"Celsius: {temp.celsius}, Fahrenheit: {temp.fahrenheit}")
```

---

## Design Patterns

### Q19: Implement the Observer pattern using Python's features.

**Answer:**
```python
class Observable:
    """Observable class using Python's features"""
    
    def __init__(self):
        self._observers = set()
    
    def attach(self, observer):
        self._observers.add(observer)
    
    def detach(self, observer):
        self._observers.discard(observer)
    
    def notify(self, event):
        for observer in self._observers:
            observer.update(event)

class Observer:
    def __init__(self, name):
        self.name = name
    
    def update(self, event):
        print(f"{self.name} received event: {event}")

# Usage
subject = Observable()
observer1 = Observer("Observer1")
observer2 = Observer("Observer2")

subject.attach(observer1)
subject.attach(observer2)

subject.notify("Event 1")
subject.detach(observer1)
subject.notify("Event 2")
```

### Q20: Implement a context manager for database transactions.

**Answer:**
```python
class DatabaseTransaction:
    """Context manager for database transactions"""
    
    def __init__(self, connection):
        self.connection = connection
        self.transaction_started = False
    
    def __enter__(self):
        self.connection.begin()
        self.transaction_started = True
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.transaction_started:
            if exc_type is None:
                self.connection.commit()
                print("Transaction committed")
            else:
                self.connection.rollback()
                print("Transaction rolled back")
        return False
    
    def execute(self, query):
        if not self.transaction_started:
            raise RuntimeError("Not in transaction")
        return self.connection.execute(query)

# Mock database connection
class MockConnection:
    def begin(self):
        print("BEGIN TRANSACTION")
    
    def commit(self):
        print("COMMIT")
    
    def rollback(self):
        print("ROLLBACK")
    
    def execute(self, query):
        print(f"EXECUTING: {query}")

# Usage
conn = MockConnection()

# Successful transaction
with DatabaseTransaction(conn) as tx:
    tx.execute("INSERT INTO users VALUES (1, 'John')")
    tx.execute("UPDATE users SET name='Jane' WHERE id=1")

# Failed transaction
try:
    with DatabaseTransaction(conn) as tx:
        tx.execute("INSERT INTO users VALUES (2, 'Bob')")
        raise ValueError("Error occurred")
except ValueError:
    pass
```

---

## Performance Optimization

### Q21: Explain and demonstrate memoization techniques.

**Answer:**
```python
from functools import lru_cache
import time

# Manual memoization
def memoize(func):
    cache = {}
    
    def wrapper(*args):
        if args in cache:
            return cache[args]
        result = func(*args)
        cache[args] = result
        return result
    
    return wrapper

@memoize
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Using lru_cache
@lru_cache(maxsize=128)
def expensive_function(n):
    time.sleep(0.1)  # Simulate expensive operation
    return n * 2

# Compare performance
start = time.time()
for i in range(10):
    expensive_function(5)
print(f"With cache: {time.time() - start:.4f}s")

# Clear cache
expensive_function.cache_clear()

# Custom cache with TTL
from functools import wraps
import time

def cache_with_ttl(ttl_seconds):
    def decorator(func):
        cache = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = str(args) + str(sorted(kwargs.items()))
            now = time.time()
            
            if key in cache:
                result, timestamp = cache[key]
                if now - timestamp < ttl_seconds:
                    return result
            
            result = func(*args, **kwargs)
            cache[key] = (result, now)
            return result
        
        return wrapper
    return decorator

@cache_with_ttl(ttl_seconds=5)
def get_data(key):
    return f"Data for {key}"

print(get_data("test"))
print(get_data("test"))  # Uses cache
```

### Q22: Optimize a function using Cython or explain when to use it.

**Answer:**
```python
# Pure Python version (slow)
def primes_python(n):
    primes = []
    for num in range(2, n):
        is_prime = True
        for i in range(2, int(num**0.5) + 1):
            if num % i == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(num)
    return primes

# Optimized Python version
def primes_optimized(n):
    if n < 2:
        return []
    sieve = [True] * n
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            sieve[i*i:n:i] = [False] * len(sieve[i*i:n:i])
    return [i for i in range(n) if sieve[i]]

# For Cython, you would create a .pyx file:
# primes_cython.pyx
"""
cdef list primes_cython(int n):
    cdef list sieve = [True] * n
    cdef int i, j
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, n, i):
                sieve[j] = False
    return [i for i in range(n) if sieve[i]]
"""

import timeit
n = 10000

print(f"Python: {timeit.timeit(lambda: primes_python(n), number=1):.4f}s")
print(f"Optimized: {timeit.timeit(lambda: primes_optimized(n), number=1):.4f}s")
```

---

## Error Handling & Debugging

### Q23: Create a custom exception hierarchy and demonstrate exception chaining.

**Answer:**
```python
class BaseAPIException(Exception):
    """Base exception for API errors"""
    def __init__(self, message, status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ValidationError(BaseAPIException):
    """Validation error"""
    def __init__(self, message):
        super().__init__(message, status_code=400)

class AuthenticationError(BaseAPIException):
    """Authentication error"""
    def __init__(self, message):
        super().__init__(message, status_code=401)

class NotFoundError(BaseAPIException):
    """Not found error"""
    def __init__(self, message):
        super().__init__(message, status_code=404)

# Exception chaining
def process_data(data):
    try:
        if not data:
            raise ValueError("Data is empty")
        result = int(data)
        return result * 2
    except ValueError as e:
        raise ValidationError("Invalid data format") from e

try:
    process_data("")
except BaseAPIException as e:
    print(f"Error: {e.message}, Status: {e.status_code}")
    print(f"Caused by: {e.__cause__}")
```

### Q24: Implement a decorator that handles exceptions and retries.

**Answer:**
```python
from functools import wraps
import time
import logging

logging.basicConfig(level=logging.INFO)

def handle_exceptions(*exception_types, default_return=None, log_error=True):
    """Decorator that handles specific exceptions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception_types as e:
                if log_error:
                    logging.error(f"Error in {func.__name__}: {e}")
                return default_return
        return wrapper
    return decorator

@handle_exceptions(ValueError, ZeroDivisionError, default_return=0, log_error=True)
def divide(a, b):
    return a / b

print(divide(10, 2))  # 5.0
print(divide(10, 0))  # 0 (handled)
print(divide("10", 2))  # 0 (handled)
```

---

## Advanced OOP Concepts

### Q25: Implement multiple inheritance with mixins.

**Answer:**
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

class User(JSONSerializableMixin, XMLSerializableMixin, LoggableMixin):
    def __init__(self, name, email):
        self.name = name
        self.email = email
    
    def greet(self):
        self.log(f"User {self.name} greeted")
        return f"Hello, {self.name}!"

user = User("John", "john@example.com")
print(user.greet())
print(user.to_json())
print(user.to_xml())
```

### Q26: Explain and demonstrate abstract base classes.

**Answer:**
```python
from abc import ABC, abstractmethod, abstractproperty

class Shape(ABC):
    """Abstract base class for shapes"""
    
    @abstractmethod
    def area(self):
        """Calculate area of the shape"""
        pass
    
    @abstractmethod
    def perimeter(self):
        """Calculate perimeter of the shape"""
        pass
    
    @abstractproperty
    def name(self):
        """Name of the shape"""
        pass
    
    def describe(self):
        return f"{self.name}: Area={self.area()}, Perimeter={self.perimeter()}"

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    @property
    def name(self):
        return "Rectangle"
    
    def area(self):
        return self.width * self.height
    
    def perimeter(self):
        return 2 * (self.width + self.height)

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    
    @property
    def name(self):
        return "Circle"
    
    def area(self):
        return 3.14159 * self.radius ** 2
    
    def perimeter(self):
        return 2 * 3.14159 * self.radius

# Usage
rect = Rectangle(5, 3)
circle = Circle(4)

print(rect.describe())
print(circle.describe())

# Cannot instantiate abstract class
try:
    shape = Shape()  # Raises TypeError
except TypeError as e:
    print(f"Error: {e}")
```

---

## Summary

This document covers advanced Python interview topics with practical examples. Key areas include:

1. **Memory Management**: Reference counting, garbage collection, memory views
2. **Advanced Features**: Decorators, metaclasses, descriptors
3. **Concurrency**: Threading, multiprocessing, asyncio
4. **Data Structures**: Custom implementations, Trie, OrderedDict
5. **Python Internals**: MRO, `__slots__`, descriptor protocol
6. **Design Patterns**: Observer, Context Manager, Factory
7. **Performance**: Memoization, optimization techniques
8. **Error Handling**: Custom exceptions, exception chaining
9. **OOP**: Abstract classes, mixins, multiple inheritance

Each topic includes code examples that demonstrate practical usage and common interview scenarios.

