# 207. Course Schedule
# Medium
# Topics
# conpanies icon
# Companies
# Hint
# There are a total of numCourses courses you have to take, labeled from 0 to numCourses - 1. You are given an array prerequisites where prerequisites[i] = [ai, bi] indicates that you must take course bi first if you want to take course ai.

# For example, the pair [0, 1], indicates that to take course 0 you have to first take course 1.
# Return true if you can finish all courses. Otherwise, return false.

 

# Example 1:

# Input: numCourses = 2, prerequisites = [[1,0]]
# Output: true
# Explanation: There are a total of 2 courses to take. 
# To take course 1 you should have finished course 0. So it is possible.
# Example 2:

# Input: numCourses = 2, prerequisites = [[1,0],[0,1]]
# Output: false
# Explanation: There are a total of 2 courses to take. 
# To take course 1 you should have finished course 0, and to take course 0 you should also have finished course 1. So it is impossible.
 

# Constraints:

# 1 <= numCourses <= 2000
# 0 <= prerequisites.length <= 5000
# prerequisites[i].length == 2
# 0 <= ai, bi < numCourses
# All the pairs prerequisites[i] are unique.

from typing import List

class Solution:
    def canFinish(self, numCourses: int, prerequisites: List[List[int]]) -> bool:
        """
        Build graph: bi -> ai (take bi before ai). Detect cycle via DFS.
        State: 0=unvisited, 1=visiting, 2=done. Cycle if we hit 1.
        O(V+E) time, O(V) space.
        """
        adj = [[] for _ in range(numCourses)]
        for a, b in prerequisites:
            adj[b].append(a)

        state = [0] * numCourses

        def has_cycle(v: int) -> bool:
            if state[v] == 1:
                return True
            if state[v] == 2:
                return False
            state[v] = 1
            for u in adj[v]:
                if has_cycle(u):
                    return True
            state[v] = 2
            return False

        for v in range(numCourses):
            if has_cycle(v):
                return False
        return True