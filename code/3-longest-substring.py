# 3. Longest Substring Without Repeating Characters
# Medium
# Given a string s, find the length of the longest substring without duplicate characters.
# Example: s = "abcabcbb" -> 3 ("abc"), s = "pwwkew" -> 3 ("wke")

class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        """
        Sliding window + hash set. Expand right, shrink left when duplicate.
        O(n) time, O(min(n, charset)) space.
        """
        seen = set()
        left = 0
        max_len = 0
        for right in range(len(s)):
            while s[right] in seen:
                seen.remove(s[left])
                left += 1
            seen.add(s[right])
            max_len = max(max_len, right - left + 1)
        return max_len
