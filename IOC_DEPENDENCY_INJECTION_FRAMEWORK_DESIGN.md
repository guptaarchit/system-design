# IoC/Dependency Injection Framework System Design

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Core Components](#core-components)
5. [API Design](#api-design)
6. [Bean Lifecycle Management](#bean-lifecycle-management)
7. [Dependency Resolution](#dependency-resolution)
8. [Scope Management](#scope-management)
9. [AOP (Aspect-Oriented Programming)](#aop-aspect-oriented-programming)
10. [Configuration Management](#configuration-management)
11. [Performance Optimization](#performance-optimization)
12. [Scalability Considerations](#scalability-considerations)
13. [Security](#security)
14. [Monitoring & Analytics](#monitoring--analytics)
15. [Deployment Strategy](#deployment-strategy)
16. [Failure Scenarios & Handling](#failure-scenarios--handling)
17. [Trade-offs & Design Decisions](#trade-offs--design-decisions)
18. [Interview Discussion Points](#interview-discussion-points)

---

## Overview

An Inversion of Control (IoC) and Dependency Injection (DI) framework that manages object creation, dependency resolution, and lifecycle management. The framework must support multiple scopes, circular dependency detection, and provide high performance.

**Key Features:**
- Automatic dependency injection
- Multiple bean scopes (singleton, prototype, request, session)
- Circular dependency detection and resolution
- AOP support (aspects, interceptors)
- Configuration via annotations and XML
- Lazy and eager initialization
- Bean lifecycle callbacks

---

## Requirements

### Functional Requirements

1. **Bean Registration**
   - Register beans via annotations (@Component, @Service, @Repository)
   - Register beans via XML configuration
   - Register beans programmatically
   - Support for factory methods

2. **Dependency Injection**
   - Constructor injection
   - Setter injection
   - Field injection
   - Interface-based injection

3. **Bean Scopes**
   - Singleton (one instance per container)
   - Prototype (new instance each time)
   - Request (one per HTTP request)
   - Session (one per HTTP session)

4. **Lifecycle Management**
   - Bean initialization callbacks
   - Bean destruction callbacks
   - Post-construct and pre-destroy hooks

5. **AOP Support**
   - Method interception
   - Aspect weaving
   - Transaction management
   - Logging aspects

### Non-Functional Requirements

1. **Performance**
   - Bean creation: < 1ms (cached)
   - Dependency resolution: < 0.1ms
   - Container startup: < 5 seconds

2. **Memory Efficiency**
   - Efficient bean storage
   - Garbage collection friendly
   - Memory leak prevention

3. **Thread Safety**
   - Thread-safe singleton creation
   - Thread-safe dependency resolution
   - Concurrent bean access

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Code                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │@Service  │  │@Component│  │@Repository│ │@Controller│  │
│  │ Classes  │  │ Classes  │  │ Classes  │  │ Classes  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│              IoC Container                                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Bean    │  │Dependency│  │  Scope    │  │  AOP     │   │
│  │Registry  │  │Resolver  │  │ Manager  │  │  Proxy   │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              Bean Storage                                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Singleton │  │Prototype │  │ Request  │  │ Session  │   │
│  │  Cache   │  │ Factory  │  │  Cache   │  │  Cache   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Component Details

#### 1. Bean Registry
- **Responsibilities**:
  - Register bean definitions
  - Store bean metadata
  - Index beans by type and name

#### 2. Dependency Resolver
- **Responsibilities**:
  - Resolve dependencies
  - Detect circular dependencies
  - Handle optional dependencies

#### 3. Scope Manager
- **Responsibilities**:
  - Manage bean scopes
  - Create/destroy beans per scope
  - Cleanup scoped beans

#### 4. AOP Proxy
- **Responsibilities**:
  - Create proxy objects
   - Intercept method calls
   - Apply aspects

---

## Core Components

### Bean Definition

```python
class BeanDefinition:
    def __init__(self):
        self.name = None  # Bean name
        self.bean_class = None  # Class type
        self.scope = 'singleton'  # Scope
        self.dependencies = []  # List of dependency names/types
        self.factory_method = None  # Factory method if any
        self.init_method = None  # Post-construct method
        self.destroy_method = None  # Pre-destroy method
        self.lazy = False  # Lazy initialization
        self.primary = False  # Primary bean for type
```

### Bean Container

```python
class IoCContainer:
    def __init__(self):
        self.bean_definitions = {}  # name -> BeanDefinition
        self.singleton_cache = {}  # name -> instance
        self.type_index = {}  # type -> [bean_names]
        self.creation_stack = []  # For circular dependency detection
    
    def register_bean(self, name, bean_class, scope='singleton', **kwargs):
        definition = BeanDefinition()
        definition.name = name
        definition.bean_class = bean_class
        definition.scope = scope
        # ... set other properties
        
        self.bean_definitions[name] = definition
        
        # Index by type
        if bean_class not in self.type_index:
            self.type_index[bean_class] = []
        self.type_index[bean_class].append(name)
    
    def get_bean(self, name_or_type):
        # Resolve bean name
        bean_name = self.resolve_bean_name(name_or_type)
        
        # Get bean definition
        definition = self.bean_definitions[bean_name]
        
        # Check scope and return appropriate instance
        if definition.scope == 'singleton':
            return self.get_singleton(bean_name, definition)
        elif definition.scope == 'prototype':
            return self.create_prototype(definition)
        # ... other scopes
    
    def get_singleton(self, name, definition):
        if name in self.singleton_cache:
            return self.singleton_cache[name]
        
        # Create instance
        instance = self.create_bean(definition)
        self.singleton_cache[name] = instance
        return instance
    
    def create_bean(self, definition):
        # Check for circular dependency
        if definition.name in self.creation_stack:
            raise CircularDependencyError(f"Circular dependency detected: {self.creation_stack}")
        
        self.creation_stack.append(definition.name)
        
        try:
            # Resolve dependencies
            dependencies = self.resolve_dependencies(definition)
            
            # Create instance
            if definition.factory_method:
                instance = definition.factory_method(*dependencies)
            else:
                instance = definition.bean_class(*dependencies)
            
            # Call init method
            if definition.init_method:
                getattr(instance, definition.init_method)()
            
            return instance
        finally:
            self.creation_stack.pop()
    
    def resolve_dependencies(self, definition):
        dependencies = []
        for dep in definition.dependencies:
            if isinstance(dep, str):
                # Dependency by name
                dep_bean = self.get_bean(dep)
            else:
                # Dependency by type
                dep_bean = self.get_bean_by_type(dep)
            dependencies.append(dep_bean)
        return dependencies
```

---

## API Design

### Annotation-Based Configuration

**Service Class:**
```python
@Service
class UserService:
    def __init__(self, user_repository: UserRepository, email_service: EmailService):
        self.user_repository = user_repository
        self.email_service = email_service
    
    @PostConstruct
    def init(self):
        # Initialization logic
        pass
    
    @PreDestroy
    def cleanup(self):
        # Cleanup logic
        pass
```

**Repository Class:**
```python
@Repository
class UserRepository:
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
```

**Component Class:**
```python
@Component
class EmailService:
    def send_email(self, to, subject, body):
        # Send email
        pass
```

### Programmatic Configuration

```python
container = IoCContainer()

# Register beans
container.register_bean('userService', UserService, scope='singleton')
container.register_bean('userRepository', UserRepository, scope='singleton')
container.register_bean('emailService', EmailService, scope='singleton')

# Set dependencies
container.set_dependency('userService', 'userRepository')
container.set_dependency('userService', 'emailService')
container.set_dependency('userRepository', 'dbConnection')

# Get bean
user_service = container.get_bean('userService')
# or
user_service = container.get_bean(UserService)
```

---

## Bean Lifecycle Management

### Lifecycle Phases

1. **Instantiation**: Create bean instance
2. **Dependency Injection**: Inject dependencies
3. **Initialization**: Call @PostConstruct methods
4. **Ready**: Bean is ready for use
5. **Destruction**: Call @PreDestroy methods

### Implementation

```python
class BeanLifecycleManager:
    def initialize_bean(self, bean, definition):
        # Call post-construct methods
        if definition.init_method:
            method = getattr(bean, definition.init_method)
            method()
        
        # Call @PostConstruct annotated methods
        for method_name in dir(bean):
            method = getattr(bean, method_name)
            if hasattr(method, '__post_construct__'):
                method()
    
    def destroy_bean(self, bean, definition):
        # Call pre-destroy methods
        if definition.destroy_method:
            method = getattr(bean, definition.destroy_method)
            method()
        
        # Call @PreDestroy annotated methods
        for method_name in dir(bean):
            method = getattr(bean, method_name)
            if hasattr(method, '__pre_destroy__'):
                method()
```

---

## Dependency Resolution

### Resolution Strategies

**1. By Name:**
- Resolve dependency by bean name
- Explicit and clear

**2. By Type:**
- Resolve dependency by type/interface
- More flexible
- Requires @Primary for multiple implementations

**3. By Qualifier:**
- Resolve by qualifier annotation
- For multiple implementations of same interface

### Circular Dependency Detection

**Detection Algorithm:**
```python
def detect_circular_dependency(self, bean_name, visited=None, rec_stack=None):
    if visited is None:
        visited = set()
    if rec_stack is None:
        rec_stack = set()
    
    visited.add(bean_name)
    rec_stack.add(bean_name)
    
    definition = self.bean_definitions[bean_name]
    for dep in definition.dependencies:
        if dep not in visited:
            if self.detect_circular_dependency(dep, visited, rec_stack):
                return True
        elif dep in rec_stack:
            return True  # Circular dependency found
    
    rec_stack.remove(bean_name)
    return False
```

**Resolution Strategies:**
1. **Lazy Injection**: Inject proxy instead of actual bean
2. **Setter Injection**: Use setter instead of constructor
3. **Refactoring**: Break circular dependency

---

## Scope Management

### Singleton Scope

**Implementation:**
- One instance per container
- Cached after first creation
- Thread-safe creation

### Prototype Scope

**Implementation:**
- New instance each time
- No caching
- Caller responsible for lifecycle

### Request Scope

**Implementation:**
- One instance per HTTP request
- Stored in request context
- Cleaned up after request

### Session Scope

**Implementation:**
- One instance per HTTP session
- Stored in session
- Cleaned up on session expiry

---

## AOP (Aspect-Oriented Programming)

### Aspect Implementation

```python
@Aspect
class LoggingAspect:
    @Around("@annotation(Loggable)")
    def log_method(self, join_point):
        method_name = join_point.method_name
        print(f"Entering {method_name}")
        
        try:
            result = join_point.proceed()
            print(f"Exiting {method_name}")
            return result
        except Exception as e:
            print(f"Exception in {method_name}: {e}")
            raise

@Aspect
class TransactionAspect:
    @Around("@annotation(Transactional)")
    def manage_transaction(self, join_point):
        transaction = self.begin_transaction()
        try:
            result = join_point.proceed()
            transaction.commit()
            return result
        except Exception as e:
            transaction.rollback()
            raise
```

### Proxy Creation

```python
class AOPProxy:
    def create_proxy(self, target, aspects):
        # Create dynamic proxy
        proxy = DynamicProxy(target)
        
        # Add aspect interceptors
        for aspect in aspects:
            proxy.add_interceptor(aspect)
        
        return proxy
```

---

## Configuration Management

### Annotation Scanning

```python
class ComponentScanner:
    def scan_package(self, package_name):
        # Scan package for annotations
        classes = self.get_classes_in_package(package_name)
        
        for cls in classes:
            if self.has_annotation(cls, Component):
                self.register_component(cls)
            elif self.has_annotation(cls, Service):
                self.register_service(cls)
            elif self.has_annotation(cls, Repository):
                self.register_repository(cls)
```

### XML Configuration

```xml
<beans>
    <bean id="userService" class="com.example.UserService" scope="singleton">
        <constructor-arg ref="userRepository"/>
        <constructor-arg ref="emailService"/>
    </bean>
    
    <bean id="userRepository" class="com.example.UserRepository">
        <constructor-arg ref="dbConnection"/>
    </bean>
</beans>
```

---

## Performance Optimization

### Bean Caching

- Cache singleton beans
- Cache bean definitions
- Cache resolved dependencies

### Lazy Initialization

- Defer bean creation until first use
- Reduce startup time
- Trade-off: First access slower

### Proxy Optimization

- Cache proxy classes
- Reuse proxy instances
- Minimize reflection overhead

---

## Scalability Considerations

### Container Scaling

- Multiple containers per application
- Container per module/package
- Hierarchical containers

### Memory Management

- Efficient bean storage
- Weak references for prototypes
- Garbage collection friendly

---

## Failure Scenarios & Handling

### 1. Circular Dependency

**Scenario:** Bean A depends on B, B depends on A.

**Mitigation:**
- Detect during registration
- Use lazy injection
- Refactor to break cycle

### 2. Missing Dependency

**Scenario:** Required dependency not found.

**Mitigation:**
- Validate during registration
- Support optional dependencies
- Clear error messages

### 3. Bean Creation Failure

**Scenario:** Exception during bean creation.

**Mitigation:**
- Rollback created dependencies
- Clear error messages
- Retry mechanism (optional)

---

## Trade-offs & Design Decisions

### 1. Eager vs Lazy Initialization

**Decision:** Configurable (eager default, lazy optional).

**Trade-offs:**

| Approach | Pros | Cons |
|----------|------|------|
| **Eager** | Fast first access | Slower startup |
| **Lazy** | Fast startup | Slower first access |

### 2. Reflection vs Code Generation

**Decision:** Reflection (simpler) with caching.

**Trade-offs:**

| Approach | Pros | Cons |
|----------|------|------|
| **Reflection** | Simple, flexible | Slower |
| **Code Gen** | Faster | Complex |

---

## High-Level Design (HLD)

### System Overview

The IoC/DI framework follows a layered architecture:

1. **Application Layer**: User code with annotations (@Component, @Service, etc.)
2. **Container Layer**: IoC Container managing bean lifecycle
3. **Storage Layer**: Bean storage (singleton cache, prototype factory, scoped caches)
4. **Configuration Layer**: Annotation scanning, XML parsing, programmatic configuration

### Component Architecture

**Core Components:**
- **Bean Registry**: Stores bean definitions and metadata
- **Dependency Resolver**: Resolves dependencies, detects circular dependencies
- **Scope Manager**: Manages bean scopes (singleton, prototype, request, session)
- **Lifecycle Manager**: Handles initialization and destruction callbacks
- **AOP Proxy Factory**: Creates proxies for aspect weaving
- **Configuration Scanner**: Scans packages for annotated classes

**Data Flow:**
```
Application Code → Container → Bean Registry → Dependency Resolver → 
Scope Manager → Bean Storage → Return Instance
```

---

## Low-Level Design (LLD)

### Bean Registry Implementation

```python
class BeanRegistry:
    def __init__(self):
        self.definitions = {}  # name -> BeanDefinition
        self.type_index = {}  # type -> [bean_names]
        self.name_to_type = {}  # name -> type
    
    def register_bean(self, name: str, bean_class: type, scope: str = 'singleton'):
        definition = BeanDefinition()
        definition.name = name
        definition.bean_class = bean_class
        definition.scope = scope
        
        # Extract dependencies from constructor
        definition.dependencies = self._extract_dependencies(bean_class)
        
        self.definitions[name] = definition
        
        # Index by type
        if bean_class not in self.type_index:
            self.type_index[bean_class] = []
        self.type_index[bean_class].append(name)
        self.name_to_type[name] = bean_class
    
    def _extract_dependencies(self, bean_class: type) -> list:
        dependencies = []
        import inspect
        
        # Get constructor signature
        sig = inspect.signature(bean_class.__init__)
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            # Check for type hints
            if param.annotation != inspect.Parameter.empty:
                dependencies.append(param.annotation)
            else:
                # Try to infer from parameter name
                dependencies.append(param_name)
        
        return dependencies
```

### Dependency Resolver with Circular Dependency Detection

```python
class DependencyResolver:
    def __init__(self, registry: BeanRegistry):
        self.registry = registry
        self.creation_stack = []  # Track creation path
        self.resolving = set()  # Currently resolving beans
    
    def resolve_dependencies(self, definition: BeanDefinition) -> list:
        dependencies = []
        
        for dep in definition.dependencies:
            if isinstance(dep, type):
                # Dependency by type
                bean = self._resolve_by_type(dep, definition.name)
            else:
                # Dependency by name
                bean = self._resolve_by_name(dep, definition.name)
            
            dependencies.append(bean)
        
        return dependencies
    
    def _resolve_by_type(self, dep_type: type, requesting_bean: str):
        # Check for circular dependency
        if dep_type in self.resolving:
            raise CircularDependencyError(
                f"Circular dependency detected: {self.creation_stack} -> {dep_type}"
            )
        
        # Find bean by type
        candidates = self.registry.type_index.get(dep_type, [])
        
        if not candidates:
            raise BeanNotFoundException(f"No bean found for type: {dep_type}")
        
        if len(candidates) > 1:
            # Multiple candidates, check for @Primary
            primary = [c for c in candidates if self.registry.definitions[c].primary]
            if primary:
                candidates = primary
            else:
                raise AmbiguousBeanException(
                    f"Multiple beans found for type {dep_type}: {candidates}"
                )
        
        bean_name = candidates[0]
        return self._resolve_by_name(bean_name, requesting_bean)
    
    def _resolve_by_name(self, bean_name: str, requesting_bean: str):
        if bean_name in self.resolving:
            raise CircularDependencyError(
                f"Circular dependency: {self.creation_stack} -> {bean_name}"
            )
        
        definition = self.registry.definitions[bean_name]
        
        # Add to resolving set
        self.resolving.add(bean_name)
        self.creation_stack.append(bean_name)
        
        try:
            # Get bean from container
            container = self.registry.container
            bean = container.get_bean(bean_name)
            return bean
        finally:
            self.resolving.remove(bean_name)
            self.creation_stack.pop()
```

### Scope Manager Implementation

```python
class ScopeManager:
    def __init__(self):
        self.singleton_cache = {}  # name -> instance
        self.request_cache = {}  # request_id -> {name -> instance}
        self.session_cache = {}  # session_id -> {name -> instance}
        self.locks = {}  # name -> Lock
    
    def get_bean(self, name: str, definition: BeanDefinition, context: dict = None):
        if definition.scope == 'singleton':
            return self._get_singleton(name, definition)
        elif definition.scope == 'prototype':
            return self._create_prototype(definition)
        elif definition.scope == 'request':
            return self._get_request_scope(name, definition, context)
        elif definition.scope == 'session':
            return self._get_session_scope(name, definition, context)
        else:
            raise ValueError(f"Unknown scope: {definition.scope}")
    
    def _get_singleton(self, name: str, definition: BeanDefinition):
        # Double-checked locking pattern
        if name in self.singleton_cache:
            return self.singleton_cache[name]
        
        # Acquire lock
        if name not in self.locks:
            self.locks[name] = threading.Lock()
        
        with self.locks[name]:
            # Double-check again
            if name in self.singleton_cache:
                return self.singleton_cache[name]
            
            # Create instance
            instance = self._create_instance(definition)
            self.singleton_cache[name] = instance
            return instance
    
    def _create_prototype(self, definition: BeanDefinition):
        # Always create new instance
        return self._create_instance(definition)
    
    def _get_request_scope(self, name: str, definition: BeanDefinition, context: dict):
        request_id = context.get('request_id')
        if not request_id:
            raise ValueError("Request scope requires request_id in context")
        
        if request_id not in self.request_cache:
            self.request_cache[request_id] = {}
        
        if name not in self.request_cache[request_id]:
            instance = self._create_instance(definition)
            self.request_cache[request_id][name] = instance
        
        return self.request_cache[request_id][name]
    
    def cleanup_request_scope(self, request_id: str):
        """Cleanup request-scoped beans after request completes"""
        if request_id in self.request_cache:
            # Call pre-destroy methods
            for name, instance in self.request_cache[request_id].items():
                definition = self.registry.definitions.get(name)
                if definition and definition.destroy_method:
                    getattr(instance, definition.destroy_method)()
            
            del self.request_cache[request_id]
```

### AOP Proxy Factory

```python
class AOPProxyFactory:
    def __init__(self):
        self.aspects = []  # List of aspect definitions
    
    def create_proxy(self, target: object, target_class: type) -> object:
        # Check if target needs proxying
        if not self._needs_proxy(target_class):
            return target
        
        # Create dynamic proxy
        proxy = DynamicProxy(target)
        
        # Add aspect interceptors
        for aspect in self.aspects:
            if aspect.matches(target_class):
                proxy.add_interceptor(aspect.create_interceptor())
        
        return proxy
    
    def _needs_proxy(self, target_class: type) -> bool:
        # Check if class has methods matching aspect pointcuts
        for aspect in self.aspects:
            if aspect.matches(target_class):
                return True
        return False

class DynamicProxy:
    def __init__(self, target: object):
        self.target = target
        self.interceptors = []
    
    def add_interceptor(self, interceptor):
        self.interceptors.append(interceptor)
    
    def __getattr__(self, name):
        attr = getattr(self.target, name)
        
        if callable(attr):
            # Wrap method with interceptors
            def wrapped(*args, **kwargs):
                join_point = JoinPoint(self.target, name, args, kwargs)
                
                # Execute interceptors (around advice)
                for interceptor in self.interceptors:
                    if interceptor.matches(join_point):
                        return interceptor.around(join_point)
                
                # No matching interceptor, call original method
                return attr(*args, **kwargs)
            
            return wrapped
        
        return attr
```

---

## Fault Tolerance

### Bean Creation Failure Handling

**Retry Logic:**
- Retry bean creation on transient failures
- Exponential backoff for retries
- Max retry attempts: 3
- Fail fast on permanent errors

**Error Recovery:**
```python
class ResilientBeanFactory:
    def create_bean(self, definition: BeanDefinition, retries: int = 3):
        for attempt in range(retries):
            try:
                return self._create_bean_internal(definition)
            except TransientError as e:
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise
            except PermanentError as e:
                raise  # Don't retry permanent errors
```

### Dependency Resolution Resilience

**Fallback Mechanisms:**
- Optional dependencies: Use None if not found
- Default values: Use provided defaults
- Factory methods: Use factory if direct creation fails

**Graceful Degradation:**
```python
def resolve_dependency(self, dep_type: type, optional: bool = False):
    try:
        return self._resolve_by_type(dep_type)
    except BeanNotFoundException:
        if optional:
            return None
        raise
```

### Container Initialization Resilience

**Partial Initialization:**
- Continue initialization even if some beans fail
- Log failures but don't stop container startup
- Provide health check endpoint

**Startup Validation:**
- Validate all required beans exist
- Check for circular dependencies before startup
- Verify scope configurations

---

## Optimizations

### Bean Caching Strategy

**Multi-Level Caching:**
1. **Definition Cache**: Cache bean definitions (immutable)
2. **Singleton Cache**: Cache singleton instances
3. **Proxy Cache**: Cache generated proxies
4. **Metadata Cache**: Cache reflection metadata

**Cache Invalidation:**
- Definitions: Never invalidated (immutable)
- Singletons: Never invalidated (lifetime of container)
- Proxies: Invalidated on aspect changes
- Metadata: Invalidated on class reload (development)

### Reflection Optimization

**Metadata Caching:**
```python
class ReflectionCache:
    def __init__(self):
        self.constructor_cache = {}  # class -> constructor
        self.field_cache = {}  # class -> fields
        self.method_cache = {}  # class -> methods
        self.annotation_cache = {}  # class -> annotations
    
    def get_constructor(self, cls: type):
        if cls not in self.constructor_cache:
            self.constructor_cache[cls] = inspect.signature(cls.__init__)
        return self.constructor_cache[cls]
```

**Lazy Reflection:**
- Only reflect when needed
- Cache reflection results
- Use code generation for hot paths (optional)

### Lazy Initialization Optimization

**Lazy Bean Creation:**
- Defer creation until first access
- Reduce startup time
- Trade-off: First access slower

**Pre-warming:**
- Optionally pre-create critical singletons
- Balance startup time vs first-access latency

### Memory Optimization

**Weak References:**
- Use weak references for prototype beans
- Allow garbage collection of unused prototypes
- Prevent memory leaks

**Object Pooling:**
- Pool frequently created prototypes
- Reduce allocation overhead
- Trade-off: Memory vs CPU

---

## Failure Safety

### Bean Creation Failures

**Scenario: Constructor Throws Exception**
- **Impact**: Bean not created, dependent beans fail
- **Mitigation**:
  - Catch exceptions during creation
  - Log error with context
  - Mark bean as failed
  - Prevent dependent beans from being created
- **Recovery**:
  - Retry on transient errors
  - Provide fallback bean (if configured)
  - Report error to monitoring system

**Scenario: Circular Dependency Detected**
- **Impact**: Container cannot initialize
- **Mitigation**:
  - Detect during dependency resolution
  - Report clear error message with cycle path
  - Suggest solutions (lazy injection, refactoring)
- **Recovery**:
  - Use lazy injection to break cycle
  - Refactor dependencies
  - Use setter injection instead of constructor

### Dependency Resolution Failures

**Scenario: Required Dependency Not Found**
- **Impact**: Bean cannot be created
- **Mitigation**:
  - Validate dependencies during registration
  - Check for optional dependencies
  - Provide clear error messages
- **Recovery**:
  - Register missing bean
  - Mark dependency as optional
  - Provide default implementation

**Scenario: Multiple Candidates for Type**
- **Impact**: Ambiguous dependency resolution
- **Mitigation**:
  - Use @Primary annotation
  - Use @Qualifier annotation
  - Provide explicit bean name
- **Recovery**:
  - Add @Primary to preferred bean
  - Use qualifier in injection point
  - Specify bean name explicitly

### Scope Management Failures

**Scenario: Request Scope Without Context**
- **Impact**: Cannot create request-scoped bean
- **Mitigation**:
  - Validate context before creating
  - Provide default scope fallback
  - Clear error message
- **Recovery**:
  - Provide request context
  - Change scope to singleton/prototype
  - Use thread-local storage

**Scenario: Session Expired**
- **Impact**: Session-scoped beans lost
- **Mitigation**:
  - Detect expired sessions
  - Cleanup expired beans
  - Handle gracefully
- **Recovery**:
  - Create new session
  - Recreate beans in new session
  - Persist critical state

### Container Shutdown Failures

**Scenario: Pre-Destroy Method Throws Exception**
- **Impact**: Other beans may not be destroyed
- **Mitigation**:
  - Catch exceptions in destroy methods
  - Continue destroying other beans
  - Log errors
- **Recovery**:
  - Fix destroy method
  - Handle exceptions gracefully
  - Ensure cleanup happens

---

## Scalability

### Container Scaling

**Multiple Containers:**
- One container per application module
- Hierarchical containers (parent-child)
- Independent scaling per module

**Container Per Thread:**
- Thread-local containers for request scope
- Isolated bean instances per thread
- Thread-safe singleton access

### Memory Scaling

**Efficient Storage:**
- Compact bean definition storage
- Weak references for prototypes
- Lazy loading of bean metadata

**Memory Limits:**
- Limit singleton cache size
- Evict least-recently-used singletons (optional)
- Monitor memory usage

### Performance Scaling

**Parallel Initialization:**
- Initialize independent beans in parallel
- Use dependency graph for ordering
- Reduce startup time

**Batch Operations:**
- Batch bean registration
- Batch dependency resolution
- Optimize reflection calls

### Horizontal Scaling Considerations

**Stateless Design:**
- Container is stateless (except singletons)
- Can run multiple instances
- Share singleton state via external storage (optional)

**Distributed Containers:**
- Multiple containers across nodes
- Shared singleton registry (Redis, etc.)
- Event-driven synchronization

---

## Interview Discussion Points

### Key Questions to Address

1. **"How do you detect circular dependencies?"**
   - **Answer**: 
     - DFS with recursion stack
     - Track creation stack
     - Detect cycles during resolution

2. **"How do you ensure thread safety?"**
   - **Answer**:
     - Double-checked locking for singletons
     - Thread-local storage for request scope
     - Synchronized creation

3. **"How do you optimize performance?"**
   - **Answer**:
     - Cache singleton beans
     - Cache bean definitions
     - Minimize reflection usage
     - Lazy initialization

---

## References

- [Spring Framework](https://spring.io/projects/spring-framework)
- [Guice](https://github.com/google/guice)
- [Dagger](https://dagger.dev/)

