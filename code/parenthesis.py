
# 32. Longest Valid Parentheses
# Hard
# Topics
# conpanies icon
# Companies
# Given a string containing just the characters '(' and ')', return the length of the longest valid (well-formed) parentheses substring.

 

# Example 1:

# Input: s = "(()"
# Output: 2
# Explanation: The longest valid parentheses substring is "()".
# Example 2:

# Input: s = ")()())"
# Output: 4
# Explanation: The longest valid parentheses substring is "()()".
# Example 3:

# Input: s = ""
# Output: 0
 

# Constraints:

# 0 <= s.length <= 3 * 104
# s[i] is '(', or ')'.

class Solution:
    def longestValidParentheses(self, s: str) -> int:
        """
        Find the length of the longest valid parentheses substring.
        
        Approach 1: Using Stack
        - Use stack to store indices of unmatched opening parentheses
        - Push -1 initially to mark the start boundary
        - When we see '(', push its index
        - When we see ')', pop from stack:
          * If stack becomes empty, push current index (new boundary)
          * Otherwise, calculate length from top of stack to current index
        
        Time: O(n) - single pass
        Space: O(n) - stack can store up to n indices
        
        Example: s = ")()())"
        i=0, ')': stack=[-1], pop -> stack=[], push 0 -> stack=[0]
        i=1, '(': stack=[0], push 1 -> stack=[0,1]
        i=2, ')': stack=[0,1], pop -> stack=[0], length = 2-0 = 2
        i=3, '(': stack=[0], push 3 -> stack=[0,3]
        i=4, ')': stack=[0,3], pop -> stack=[0], length = 4-0 = 4
        i=5, ')': stack=[0], pop -> stack=[], push 5 -> stack=[5]
        Max length = 4
        """
        if not s:
            return 0
        
        stack = [-1]  # Start with -1 to handle edge cases
        max_length = 0
        
        for i, char in enumerate(s):
            if char == '(':
                # Push index of opening parenthesis
                stack.append(i)
            else:
                # Closing parenthesis
                stack.pop()
                
                if not stack:
                    # Stack is empty, push current index as new boundary
                    stack.append(i)
                else:
                    # Calculate length of valid parentheses substring
                    # from top of stack (last unmatched '(') to current position
                    max_length = max(max_length, i - stack[-1])
        
        return max_length


# Alternative approach using Dynamic Programming
class SolutionDP:
    def longestValidParentheses(self, s: str) -> int:
        """
        DP Approach:
        dp[i] = length of longest valid parentheses ending at index i
        
        If s[i] == '(', dp[i] = 0 (can't end valid substring with '(')
        If s[i] == ')':
            - If s[i-1] == '(', dp[i] = dp[i-2] + 2
            - If s[i-1] == ')' and s[i-dp[i-1]-1] == '(', 
              dp[i] = dp[i-1] + 2 + dp[i-dp[i-1]-2]
        
        Time: O(n)
        Space: O(n)
        """
        if not s:
            return 0
        
        n = len(s)
        dp = [0] * n
        max_length = 0
        
        for i in range(1, n):
            if s[i] == ')':
                if s[i - 1] == '(':
                    # Case: ...()
                    dp[i] = (dp[i - 2] if i >= 2 else 0) + 2
                elif i - dp[i - 1] > 0 and s[i - dp[i - 1] - 1] == '(':
                    # Case: ...((...))
                    dp[i] = dp[i - 1] + (dp[i - dp[i - 1] - 2] if i - dp[i - 1] >= 2 else 0) + 2
                
                max_length = max(max_length, dp[i])
        
        return max_length


# Test cases
if __name__ == "__main__":
    solution = Solution()
    solution_dp = SolutionDP()
    
    # Example 1: "(()"
    result1 = solution.longestValidParentheses("(()")
    assert result1 == 2
    assert solution_dp.longestValidParentheses("(()") == 2
    print("Example 1 passed: '(()' -> 2")
    
    # Example 2: ")()())"
    result2 = solution.longestValidParentheses(")()())")
    assert result2 == 4
    assert solution_dp.longestValidParentheses(")()())") == 4
    print("Example 2 passed: ')()())' -> 4")
    
    # Example 3: ""
    result3 = solution.longestValidParentheses("")
    assert result3 == 0
    assert solution_dp.longestValidParentheses("") == 0
    print("Example 3 passed: '' -> 0")
    
    # Additional test cases
    result4 = solution.longestValidParentheses("()(()")
    assert result4 == 2
    assert solution_dp.longestValidParentheses("()(()") == 2
    print("Additional test passed: '()(()' -> 2")
    
    result5 = solution.longestValidParentheses("((()))")
    assert result5 == 6
    assert solution_dp.longestValidParentheses("((()))") == 6
    print("Additional test passed: '((()))' -> 6")
    
    result6 = solution.longestValidParentheses("()(())")
    assert result6 == 6
    assert solution_dp.longestValidParentheses("()(())") == 6
    print("Additional test passed: '()(())' -> 6")
    
    print("\nAll test cases passed!")