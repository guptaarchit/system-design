# 92. Reverse Linked List II
# Medium
# Topics
# conpanies icon
# Companies
# Given the head of a singly linked list and two integers left and right where left <= right, reverse the nodes of the list from position left to position right, and return the reversed list.

 

# Example 1:


# Input: head = [1,2,3,4,5], left = 2, right = 4
# Output: [1,4,3,2,5]
# Example 2:

# Input: head = [5], left = 1, right = 1
# Output: [5]
 

# Constraints:

# The number of nodes in the list is n.
# 1 <= n <= 500
# -500 <= Node.val <= 500
# 1 <= left <= right <= n

# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class Solution:
    def reverseBetween(self, head: ListNode, left: int, right: int) -> ListNode:
        """
        Reverse nodes from position left to right (1-indexed).
        
        Approach:
        1. Use dummy node to handle edge case where left = 1
        2. Find the node before the reversal starts (prev)
        3. Reverse nodes from left to right
        4. Connect the reversed portion back to the list
        
        Time: O(n) - single pass
        Space: O(1) - only using pointers
        """
        # Dummy node to handle edge case where left = 1
        dummy = ListNode(0)
        dummy.next = head
        
        # Find the node before position 'left'
        prev = dummy
        for _ in range(left - 1):
            prev = prev.next
        
        # Start reversing from 'left' position
        # prev.next is the first node to reverse
        current = prev.next
        
        # Reverse nodes from left to right
        # We'll move current.next to the front of the reversed portion
        # 
        # EXAMPLE 1: [1,2,3,4,5], left=2, right=4
        # Goal: Reverse positions 2-4 → [1,4,3,2,5]
        #
        # Initial state:
        #   dummy -> 1 -> 2 -> 3 -> 4 -> 5
        #            prev cur  next
        #
        # After finding prev (position 1):
        #   dummy -> 1 -> 2 -> 3 -> 4 -> 5
        #            prev cur
        #
        # Iteration 1 (right-left = 2 iterations):
        #   next_node = current.next = 3
        #   current.next = next_node.next = 4
        #   next_node.next = prev.next = 2
        #   prev.next = next_node = 3
        #   Result: dummy -> 1 -> 3 -> 2 -> 4 -> 5
        #                  prev      cur  next
        #
        # Iteration 2:
        #   next_node = current.next = 4
        #   current.next = next_node.next = 5
        #   next_node.next = prev.next = 3
        #   prev.next = next_node = 4
        #   Result: dummy -> 1 -> 4 -> 3 -> 2 -> 5
        #                  prev           cur
        #
        # Final: Return dummy.next = [1,4,3,2,5] ✓
        #
        # ====================================================================
        # EXAMPLE 2: BIGGER LIST [1,2,3,4,5,6,7,8], left=3, right=7
        # Goal: Reverse positions 3-7 → [1,2,7,6,5,4,3,8]
        #
        # Initial state:
        #   dummy -> 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8
        #                  prev cur  next
        #
        # After finding prev (position 2):
        #   dummy -> 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8
        #                  prev cur
        #
        # Iteration 1: Move node 4 to front
        #   next_node = 4
        #   current.next = 5 (skip 4)
        #   next_node.next = 3 (4 points to prev.next)
        #   prev.next = 4
        #   Result: dummy -> 1 -> 2 -> 4 -> 3 -> 5 -> 6 -> 7 -> 8
        #                  prev      cur
        #
        # Iteration 2: Move node 5 to front
        #   next_node = 5
        #   current.next = 6 (skip 5)
        #   next_node.next = 4 (5 points to prev.next)
        #   prev.next = 5
        #   Result: dummy -> 1 -> 2 -> 5 -> 4 -> 3 -> 6 -> 7 -> 8
        #                  prev      cur
        #
        # Iteration 3: Move node 6 to front
        #   next_node = 6
        #   current.next = 7 (skip 6)
        #   next_node.next = 5 (6 points to prev.next)
        #   prev.next = 6
        #   Result: dummy -> 1 -> 2 -> 6 -> 5 -> 4 -> 3 -> 7 -> 8
        #                  prev      cur
        #
        # Iteration 4: Move node 7 to front
        #   next_node = 7
        #   current.next = 8 (skip 7)
        #   next_node.next = 6 (7 points to prev.next)
        #   prev.next = 7
        #   Result: dummy -> 1 -> 2 -> 7 -> 6 -> 5 -> 4 -> 3 -> 8
        #                  prev      cur
        #
        # Final: Return dummy.next = [1,2,7,6,5,4,3,8] ✓
        #
        # Pattern: Each iteration moves current.next to the front of the
        # reversed portion, building it incrementally from right to left.
        
        for _ in range(right - left):
            # The node to move forward
            next_node = current.next
            
            # Skip next_node in its current position
            current.next = next_node.next
            
            # Insert next_node at the front of reversed portion
            next_node.next = prev.next
            prev.next = next_node
        
        return dummy.next


# Helper function to create linked list from list
def create_linked_list(arr):
    if not arr:
        return None
    head = ListNode(arr[0])
    current = head
    for val in arr[1:]:
        current.next = ListNode(val)
        current = current.next
    return head


# Helper function to convert linked list to list
def linked_list_to_list(head):
    result = []
    current = head
    while current:
        result.append(current.val)
        current = current.next
    return result


# Test cases
if __name__ == "__main__":
    solution = Solution()
    
    # Example 1: [1,2,3,4,5], left = 2, right = 4
    head1 = create_linked_list([1, 2, 3, 4, 5])
    result1 = solution.reverseBetween(head1, 2, 4)
    assert linked_list_to_list(result1) == [1, 4, 3, 2, 5]
    print("Example 1 passed: [1,2,3,4,5] -> [1,4,3,2,5]")
    
    # Example 2: [5], left = 1, right = 1
    head2 = create_linked_list([5])
    result2 = solution.reverseBetween(head2, 1, 1)
    assert linked_list_to_list(result2) == [5]
    print("Example 2 passed: [5] -> [5]")
    
    # Additional test: reverse entire list
    head3 = create_linked_list([1, 2, 3, 4, 5])
    result3 = solution.reverseBetween(head3, 1, 5)
    assert linked_list_to_list(result3) == [5, 4, 3, 2, 1]
    print("Additional test passed: reverse entire list")
    
    # Additional test: reverse from start
    head4 = create_linked_list([1, 2, 3, 4, 5])
    result4 = solution.reverseBetween(head4, 1, 3)
    assert linked_list_to_list(result4) == [3, 2, 1, 4, 5]
    print("Additional test passed: reverse from start")
    
    # Bigger example: [1,2,3,4,5,6,7,8], left = 3, right = 7
    head5 = create_linked_list([1, 2, 3, 4, 5, 6, 7, 8])
    result5 = solution.reverseBetween(head5, 3, 7)
    assert linked_list_to_list(result5) == [1, 2, 7, 6, 5, 4, 3, 8]
    print("Bigger example passed: [1,2,3,4,5,6,7,8] -> [1,2,7,6,5,4,3,8]")
    
    print("\nAll test cases passed!")