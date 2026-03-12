# 409. Longest Palindrome
# Solved
# Easy
# Topics
# Companies
# Given a string s which consists of lowercase or uppercase letters, return the length 
# of the longest palindrome that can be built with those letters.

# Letters are case sensitive, for example, "Aa" is not considered a palindrome.

# Example 1:
# Input: s = "abccccdd"
# Output: 7
# Explanation: One longest palindrome that can be built is "dccaccd", whose length is 7.

# Example 2:
# Input: s = "a"
# Output: 1
# Explanation: The longest palindrome that can be built is "a", whose length is 1.

# Constraints:
# 1 <= s.length <= 2000
# s consists of lowercase and/or uppercase English letters only.


# Code - Using Counter
from collections import Counter

class Solution:
    def longestPalindrome(self, s: str) -> int:
        """
        Find the length of the longest palindrome that can be built from the string.
        
        Approach: Frequency Counting with Counter
        - Count frequency of each character
        - For palindromes: pairs go on both sides, at most one odd-count char in center
        - Use all even counts, use (odd_count - 1) for odd counts
        - Add 1 if there's any character with odd count (for center)
        
        Time Complexity: O(n) where n is length of string
        Space Complexity: O(1) - at most 52 characters (26 lowercase + 26 uppercase)
        
        Example walkthrough for s = "abccccdd":
        Counter: {'c': 4, 'd': 2, 'a': 1, 'b': 1}
        - 'c': count=4 (even) → use all 4 → length += 4
        - 'd': count=2 (even) → use all 2 → length += 2
        - 'a': count=1 (odd) → use 0 (1-1) → length += 0, has_odd = True
        - 'b': count=1 (odd) → use 0 (1-1) → length += 0, has_odd = True
        - Total: 4 + 2 + 0 + 0 = 6
        - Add 1 for center (since has_odd = True) → 7
        - Result: 7 (can form "dccaccd" or "ccaddacc")
        """
        # Count frequency of each character
        char_count = Counter(s)
        
        length = 0
        has_odd = False
        
        for count in char_count.values():
            if count % 2 == 0:
                # Even count: use all characters (they form pairs)
                length += count
            else:
                # Odd count: use (count - 1) characters (form pairs), keep 1 for potential center
                length += count - 1
                has_odd = True
        
        # If we have any character with odd count, we can place one in the center
        if has_odd:
            length += 1
        
        return length


# Code - Alternative: More concise version
class Solution2:
    def longestPalindrome(self, s: str) -> int:
        """
        More concise version using Counter.
        Same logic but written more compactly.
        """
        char_count = Counter(s)
        
        # Sum all even counts and (odd_count - 1) for odd counts
        length = sum(count - (count % 2) for count in char_count.values())
        
        # Add 1 if there's any odd count (for center)
        # If length < len(s), it means we had odd counts, so we can add 1
        return length + (1 if length < len(s) else 0)


# Note
# Algorithm: Frequency Counting
# Key insight: In a palindrome, characters appear in pairs (except possibly one in center).
#
# Steps:
# 1. Count frequency of each character using Counter
# 2. For each character:
#    - If count is even: use all characters (they form pairs)
#    - If count is odd: use (count - 1) characters (form pairs), save 1 for center
# 3. If any character had odd count, add 1 for the center position
#
# Example: s = "abccccdd"
# - 'c': 4 (even) → use 4 → contributes 4
# - 'd': 2 (even) → use 2 → contributes 2  
# - 'a': 1 (odd) → use 0 → contributes 0, but marks has_odd = True
# - 'b': 1 (odd) → use 0 → contributes 0
# - Total: 4 + 2 + 0 + 0 = 6
# - Add 1 for center → 7
# - Can form: "dccaccd" or "ccaddacc"
#
# Time Complexity: O(n) - single pass to count, single pass through counts
# Space Complexity: O(1) - Counter stores at most 52 unique characters


# Testcase
def test_longestPalindrome():
    solution = Solution()
    solution2 = Solution2()
    
    # Test case 1
    assert solution.longestPalindrome("abccccdd") == 7
    assert solution2.longestPalindrome("abccccdd") == 7
    
    # Test case 2
    assert solution.longestPalindrome("a") == 1
    assert solution2.longestPalindrome("a") == 1
    
    # Test case 3: All even counts
    assert solution.longestPalindrome("aabbcc") == 6
    assert solution2.longestPalindrome("aabbcc") == 6
    
    # Test case 4: All odd counts
    assert solution.longestPalindrome("abc") == 1
    assert solution2.longestPalindrome("abc") == 1
    
    # Test case 5: Single character repeated
    assert solution.longestPalindrome("aaaa") == 4
    assert solution2.longestPalindrome("aaaa") == 4
    
    # Test case 6: Mixed case (case sensitive)
    assert solution.longestPalindrome("Aa") == 1  # 'A' and 'a' are different
    assert solution2.longestPalindrome("Aa") == 1
    
    # Test case 7: All same character
    assert solution.longestPalindrome("zzzzz") == 5
    assert solution2.longestPalindrome("zzzzz") == 5
    
    # Test case 8: Empty string (edge case)
    assert solution.longestPalindrome("") == 0
    assert solution2.longestPalindrome("") == 0
    
    # Test case 9: Complex case
    assert solution.longestPalindrome("racecar") == 7
    assert solution2.longestPalindrome("racecar") == 7
    
    print("All test cases passed!")


# Test Result
if __name__ == "__main__":
    test_longestPalindrome()