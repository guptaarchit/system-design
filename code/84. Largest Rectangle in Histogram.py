# 84. Largest Rectangle in Histogram
# Hard
# Topics
# conpanies icon
# Companies
# Given an array of integers heights representing the histogram's bar height where the width of each bar is 1, return the area of the largest rectangle in the histogram.

 

# Example 1:


# Input: heights = [2,1,5,6,2,3]
# Output: 10
# Explanation: The above is a histogram where width of each bar is 1.
# The largest rectangle is shown in the red area, which has an area = 10 units.
# Example 2:


# Input: heights = [2,4]
# Output: 4
 

# Constraints:

# 1 <= heights.length <= 105
# 0 <= heights[i] <= 104

class Solution:
    def largestRectangleArea(self, heights: list[int]) -> int:
        """
        Find the largest rectangle area in histogram using monotonic stack.
        
        Key Insight:
        For each bar, find the largest rectangle where that bar is the minimum height.
        We need to find left and right boundaries where the bar height is minimum.
        
        Algorithm:
        1. Use stack to store indices of bars in increasing order of height
        2. When we encounter a bar shorter than stack top:
           - Pop from stack (this bar's right boundary is current position)
           - Calculate area: height[popped] * (current_index - stack_top_index - 1)
           - Update max_area
        3. After processing all bars, process remaining stack elements
        
        Time: O(n) - each bar pushed/popped once
        Space: O(n) - stack
        
        Example: heights = [2,1,5,6,2,3]
        i=0 (2): stack=[], push 0 → stack=[0]
        i=1 (1): 1 < 2 → pop 0, stack empty → width=i=1, area=2*1=2 → push 1 → stack=[1]
        i=2 (5): 5 > 1 → push 2 → stack=[1,2]
        i=3 (6): 6 > 5 → push 3 → stack=[1,2,3]
        i=4 (2): 2 < 6 → pop 3, area = 6*(4-2-1) = 6*1 = 6
                  2 < 5 → pop 2, area = 5*(4-1-1) = 5*2 = 10 (max)
                  2 > 1 → push 4 → stack=[1,4]
        i=5 (3): 3 > 2 → push 5 → stack=[1,4,5]
        After loop: process remaining
          pop 5: area = 3*(6-4-1) = 3*1 = 3
          pop 4: area = 2*(6-1-1) = 2*4 = 8
          pop 1: area = 1*(6-(-1)-1) = 1*6 = 6
        Max area = 10
        """
        stack = []
        max_area = 0
        n = len(heights)
        
        for i in range(n):
            # While current bar is shorter than bar at stack top
            # This means we found the right boundary for bars in stack
            while stack and heights[i] < heights[stack[-1]]:
                # Pop the bar index
                height = heights[stack.pop()]
                
                # Calculate width
                # Stack empty → width = i (extends from index 0 to i-1). Left boundary = -1.
                # Stack not empty → width = i - stack[-1] - 1 (extends from stack[-1]+1 to i-1).
                width = i if not stack else i - stack[-1] - 1
                
                # Calculate area and update max
                area = height * width
                max_area = max(max_area, area)
            
            # Push current index to stack
            stack.append(i)
        
        # Process remaining bars in stack
        # WHY IS THIS NECESSARY?
        # ======================
        # After the main loop, bars remaining in the stack never found a shorter bar
        # to their right. This means they extend all the way to the END of the histogram.
        # We must calculate their areas, otherwise we'll miss potential maximum rectangles.
        #
        # Example: heights = [2, 1, 5, 6, 2, 3]
        # After main loop: stack = [1, 4, 5]
        #   - Bar at index 1 (height=1): extends from index 1 to end (width=5)
        #   - Bar at index 4 (height=2): extends from index 4 to end (width=2)
        #   - Bar at index 5 (height=3): extends from index 5 to end (width=1)
        #
        # Without this step, we'd miss these rectangles!
        #
        # Width calculation:
        # - If stack becomes empty: width extends from start (0) to end (n)
        # - Otherwise: width extends from previous bar to end (n - stack[-1] - 1)
        
        while stack:
            height = heights[stack.pop()]
            # Calculate width: from left boundary to end of histogram
            width = n if not stack else n - stack[-1] - 1
            area = height * width
            max_area = max(max_area, area)
        
        return max_area


# Alternative approach: Using sentinel values for cleaner code
class SolutionSentinel:
    def largestRectangleArea(self, heights: list[int]) -> int:
        """
        Same algorithm but using sentinel values (0 at start and end)
        to simplify boundary handling.
        """
        # Add sentinel 0 at the end to ensure all bars are processed
        heights = heights + [0]
        stack = [-1]  # Sentinel at start
        max_area = 0
        
        for i in range(len(heights)):
            # While current bar is shorter than bar at stack top
            while stack[-1] != -1 and heights[i] < heights[stack[-1]]:
                height = heights[stack.pop()]
                width = i - stack[-1] - 1
                max_area = max(max_area, height * width)
            stack.append(i)
        
        return max_area


# Test cases
if __name__ == "__main__":
    solution = Solution()
    solution2 = SolutionSentinel()
    
    # Example 1: [2,1,5,6,2,3] -> 10
    result1 = solution.largestRectangleArea([2, 1, 5, 6, 2, 3])
    assert result1 == 10
    assert solution2.largestRectangleArea([2, 1, 5, 6, 2, 3]) == 10
    print("Example 1 passed: [2,1,5,6,2,3] -> 10")
    
    # Example 2: [2,4] -> 4
    result2 = solution.largestRectangleArea([2, 4])
    assert result2 == 4
    assert solution2.largestRectangleArea([2, 4]) == 4
    print("Example 2 passed: [2,4] -> 4")
    
    # Additional test cases
    result3 = solution.largestRectangleArea([1])
    assert result3 == 1
    assert solution2.largestRectangleArea([1]) == 1
    print("Edge case passed: [1] -> 1")
    
    result4 = solution.largestRectangleArea([1, 1])
    assert result4 == 2
    assert solution2.largestRectangleArea([1, 1]) == 2
    print("Edge case passed: [1,1] -> 2")
    
    result5 = solution.largestRectangleArea([5, 4, 3, 2, 1])
    assert result5 == 9  # 3 bars of height 3 = 9
    assert solution2.largestRectangleArea([5, 4, 3, 2, 1]) == 9
    print("Edge case passed: Decreasing heights")
    
    result6 = solution.largestRectangleArea([1, 2, 3, 4, 5])
    assert result6 == 9  # 3 bars of height 3 = 9
    assert solution2.largestRectangleArea([1, 2, 3, 4, 5]) == 9
    print("Edge case passed: Increasing heights")
    
    print("\nAll test cases passed!")