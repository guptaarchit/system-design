# 146. LRU Cache
# Medium
# Topics
# conpanies icon
# Companies
# Design a data structure that follows the constraints of a Least Recently Used (LRU) cache.

# Implement the LRUCache class:

# LRUCache(int capacity) Initialize the LRU cache with positive size capacity.
# int get(int key) Return the value of the key if the key exists, otherwise return -1.
# void put(int key, int value) Update the value of the key if the key exists. Otherwise, add the key-value pair to the cache. If the number of keys exceeds the capacity from this operation, evict the least recently used key.
# The functions get and put must each run in O(1) average time complexity.

 

# Example 1:

# Input
# ["LRUCache", "put", "put", "get", "put", "get", "put", "get", "get", "get"]
# [[2], [1, 1], [2, 2], [1], [3, 3], [2], [4, 4], [1], [3], [4]]
# Output
# [null, null, null, 1, null, -1, null, -1, 3, 4]

# Explanation
# LRUCache lRUCache = new LRUCache(2);
# lRUCache.put(1, 1); // cache is {1=1}
# lRUCache.put(2, 2); // cache is {1=1, 2=2}
# lRUCache.get(1);    // return 1
# lRUCache.put(3, 3); // LRU key was 2, evicts key 2, cache is {1=1, 3=3}
# lRUCache.get(2);    // returns -1 (not found)
# lRUCache.put(4, 4); // LRU key was 1, evicts key 1, cache is {4=4, 3=3}
# lRUCache.get(1);    // return -1 (not found)
# lRUCache.get(3);    // return 3
# lRUCache.get(4);    // return 4

# ============================================================================
# APPROACH 1: Using OrderedDict (Simpler - Python built-in)
# ============================================================================
# OrderedDict maintains insertion order and allows O(1) move_to_end operation
# Under the hood, it uses a doubly linked list, but we don't need to implement it

from collections import OrderedDict

class LRUCacheOrderedDict:
    """
    Simpler implementation using Python's OrderedDict.
    OrderedDict internally uses a doubly linked list, so we get O(1) operations
    without implementing the linked list ourselves.
    """
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()
    
    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            # Update existing key and move to end
            self.cache[key] = value
            self.cache.move_to_end(key)
        else:
            # New key
            if len(self.cache) >= self.capacity:
                # Remove least recently used (first item)
                self.cache.popitem(last=False)
            self.cache[key] = value


# ============================================================================
# APPROACH 2: Manual Doubly Linked List (More control, interview-style)
# ============================================================================
# Why can't we use just a single last_used_key variable?
# 
# THE PROBLEM: We need to know the LEAST recently used key to evict it,
# but last_used_key only tells us the MOST recently used key.
#
# CONCRETE COUNTEREXAMPLE:
#   Capacity = 2
#   
#   Step 1: put(1, 1)
#     cache = {1: 1}
#     last_used_key = 1  ✓ We know 1 is most recent
#   
#   Step 2: put(2, 2)
#     cache = {1: 1, 2: 2}
#     last_used_key = 2  ✓ We know 2 is most recent
#   
#   Step 3: get(1)
#     cache = {1: 1, 2: 2}
#     last_used_key = 1  ✓ We know 1 is most recent
#     BUT: Which key is LEAST recent? We don't know! ❌
#   
#   Step 4: put(3, 3)  → Need to evict one key
#     We need to evict the LEAST recently used key
#     last_used_key = 1 tells us 1 is most recent
#     But we need to evict 2 (least recent)!
#     HOW DO WE KNOW IT'S 2? ❌ We can't tell!
#
# THE SOLUTION: We need to maintain the FULL ORDERING of all keys:
#   - Most recent: 1
#   - Least recent: 2
#   
#   This requires tracking the order of ALL keys, not just the last one.
#   A doubly linked list (or OrderedDict) maintains this ordering efficiently.
#
# ALTERNATIVE THAT DOESN'T WORK:
#   What if we track "least_recently_used_key" instead?
#   Still fails! When we update a key, we need to know what the NEW
#   least recently used key is. We'd need to track the full order anyway.
#
# PROOF BY CODE (Why last_used_key fails):
#   class BrokenLRU:
#       def __init__(self, capacity):
#           self.cache = {}
#           self.capacity = capacity
#           self.last_used_key = None  # ❌ Only tracks most recent
#       
#       def put(self, key, value):
#           if len(self.cache) >= self.capacity and key not in self.cache:
#               # ❌ PROBLEM: Which key to evict? We don't know!
#               # We only know last_used_key (most recent), not least recent
#               # We can't determine which key to remove!
#               pass
#       
#   The broken implementation can't determine which key to evict because
#   it doesn't maintain the ordering information needed.

