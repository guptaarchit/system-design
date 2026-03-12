# 160. Intersection of Two Linked Lists
# Solved
# Easy
# Topics
# conpanies icon
# Companies
# Given the heads of two singly linked-lists headA and headB, return the node at which the two lists intersect. If the two linked lists have no intersection at all, return null.

# For example, the following two linked lists begin to intersect at node c1:


# The test cases are generated such that there are no cycles anywhere in the entire linked structure.

# Note that the linked lists must retain their original structure after the function returns.

# Custom Judge:

# The inputs to the judge are given as follows (your program is not given these inputs):

# intersectVal - The value of the node where the intersection occurs. This is 0 if there is no intersected node.
# listA - The first linked list.
# listB - The second linked list.
# skipA - The number of nodes to skip ahead in listA (starting from the head) to get to the intersected node.
# skipB - The number of nodes to skip ahead in listB (starting from the head) to get to the intersected node.
# The judge will then create the linked structure based on these inputs and pass the two heads, headA and headB to your program. If you correctly return the intersected node, then your solution will be accepted.

 

# Example 1:


# Input: intersectVal = 8, listA = [4,1,8,4,5], listB = [5,6,1,8,4,5], skipA = 2, skipB = 3
# Output: Intersected at '8'
# Explanation: The intersected node's value is 8 (note that this must not be 0 if the two lists intersect).
# From the head of A, it reads as [4,1,8,4,5]. From the head of B, it reads as [5,6,1,8,4,5]. There are 2 nodes before the intersected node in A; There are 3 nodes before the intersected node in B.
# - Note that the intersected node's value is not 1 because the nodes with value 1 in A and B (2nd node in A and 3rd node in B) are different node references. In other words, they point to two different locations in memory, while the nodes with value 8 in A and B (3rd node in A and 4th node in B) point to the same location in memory.
# Example 2:


# Input: intersectVal = 2, listA = [1,9,1,2,4], listB = [3,2,4], skipA = 3, skipB = 1
# Output: Intersected at '2'
# Explanation: The intersected node's value is 2 (note that this must not be 0 if the two lists intersect).
# From the head of A, it reads as [1,9,1,2,4]. From the head of B, it reads as [3,2,4]. There are 3 nodes before the intersected node in A; There are 1 node before the intersected node in B.
# Example 3:


# Input: intersectVal = 0, listA = [2,6,4], listB = [1,5], skipA = 3, skipB = 2
# Output: No intersection
# Explanation: From the head of A, it reads as [2,6,4]. From the head of B, it reads as [1,5]. Since the two lists do not intersect, intersectVal must be 0, while skipA and skipB can be arbitrary values.
# Explanation: The two lists do not intersect, so return null.
 

# Constraints:

# The number of nodes of listA is in the m.
# The number of nodes of listB is in the n.
# 1 <= m, n <= 3 * 104
# 1 <= Node.val <= 105
# 0 <= skipA <= m
# 0 <= skipB <= n
# intersectVal is 0 if listA and listB do not intersect.
# intersectVal == listA[skipA] == listB[skipB] if listA and listB intersect.
 

# Follow up: Could you write a solution that runs in O(m + n) time and use only O(1) memory?

# Definition for singly-linked list.
class ListNode:
    def __init__(self, x):
        self.val = x
        self.next = None


class Solution:
    def getIntersectionNode(self, headA: ListNode, headB: ListNode) -> ListNode | None:
        """
        Find the intersection node of two linked lists.
        
        Algorithm (Two Pointers):
        1. Use two pointers, one for each list
        2. When a pointer reaches the end, switch it to the other list's head
        3. Both pointers will meet at the intersection (if it exists)
        
        Why this works:
        - If lists intersect: both pointers will travel the same total distance
          (lengthA + lengthB) before meeting at intersection
        - If lists don't intersect: both pointers will be None simultaneously
        
        Example:
        ListA: [4,1,8,4,5] (length 5)
        ListB: [5,6,1,8,4,5] (length 6, intersects at node 8)
        
        Pointer A path: 4->1->8->4->5->None->5->6->1->8 (meets at 8)
        Pointer B path: 5->6->1->8->4->5->None->4->1->8 (meets at 8)
        
        Both travel 5+3 = 8 nodes before meeting at intersection.
        
        Time: O(m + n) - each list traversed at most twice
        Space: O(1) - only using two pointers
        """
        if not headA or not headB:
            return None
        
        ptrA = headA
        ptrB = headB
        
        # Traverse until both pointers meet or both become None
        while ptrA != ptrB:
            # Move to next node, or switch to other list if at end
            ptrA = ptrA.next if ptrA else headB
            ptrB = ptrB.next if ptrB else headA
        
        # ptrA == ptrB (either intersection node or None)
        return ptrA


# Helper function to create linked list from array
def create_linked_list(arr):
    if not arr:
        return None
    head = ListNode(arr[0])
    current = head
    for val in arr[1:]:
        current.next = ListNode(val)
        current = current.next
    return head


# Helper function to create intersection
def create_intersection(listA_arr, listB_arr, skipA, skipB):
    """
    Create two linked lists that intersect.
    skipA: nodes to skip in listA before intersection
    skipB: nodes to skip in listB before intersection
    """
    # Create listA up to intersection point
    listA_nodes = [ListNode(val) for val in listA_arr]
    for i in range(len(listA_nodes) - 1):
        listA_nodes[i].next = listA_nodes[i + 1]
    
    # Create listB up to intersection point
    listB_nodes = [ListNode(val) for val in listB_arr[:skipB]]
    for i in range(len(listB_nodes) - 1):
        listB_nodes[i].next = listB_nodes[i + 1]
    
    # Connect listB to intersection point
    if listB_nodes and skipA < len(listA_nodes):
        listB_nodes[-1].next = listA_nodes[skipA]
    
    headA = listA_nodes[0] if listA_nodes else None
    headB = listB_nodes[0] if listB_nodes else listA_nodes[skipA] if skipA < len(listA_nodes) else None
    
    return headA, headB


# Test cases
if __name__ == "__main__":
    solution = Solution()
    
    # Example 1: intersectVal = 8, listA = [4,1,8,4,5], listB = [5,6,1,8,4,5], skipA = 2, skipB = 3
    headA1, headB1 = create_intersection([4, 1, 8, 4, 5], [5, 6, 1, 8, 4, 5], 2, 3)
    result1 = solution.getIntersectionNode(headA1, headB1)
    assert result1 is not None
    assert result1.val == 8
    print("Example 1 passed: Intersected at '8'")
    
    # Example 2: intersectVal = 2, listA = [1,9,1,2,4], listB = [3,2,4], skipA = 3, skipB = 1
    headA2, headB2 = create_intersection([1, 9, 1, 2, 4], [3, 2, 4], 3, 1)
    result2 = solution.getIntersectionNode(headA2, headB2)
    assert result2 is not None
    assert result2.val == 2
    print("Example 2 passed: Intersected at '2'")
    
    # Example 3: No intersection, listA = [2,6,4], listB = [1,5]
    headA3 = create_linked_list([2, 6, 4])
    headB3 = create_linked_list([1, 5])
    result3 = solution.getIntersectionNode(headA3, headB3)
    assert result3 is None
    print("Example 3 passed: No intersection")
    
    # Edge case: One list is empty
    headA4 = create_linked_list([1, 2, 3])
    result4 = solution.getIntersectionNode(headA4, None)
    assert result4 is None
    print("Edge case passed: One list is empty")
    
    print("\nAll test cases passed!")