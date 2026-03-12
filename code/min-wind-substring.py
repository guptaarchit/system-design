# 76. Minimum Window Substring
# Solved
# Hard
# Topics
# Companies
# Hint
# Given two strings s and t of lengths m and n respectively, return the minimum window substring 
# of s such that every character in t (including duplicates) is included in the window. 
# If there is no such substring, return the empty string "".

# The testcases will be generated such that the answer is unique.

# Example 1:
# Input: s = "ADOBECODEBANC", t = "ABC"
# Output: "BANC"
# Explanation: The minimum window substring "BANC" includes 'A', 'B', and 'C' from string t.

# Example 2:
# Input: s = "a", t = "a"
# Output: "a"
# Explanation: The entire string s is the minimum window.

# Example 3:
# Input: s = "a", t = "aa"
# Output: ""
# Explanation: Both 'a's from t must be included in the window.
# Since the largest window of s only has one 'a', return empty string.

# Constraints:
# m == s.length
# n == t.length
# 1 <= m, n <= 105
# s and t consist of uppercase and lowercase English letters.

# Follow up: Could you find an algorithm that runs in O(m + n) time?


# Code
class Solution:
    def minWindow(self, s: str, t: str) -> str:
        """
        Find the minimum window substring of s that contains all characters of t.
        
        Time Complexity: O(m + n) where m = len(s), n = len(t)
        Space Complexity: O(m + n) for the hash maps
        """
        if not s or not t or len(s) < len(t):
            return ""
        
        # Count characters needed from t
        need = {}
        for char in t:
            need[char] = need.get(char, 0) + 1
        
        # Track characters in current window
        window = {}
        
        # Track how many unique characters we have satisfied
        # (i.e., have the required count)
        have = 0
        need_count = len(need)
        
        # Result tracking
        min_len = float('inf')
        result_start = 0
        
        # Two pointers for sliding window
        left = 0
        
        # Expand window by moving right pointer
        for right in range(len(s)):
            char = s[right]
            
            # Add character to window
            window[char] = window.get(char, 0) + 1
            
            # Check if we've satisfied the requirement for this character
            if char in need and window[char] == need[char]:
                have += 1
            
            # Try to shrink window from left while maintaining validity
            while have == need_count:
                # Update minimum window if current is smaller
                current_len = right - left + 1
                if current_len < min_len:
                    min_len = current_len
                    result_start = left
                
                # Remove leftmost character
                left_char = s[left]
                window[left_char] -= 1
                
                # Check if we broke the requirement for this character
                if left_char in need and window[left_char] < need[left_char]:
                    have -= 1
                
                left += 1
        
        # Return result
        if min_len == float('inf'):
            return ""
        return s[result_start:result_start + min_len]


# Note
# Algorithm: Sliding Window (Two Pointers)
# 1. Use two pointers (left, right) to maintain a window
# 2. Expand window by moving right pointer until all characters from t are included
# 3. Once all characters are included, try to shrink from left to find minimum window
# 4. Keep track of minimum valid window found
# 
# Key insight: Use a counter to track how many unique characters have been satisfied
# (i.e., have reached their required count). This avoids checking all characters repeatedly.


# Testcase
def test_minWindow():
    solution = Solution()
    
    # Test case 1
    assert solution.minWindow("ADOBECODEBANC", "ABC") == "BANC"
    
    # Test case 2
    assert solution.minWindow("a", "a") == "a"
    
    # Test case 3
    assert solution.minWindow("a", "aa") == ""
    
    # Test case 4: Multiple occurrences
    assert solution.minWindow("aab", "aab") == "aab"
    
    # Test case 5: No valid window
    assert solution.minWindow("a", "b") == ""
    
    # Test case 6: Window at the end
    assert solution.minWindow("abc", "bc") == "bc"
    
    # Test case 7: Window at the beginning
    assert solution.minWindow("abc", "ab") == "ab"
    
    print("All test cases passed!")


# Test Result
if __name__ == "__main__":
    test_minWindow()