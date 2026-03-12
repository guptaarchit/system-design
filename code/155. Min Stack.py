# 155. Min Stack
# Medium
# Topics
# conpanies icon
# Companies
# Hint
# Design a stack that supports push, pop, top, and retrieving the minimum element in constant time.

# Implement the MinStack class:

# MinStack() initializes the stack object.
# void push(int val) pushes the element val onto the stack.
# void pop() removes the element on the top of the stack.
# int top() gets the top element of the stack.
# int getMin() retrieves the minimum element in the stack.
# You must implement a solution with O(1) time complexity for each function.

 

# Example 1:

# Input
# ["MinStack","push","push","push","getMin","pop","top","getMin"]
# [[],[-2],[0],[-3],[],[],[],[]]

# Output
# [null,null,null,null,-3,null,0,-2]

# Explanation
# MinStack minStack = new MinStack();
# minStack.push(-2);
# minStack.push(0);
# minStack.push(-3);
# minStack.getMin(); // return -3
# minStack.pop();
# minStack.top();    // return 0
# minStack.getMin(); // return -2


class MinStack:
    """
    Min Stack implementation with O(1) operations.
    
    Approach: Store pairs of (value, min_so_far) in the stack.
    This way, each element knows the minimum value when it was pushed,
    allowing O(1) getMin() after pop operations.
    
    Time Complexity: O(1) for all operations
    Space Complexity: O(n) where n is number of elements
    """
    
    def __init__(self):
        """
        Initialize the stack.
        Stack stores tuples: (value, minimum_value_seen_so_far)
        """
        self.stack = []
    
    def push(self, val: int) -> None:
        """
        Push element onto stack.
        Store the minimum value seen so far with each element.
        """
        if not self.stack:
            # First element - it's the minimum
            self.stack.append((val, val))
        else:
            # Compare with current minimum
            current_min = self.stack[-1][1]
            self.stack.append((val, min(val, current_min)))
    
    def pop(self) -> None:
        """
        Remove the top element from the stack.
        """
        if self.stack:
            self.stack.pop()
    
    def top(self) -> int:
        """
        Get the top element of the stack.
        """
        return self.stack[-1][0]
    
    def getMin(self) -> int:
        """
        Retrieve the minimum element in the stack in O(1) time.
        """
        return self.stack[-1][1]


# Alternative approach: Using two stacks
class MinStackTwoStacks:
    """
    Alternative implementation using two stacks:
    - One stack for values
    - One stack for minimums (only push when new min is found)
    
    This can be more space-efficient if many duplicate values exist.
    """
    
    def __init__(self):
        self.stack = []
        self.min_stack = []
    
    def push(self, val: int) -> None:
        self.stack.append(val)
        # Only push to min_stack if it's empty or val <= current min
        if not self.min_stack or val <= self.min_stack[-1]:
            self.min_stack.append(val)
    
    def pop(self) -> None:
        if self.stack:
            popped = self.stack.pop()
            # If we're popping the current minimum, remove from min_stack
            if self.min_stack and popped == self.min_stack[-1]:
                self.min_stack.pop()
    
    def top(self) -> int:
        return self.stack[-1]
    
    def getMin(self) -> int:
        return self.min_stack[-1]


# Test cases
if __name__ == "__main__":
    # Example 1
    minStack = MinStack()
    minStack.push(-2)
    minStack.push(0)
    minStack.push(-3)
    assert minStack.getMin() == -3
    minStack.pop()
    assert minStack.top() == 0
    assert minStack.getMin() == -2
    print("Example 1 passed")
    
    # Test with two stacks approach
    minStack2 = MinStackTwoStacks()
    minStack2.push(-2)
    minStack2.push(0)
    minStack2.push(-3)
    assert minStack2.getMin() == -3
    minStack2.pop()
    assert minStack2.top() == 0
    assert minStack2.getMin() == -2
    print("Two stacks approach passed")
    
    # Additional test cases
    minStack3 = MinStack()
    minStack3.push(5)
    minStack3.push(3)
    minStack3.push(4)
    assert minStack3.getMin() == 3
    minStack3.pop()
    assert minStack3.getMin() == 3
    minStack3.pop()
    assert minStack3.getMin() == 5
    print("Additional tests passed")
    
    print("\nAll test cases passed!")
