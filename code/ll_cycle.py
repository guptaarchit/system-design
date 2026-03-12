# Given the head of a linked list, return the node where the cycle begins. If there is no cycle, return null.

# There is a cycle in a linked list if there is some node in the list that can be reached again by continuously following the next pointer. Internally, pos is used to denote the index of the node that tail's next pointer is connected to (0-indexed). It is -1 if there is no cycle. Note that pos is not passed as a parameter.

# Do not modify the linked list.

 

# Example 1:


# Input: head = [3,2,0,-4], pos = 1
# Output: tail connects to node index 1
# Explanation: There is a cycle in the linked list, where tail connects to the second node.
# Example 2:


# Input: head = [1,2], pos = 0
# Output: tail connects to node index 0
# Explanation: There is a cycle in the linked list, where tail connects to the first node.
# Example 3:


# Input: head = [1], pos = -1
# Output: no cycle
# Explanation: There is no cycle in the linked list.
 

# Constraints:

# The number of the nodes in the list is in the range [0, 104].
# -105 <= Node.val <= 105
# pos is -1 or a valid index in the linked-list.
 

# Follow up: Can you solve it using O(1) (i.e. constant) memory?

# Definition for singly-linked list.
class ListNode:
    def __init__(self, x):
        self.val = x
        self.next = None


class Solution:
    def detectCycle(self, head: ListNode) -> ListNode | None:
        """
        Find the node where the cycle begins using Floyd's Cycle Detection Algorithm.
        
        Algorithm (Floyd's Tortoise and Hare):
        1. Use slow (1 step) and fast (2 steps) pointers
        2. If there's a cycle, they will meet
        3. Reset slow to head, keep fast at meeting point
        4. Move both one step at a time - where they meet is cycle start
        
        Mathematical Proof:
        Let:
        - L = distance from head to cycle start
        - C = cycle length
        - x = distance from cycle start to meeting point
        
        When slow and fast meet:
        - Slow has traveled: L + x
        - Fast has traveled: L + x + n*C (n complete cycles)
        - Since fast is 2x speed: 2(L + x) = L + x + n*C
        - Simplifying: L + x = n*C → L = n*C - x
        
        This means: distance from head to cycle start = distance from meeting point
        to cycle start (going backwards in cycle)
        
        Time: O(n)
        Space: O(1)
        """
        if not head or not head.next:
            return None
        
        # Step 1: Detect if cycle exists using Floyd's algorithm
        slow = fast = head
        
        # Move slow 1 step, fast 2 steps
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
            
            # If they meet, cycle exists
            if slow == fast:
                break
        else:
            # No cycle found
            return None
        
        # Step 2: Find the cycle start
        # Reset slow to head, keep fast at meeting point
        # Move both one step at a time
        slow = head
        while slow != fast:
            slow = slow.next
            fast = fast.next
        
        # They meet at cycle start
        return slow


# Helper function to create linked list with cycle
def create_linked_list_with_cycle(arr, pos):
    """
    Create a linked list from array with cycle at position 'pos'.
    pos = -1 means no cycle.
    """
    if not arr:
        return None
    
    nodes = [ListNode(val) for val in arr]
    
    # Connect nodes
    for i in range(len(nodes) - 1):
        nodes[i].next = nodes[i + 1]
    
    # Create cycle if pos >= 0
    if pos >= 0:
        nodes[-1].next = nodes[pos]
    
    return nodes[0]


# Helper function to get node at index (for testing)
def get_node_at_index(head, index):
    """Get node at given index (0-indexed)"""
    current = head
    for _ in range(index):
        if current:
            current = current.next
        else:
            return None
    return current


# Test cases
if __name__ == "__main__":
    solution = Solution()
    
    # Example 1: [3,2,0,-4], pos = 1
    head1 = create_linked_list_with_cycle([3, 2, 0, -4], 1)
    cycle_start1 = solution.detectCycle(head1)
    expected1 = get_node_at_index(head1, 1)
    assert cycle_start1 == expected1
    assert cycle_start1.val == 2
    print("Example 1 passed: Cycle starts at node with value 2")
    
    # Example 2: [1,2], pos = 0
    head2 = create_linked_list_with_cycle([1, 2], 0)
    cycle_start2 = solution.detectCycle(head2)
    expected2 = get_node_at_index(head2, 0)
    assert cycle_start2 == expected2
    assert cycle_start2.val == 1
    print("Example 2 passed: Cycle starts at node with value 1")
    
    # Example 3: [1], pos = -1 (no cycle)
    head3 = create_linked_list_with_cycle([1], -1)
    cycle_start3 = solution.detectCycle(head3)
    assert cycle_start3 is None
    print("Example 3 passed: No cycle detected")
    
    # Additional test: Longer list with cycle
    head4 = create_linked_list_with_cycle([1, 2, 3, 4, 5, 6], 2)
    cycle_start4 = solution.detectCycle(head4)
    expected4 = get_node_at_index(head4, 2)
    assert cycle_start4 == expected4
    assert cycle_start4.val == 3
    print("Additional test passed: Cycle starts at node with value 3")
    
    print("\nAll test cases passed!")