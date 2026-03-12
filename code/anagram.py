# Given an array of strings strs, group the anagrams together. You can return the answer in any order.

 

# Example 1:

# Input: strs = ["eat","tea","tan","ate","nat","bat"]

# Output: [["bat"],["nat","tan"],["ate","eat","tea"]]

# Explanation:

# There is no string in strs that can be rearranged to form "bat".
# The strings "nat" and "tan" are anagrams as they can be rearranged to form each other.
# The strings "ate", "eat", and "tea" are anagrams as they can be rearranged to form each other.
# Example 2:

# Input: strs = [""]

# Output: [[""]]

# Example 3:

# Input: strs = ["a"]

# Output: [["a"]]

 

# Constraints:

# 1 <= strs.length <= 104
# 0 <= strs[i].length <= 100
# strs[i] consists of lowercase English letters.

from typing import List
from collections import defaultdict

class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        """
        Group Anagrams - Approach 1: Sorted String as Key
        
        IDEA: Anagrams have the same characters, just in different order.
        If we sort each string, anagrams will have the same sorted form.
        Use the sorted string as a key to group anagrams together.
        
        Example: 
        - "eat", "tea", "ate" all sort to "aet"
        - "tan", "nat" both sort to "ant"
        
        Time: O(n * k log k) where n = number of strings, k = average length
        Space: O(n * k)
        """
        groups = defaultdict(list)
        
        for s in strs:
            # Sort characters to create a unique key for anagrams
            key = ''.join(sorted(s))
            groups[key].append(s)
        
        return list(groups.values())
    
    def groupAnagrams_approach2(self, strs: List[str]) -> List[List[str]]:
        """
        Group Anagrams - Approach 2: Character Count as Key
        
        IDEA: Instead of sorting, count frequency of each character.
        Anagrams will have the same character frequencies.
        Use a tuple of character counts as the key.
        
        Example:
        - "eat" -> (a:1, e:1, t:1) -> (1,0,0,0,1,0,...,1,0,...)
        - "tea" -> (a:1, e:1, t:1) -> same tuple
        
        Time: O(n * k) where n = number of strings, k = average length
        Space: O(n * k)
        
        More efficient for longer strings since we avoid sorting!
        """
        groups = defaultdict(list)
        
        for s in strs:
            # Count frequency of each character (a-z)
            count = [0] * 26
            for char in s:
                count[ord(char) - ord('a')] += 1
            
            # Use tuple as key (lists can't be dictionary keys)
            key = tuple(count)
            groups[key].append(s)
        
        return list(groups.values())