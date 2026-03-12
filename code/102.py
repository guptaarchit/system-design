# 102. Binary Tree Level Order Traversal
# Medium
# Topics
# conpanies icon
# Companies
# Hint
# Given the root of a binary tree, return the level order traversal of its nodes' values. (i.e., from left to right, level by level).

 

# Example 1:


# Input: root = [3,9,20,null,null,15,7]
# Output: [[3],[9,20],[15,7]]
# Example 2:

# Input: root = [1]
# Output: [[1]]
# Example 3:

# Input: root = []
# Output: []
 

# Constraints:

# The number of nodes in the tree is in the range [0, 2000].
# -1000 <= Node.val <= 1000

from typing import Optional, List

# Definition for a binary tree node.
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def levelOrder(self, root: Optional[TreeNode]) -> List[List[int]]:
        """
        Return the level order traversal of the binary tree.
        Uses DFS (Depth-First Search) with recursion to traverse level by level.
        
        Time Complexity: O(n) where n is the number of nodes
        Space Complexity: O(h) where h is the height of the tree (recursion stack)
        """
        if not root:
            return []
        
        result = []
        
        def dfs(node: Optional[TreeNode], level: int):
            """
            Recursive helper function to traverse the tree.
            Adds nodes to the appropriate level in the result list.
            """
            if not node:
                return
            
            # If we need a new level, create it
            if level == len(result):
                result.append([])
            
            # Add current node's value to its level
            result[level].append(node.val)
            
            # Recursively process left and right children
            dfs(node.left, level + 1)
            dfs(node.right, level + 1)
        
        dfs(root, 0)
        return result
