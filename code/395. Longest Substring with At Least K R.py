# 395. Longest Substring with At Least K Repeating Characters
# Medium
# Topics
# Companies
# Given a string s and an integer k, return the length of the longest substring of s 
# such that the frequency of each character in this substring is greater than or equal to k.
# If no such substring exists, return 0.

# Example 1:
# Input: s = "aaabb", k = 3
# Output: 3
# Explanation: The longest substring is "aaa", as 'a' is repeated 3 times.

# Example 2:
# Input: s = "ababbc", k = 2
# Output: 5
# Explanation: The longest substring is "ababb", as 'a' is repeated 2 times and 'b' is repeated 3 times.

# Constraints:
# 1 <= s.length <= 104
# s consists of only lowercase English letters.
# 1 <= k <= 105


# Code
class Solution:
    def longestSubstring(self, s: str, k: int) -> int:
        """
        Find the length of the longest substring where each character appears at least k times.
        
        Approach: Divide and Conquer
        - If a character appears less than k times, it cannot be part of any valid substring
        - Split the string at such characters and recursively solve for each segment
        
        Time Complexity: O(n^2) worst case, O(n log n) average case
        Space Complexity: O(n) for recursion stack
        """
        return self._longestSubstringHelper(s, k)
    
    def _longestSubstringHelper(self, s: str, k: int) -> int:
        # Base case: empty string
        if not s:
            return 0
        
        # Count frequency of each character
        char_count = {}
        for char in s:
            char_count[char] = char_count.get(char, 0) + 1
        
        # Find characters that appear less than k times
        invalid_chars = set()
        for char, count in char_count.items():
            if count < k:
                invalid_chars.add(char)
        
        # If no invalid characters, entire string is valid
        if not invalid_chars:
            return len(s)
        
        # Split string at invalid characters and recursively solve
        max_len = 0
        start = 0
        
        for i, char in enumerate(s):
            if char in invalid_chars:
                # Process substring before this invalid character
                if i > start:
                    max_len = max(max_len, self._longestSubstringHelper(s[start:i], k))
                start = i + 1
        
        # Process remaining substring after last invalid character
        if start < len(s):
            max_len = max(max_len, self._longestSubstringHelper(s[start:], k))
        
        return max_len


# Alternative Solution: Sliding Window with Unique Character Constraint
class Solution2:
    def longestSubstring(self, s: str, k: int) -> int:
        """
        Alternative approach using sliding window.
        Try all possible numbers of unique characters (1 to 26).
        
        Time Complexity: O(26 * n) = O(n)
        Space Complexity: O(1) - fixed size arrays
        """
        max_len = 0
        
        # Try all possible numbers of unique characters
        for unique_count in range(1, 27):  # At most 26 unique characters (lowercase)
            char_count = [0] * 26
            left = 0
            unique = 0  # Number of unique characters in current window
            valid = 0   # Number of characters that appear at least k times
            
            for right in range(len(s)):
                # Expand window
                idx = ord(s[right]) - ord('a')
                if char_count[idx] == 0:
                    unique += 1
                char_count[idx] += 1
                
                if char_count[idx] == k:
                    valid += 1
                
                # Shrink window if too many unique characters
                while unique > unique_count:
                    left_idx = ord(s[left]) - ord('a')
                    if char_count[left_idx] == k:
                        valid -= 1
                    char_count[left_idx] -= 1
                    if char_count[left_idx] == 0:
                        unique -= 1
                    left += 1
                
                # Update result if all characters in window are valid
                if unique == unique_count and valid == unique_count:
                    max_len = max(max_len, right - left + 1)
        
        return max_len


# Note
# Algorithm: Divide and Conquer
# Key insight: If a character appears less than k times, it cannot be part of any valid substring.
# Therefore, we can split the string at positions where such characters appear and recursively 
# solve for each segment.
#
# Steps:
# 1. Count frequency of all characters in the current substring
# 2. Find characters that appear less than k times (invalid characters)
# 3. If no invalid characters exist, the entire substring is valid
# 4. Otherwise, split at invalid characters and recursively solve for each segment
# 5. Return the maximum length found
#
# Time Complexity: O(n^2) worst case (when string needs to be split many times)
#                  O(n log n) average case (balanced splits)
# Space Complexity: O(n) for recursion stack


# Testcase
def test_longestSubstring():
    solution = Solution()
    
    # Test case 1
    assert solution.longestSubstring("aaabb", 3) == 3
    
    # Test case 2
    assert solution.longestSubstring("ababbc", 2) == 5
    
    # Test case 3: No valid substring
    assert solution.longestSubstring("abcde", 2) == 0
    
    # Test case 4: Entire string is valid
    assert solution.longestSubstring("aabbcc", 2) == 6
    
    # Test case 5: Single character
    assert solution.longestSubstring("a", 1) == 1
    
    # Test case 6: Single character, k too large
    assert solution.longestSubstring("a", 2) == 0
    
    # Test case 7: Mixed valid and invalid
    assert solution.longestSubstring("ababacb", 3) == 0
    
    # Test case 8: Complex case
    assert solution.longestSubstring("bbaaacbd", 3) == 3
    
    print("All test cases passed!")


# Test Result
if __name__ == "__main__":
    test_longestSubstring()
    
    # Also test the alternative solution
    solution2 = Solution2()
    assert solution2.longestSubstring("aaabb", 3) == 3
    assert solution2.longestSubstring("ababbc", 2) == 5
    print("Alternative solution also works!")
