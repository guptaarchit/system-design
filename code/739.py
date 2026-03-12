# 739. Daily Temperatures
# Medium
# Topics
# conpanies icon
# Companies
# Hint
# Given an array of integers temperatures represents the daily temperatures, return an array answer such that answer[i] is the number of days you have to wait after the ith day to get a warmer temperature. If there is no future day for which this is possible, keep answer[i] == 0 instead.

 

# Example 1:

# Input: temperatures = [73,74,75,71,69,72,76,73]
# Output: [1,1,4,2,1,1,0,0]
# Example 2:

# Input: temperatures = [30,40,50,60]
# Output: [1,1,1,0]
# Example 3:

# Input: temperatures = [30,60,90]
# Output: [1,1,0]
 

# Constraints:

# 1 <= temperatures.length <= 105
# 30 <= temperatures[i] <= 100

class Solution:
    def dailyTemperatures(self, temperatures: list[int]) -> list[int]:
        """
        Find the number of days to wait until a warmer temperature.
        
        Algorithm: Monotonic Stack
        1. Use stack to store indices of temperatures waiting for warmer day
        2. For each temperature:
           - While stack not empty and current > temperature at stack top:
             * Pop index from stack
             * Set result[popped_index] = current_index - popped_index
           - Push current index to stack
        
        Time: O(n) - each index pushed/popped once
        Space: O(n) - stack and result array
        
        Example: temperatures = [73,74,75,71,69,72,76,73]
        i=0 (73): stack=[], push 0 → stack=[0]
        i=1 (74): 74 > 73 → pop 0, result[0]=1 → stack=[], push 1 → stack=[1]
        i=2 (75): 75 > 74 → pop 1, result[1]=1 → stack=[], push 2 → stack=[2]
        i=3 (71): 71 < 75 → push 3 → stack=[2,3]
        i=4 (69): 69 < 71 → push 4 → stack=[2,3,4]
        i=5 (72): 72 > 69 → pop 4, result[4]=1 → stack=[2,3]
                  72 > 71 → pop 3, result[3]=2 → stack=[2]
                  72 < 75 → push 5 → stack=[2,5]
        i=6 (76): 76 > 72 → pop 5, result[5]=1 → stack=[2]
                  76 > 75 → pop 2, result[2]=4 → stack=[], push 6 → stack=[6]
        i=7 (73): 73 < 76 → push 7 → stack=[6,7]
        Result: [1,1,4,2,1,1,0,0]
        """
        n = len(temperatures)
        result = [0] * n
        stack = []  # Store indices
        
        for i in range(n):
            # While current temperature is warmer than temperature at stack top
            while stack and temperatures[i] > temperatures[stack[-1]]:
                # Pop index and calculate days to wait
                prev_index = stack.pop()
                result[prev_index] = i - prev_index
            
            # Push current index to stack
            stack.append(i)
        
        return result


# Alternative approach: Brute force (for comparison, not optimal)
class SolutionBruteForce:
    def dailyTemperatures(self, temperatures: list[int]) -> list[int]:
        """
        Brute force approach - O(n²) time complexity.
        Not optimal but easier to understand.
        """
        n = len(temperatures)
        result = [0] * n
        
        for i in range(n):
            for j in range(i + 1, n):
                if temperatures[j] > temperatures[i]:
                    result[i] = j - i
                    break
        
        return result


# Test cases
if __name__ == "__main__":
    solution = Solution()
    
    # Example 1: [73,74,75,71,69,72,76,73] -> [1,1,4,2,1,1,0,0]
    result1 = solution.dailyTemperatures([73, 74, 75, 71, 69, 72, 76, 73])
    assert result1 == [1, 1, 4, 2, 1, 1, 0, 0]
    print("Example 1 passed: [73,74,75,71,69,72,76,73] -> [1,1,4,2,1,1,0,0]")
    
    # Example 2: [30,40,50,60] -> [1,1,1,0]
    result2 = solution.dailyTemperatures([30, 40, 50, 60])
    assert result2 == [1, 1, 1, 0]
    print("Example 2 passed: [30,40,50,60] -> [1,1,1,0]")
    
    # Example 3: [30,60,90] -> [1,1,0]
    result3 = solution.dailyTemperatures([30, 60, 90])
    assert result3 == [1, 1, 0]
    print("Example 3 passed: [30,60,90] -> [1,1,0]")
    
    # Additional test cases
    result4 = solution.dailyTemperatures([30])
    assert result4 == [0]
    print("Edge case passed: [30] -> [0]")
    
    result5 = solution.dailyTemperatures([30, 30, 30])
    assert result5 == [0, 0, 0]
    print("Edge case passed: [30,30,30] -> [0,0,0]")
    
    result6 = solution.dailyTemperatures([90, 80, 70, 60])
    assert result6 == [0, 0, 0, 0]
    print("Edge case passed: Decreasing temperatures -> [0,0,0,0]")
    
    print("\nAll test cases passed!")