class Node:
    """Doubly linked list node"""
    def __init__(self, key: int = 0, value: int = 0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    LRU Cache implementation using hash map + doubly linked list.
    
    Time Complexity: O(1) for both get() and put()
    Space Complexity: O(capacity)
    
    Structure:
    - HashMap: key -> Node mapping for O(1) lookup
    - Doubly Linked List: maintains order (head = most recent, tail = least recent)
    - Dummy head and tail nodes simplify edge cases
    """
    
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # key -> Node mapping
        
        # Create dummy head and tail nodes
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _add_node(self, node: Node):
        """Add node right after head (most recent position)"""
        node.prev = self.head
        node.next = self.head.next
        
        self.head.next.prev = node
        self.head.next = node
    
    def _remove_node(self, node: Node):
        """Remove node from the linked list"""
        prev_node = node.prev
        next_node = node.next
        
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _move_to_head(self, node: Node):
        """Move node to head (mark as most recently used)"""
        self._remove_node(node)
        self._add_node(node)
    
    def _pop_tail(self) -> Node:
        """Remove and return the least recently used node (before tail)"""
        last_node = self.tail.prev
        self._remove_node(last_node)
        return last_node
    
    def get(self, key: int) -> int:
        """
        Get value by key and mark as most recently used.
        Returns -1 if key doesn't exist.
        """
        node = self.cache.get(key)
        
        if not node:
            return -1
        
        # Move to head (mark as most recently used)
        self._move_to_head(node)
        return node.value
    
    def put(self, key: int, value: int) -> None:
        """
        Insert or update key-value pair.
        If key exists, update value and mark as most recently used.
        If key doesn't exist:
            - If at capacity, evict least recently used
            - Add new node and mark as most recently used
        """
        node = self.cache.get(key)
        
        if not node:
            # New key
            new_node = Node(key, value)
            
            if len(self.cache) >= self.capacity:
                # Evict least recently used
                tail = self._pop_tail()
                del self.cache[tail.key]
            
            self.cache[key] = new_node
            self._add_node(new_node)
        else:
            # Existing key - update value and move to head
            node.value = value
            self._move_to_head(node)


# Test cases
if __name__ == "__main__":
    # Example 1 - Test OrderedDict version
    print("Testing OrderedDict implementation:")
    lru1 = LRUCacheOrderedDict(2)
    lru1.put(1, 1)
    lru1.put(2, 2)
    assert lru1.get(1) == 1
    lru1.put(3, 3)  # evicts key 2
    assert lru1.get(2) == -1
    lru1.put(4, 4)  # evicts key 1
    assert lru1.get(1) == -1
    assert lru1.get(3) == 3
    assert lru1.get(4) == 4
    print("✓ OrderedDict implementation passed!")
    
    # Example 1 - Test manual implementation
    print("\nTesting manual doubly linked list implementation:")
    lru2 = LRUCache(2)
    lru2.put(1, 1)
    lru2.put(2, 2)
    assert lru2.get(1) == 1
    lru2.put(3, 3)  # evicts key 2
    assert lru2.get(2) == -1
    lru2.put(4, 4)  # evicts key 1
    assert lru2.get(1) == -1
    assert lru2.get(3) == 3
    assert lru2.get(4) == 4
    print("✓ Manual implementation passed!")
    
    print("\nAll test cases passed!")