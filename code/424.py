# 424. Longest Repeating Character Replacement
# Medium
# Topics
# conpanies icon
# Companies
# You are given a string s and an integer k. You can choose any character of the string and change it to any other uppercase English character. You can perform this operation at most k times.

# Return the length of the longest substring containing the same letter you can get after performing the above operations.

 

# Example 1:

# Input: s = "ABAB", k = 2
# Output: 4
# Explanation: Replace the two 'A's with two 'B's or vice versa.
# Example 2:

# Input: s = "AABABBA", k = 1
# Output: 4
# Explanation: Replace the one 'A' in the middle with 'B' and form "AABBBBA".
# The substring "BBBB" has the longest repeating letters, which is 4.
# There may exists other ways to achieve this answer too.
 

# Constraints:

# 1 <= s.length <= 105
# s consists of only uppercase English letters.
# 0 <= k <= s.length

class Solution:
    def characterReplacement(self, s: str, k: int) -> int:
        # Sliding window approach
        # Track frequency of each character in current window
        char_count = {}
        left = 0
        max_freq = 0  # Maximum frequency of any character in current window
        max_length = 0
        
        for right in range(len(s)):
            # Expand window by adding character at right pointer
            char_count[s[right]] = char_count.get(s[right], 0) + 1
            max_freq = max(max_freq, char_count[s[right]])
            
            # If window size - max_freq > k, we need more than k replacements
            # Shrink window from left
            while (right - left + 1) - max_freq > k:
                char_count[s[left]] -= 1
                left += 1
                # Note: We don't need to update max_freq here because
                # we only care about the maximum valid window size
            
            # Update maximum length
            max_length = max(max_length, right - left + 1)
        
        return max_length
    
    # Alternative Approach 1: Binary Search on Answer
    # Time: O(n log n), Space: O(1)
    def characterReplacement_binary_search(self, s: str, k: int) -> int:
        """
        Binary search on the answer length.
        For each candidate length, check if a valid substring exists.
        """
        def is_valid(length):
            """Check if a substring of given length exists that can be made uniform with <= k replacements"""
            char_count = {}
            max_freq = 0
            
            # Check first window
            for i in range(length):
                char_count[s[i]] = char_count.get(s[i], 0) + 1
                max_freq = max(max_freq, char_count[s[i]])
            
            if length - max_freq <= k:
                return True
            
            # Slide window
            for i in range(length, len(s)):
                char_count[s[i]] = char_count.get(s[i], 0) + 1
                char_count[s[i - length]] -= 1
                
                # Recalculate max_freq (can be optimized but this works)
                max_freq = max(char_count.values())
                if length - max_freq <= k:
                    return True
            
            return False
        
        left, right = 0, len(s)
        result = 0
        
        while left <= right:
            mid = (left + right) // 2
            if is_valid(mid):
                result = mid
                left = mid + 1
            else:
                right = mid - 1
        
        return result
    
    # Alternative Approach 2: Try Each Character as Target
    # Time: O(26n) = O(n), Space: O(1)
    def characterReplacement_per_character(self, s: str, k: int) -> int:
        """
        For each possible character (A-Z), find the longest substring
        that can be converted to all that character with <= k replacements.
        """
        max_length = 0
        
        for target_char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            left = 0
            replacements = 0
            
            for right in range(len(s)):
                # If current char is not target, we need a replacement
                if s[right] != target_char:
                    replacements += 1
                
                # Shrink window if we exceed k replacements
                while replacements > k:
                    if s[left] != target_char:
                        replacements -= 1
                    left += 1
                
                max_length = max(max_length, right - left + 1)
        
        return max_length
    
    # Alternative Approach 3: Brute Force (for understanding)
    # Time: O(n²), Space: O(1)
    def characterReplacement_brute_force(self, s: str, k: int) -> int:
        """
        Try all possible substrings and check validity.
        Not efficient but helps understand the problem.
        """
        max_length = 0
        
        for i in range(len(s)):
            char_count = {}
            max_freq = 0
            
            for j in range(i, len(s)):
                char_count[s[j]] = char_count.get(s[j], 0) + 1
                max_freq = max(max_freq, char_count[s[j]])
                
                window_size = j - i + 1
                if window_size - max_freq <= k:
                    max_length = max(max_length, window_size)
        
        return max_length