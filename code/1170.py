# 1170. Compare Strings by Frequency of the Smallest Character
# Medium
# Topics
# conpanies icon
# Companies
# Hint
# Let the function f(s) be the frequency of the lexicographically smallest character in a non-empty string s. For example, if s = "dcce" then f(s) = 2 because the lexicographically smallest character is 'c', which has a frequency of 2.

# You are given an array of strings words and another array of query strings queries. For each query queries[i], count the number of words in words such that f(queries[i]) < f(W) for each W in words.

# Return an integer array answer, where each answer[i] is the answer to the ith query.

 

# Example 1:

# Input: queries = ["cbd"], words = ["zaaaz"]
# Output: [1]
# Explanation: On the first query we have f("cbd") = 1, f("zaaaz") = 3 so f("cbd") < f("zaaaz").
# Example 2:

# Input: queries = ["bbb","cc"], words = ["a","aa","aaa","aaaa"]
# Output: [1,2]
# Explanation: On the first query only f("bbb") < f("aaaa"). On the second query both f("aaa") and f("aaaa") are both > f("cc").
 

# Constraints:

# 1 <= queries.length <= 2000
# 1 <= words.length <= 2000
# 1 <= queries[i].length, words[i].length <= 10
# queries[i][j], words[i][j] consist of lowercase English letters.

"""
================================================================================
PROBLEM EXPLANATION
================================================================================

WHAT IS f(s)?
------------
f(s) = frequency of the lexicographically smallest character in string s

Examples:
- f("dcce") = 2 → smallest char is 'c', appears 2 times
- f("cbd") = 1 → smallest char is 'b', appears 1 time  
- f("zaaaz") = 3 → smallest char is 'a', appears 3 times
- f("bbb") = 3 → smallest char is 'b', appears 3 times
- f("cc") = 2 → smallest char is 'c', appears 2 times

THE TASK:
--------
For each query queries[i], count how many words W in words satisfy:
    f(queries[i]) < f(W)

Example 1:
- queries = ["cbd"], words = ["zaaaz"]
- f("cbd") = 1, f("zaaaz") = 3
- Since 1 < 3, count = 1 → Output: [1]

Example 2:
- queries = ["bbb","cc"], words = ["a","aa","aaa","aaaa"]
- f("bbb") = 3
  - f("a") = 1, f("aa") = 2, f("aaa") = 3, f("aaaa") = 4
  - Count where 3 < f(W): only "aaaa" (f=4) → count = 1
- f("cc") = 2
  - Count where 2 < f(W): "aaa" (f=3) and "aaaa" (f=4) → count = 2
- Output: [1, 2]

APPROACH 1 - SIMPLE (O(Q × W)):
--------------------------------
1. Create helper function f(s) to calculate frequency of smallest character
2. Precompute f(W) for all words
3. For each query, calculate f(query) and count words with f(W) > f(query)
   - Compare with all words: O(W) per query

APPROACH 2 - OPTIMIZED (O(W log W + Q log W)):
-----------------------------------------------
1. Create helper function f(s)
2. Precompute and SORT f(W) for all words: O(W log W)
3. For each query, use binary search to count: O(log W) per query
   - Sort word frequencies once
   - Use bisect_right to find count of words with f(W) > f(query)
   
This is faster when Q is large (many queries)!

TIME COMPLEXITY EXPLANATION:
---------------------------
Let's break down what happens:

1. Computing f(s) for ONE string:
   - `min(s)` scans the string to find smallest char → O(L) where L = length of s
   - `s.count()` scans the string to count occurrences → O(L)
   - Total: O(L) per string

APPROACH 1 - SIMPLE:
--------------------
2. Preprocessing (compute f(W) for all words):
   - For each word: O(L_word) where L_word = length of that word
   - Total: O(W × L_max) where W = number of words, L_max = maximum word length

3. Processing queries:
   - For each query:
     a) Compute f(query): O(L_query) where L_query = query length
     b) Compare with W precomputed values: O(W) - linear scan
   - Total: O(Q × (L_max + W)) where Q = number of queries

Overall: O(W × L_max + Q × (L_max + W))
Since L_max ≤ 10 (constant): O(W + Q × W) = O(Q × W)

APPROACH 2 - OPTIMIZED (with binary search):
--------------------------------------------
2. Preprocessing (compute and SORT f(W) for all words):
   - Compute f(W): O(W × L_max)
   - Sort: O(W log W)
   - Total: O(W × L_max + W log W) = O(W log W) since L_max is constant

3. Processing queries:
   - For each query:
     a) Compute f(query): O(L_query) = O(L_max) = O(1)
     b) Binary search to count: O(log W)
   - Total: O(Q × log W)

Overall: O(W log W + Q × log W)

COMPARISON:
----------
- Simple: O(Q × W) - good when Q is small
- Optimized: O(W log W + Q × log W) - better when Q is large!
- When Q >> W, optimized is much faster!

IMPORTANT: What is "max string length" (L_max)?
- L_max = the maximum length among ALL strings (both queries and words)
- From constraints: all strings are ≤ 10 characters
- So L_max ≤ 10, which means it's effectively a constant!
"""


class Solution:
    def numSmallerByFrequency(self, queries: list[str], words: list[str]) -> list[int]:
        """
        SIMPLE APPROACH: O(Q × W)
        For each query, compare with all words.
        """
        def f(s: str) -> int:
            if not s:
                return 0
            smallest_char = min(s)
            return s.count(smallest_char)
        
        # Precompute f(W) for all words
        word_freqs = [f(word) for word in words]
        
        # For each query, count words where f(query) < f(word)
        result = []
        for query in queries:
            query_freq = f(query)
            # Count how many words have f(W) > f(query)
            count = sum(1 for wf in word_freqs if wf > query_freq)
            result.append(count)
        
        return result
    
    def numSmallerByFrequency_optimized(self, queries: list[str], words: list[str]) -> list[int]:
        """
        OPTIMIZED APPROACH: O(W log W + Q log W)
        Sort word frequencies and use binary search.
        
        Key insight: Instead of comparing with all words (O(W)),
        we can sort word frequencies and use binary search (O(log W)).
        """
        import bisect
        
        def f(s: str) -> int:
            if not s:
                return 0
            smallest_char = min(s)
            return s.count(smallest_char)
        
        # Precompute and SORT word frequencies
        word_freqs = sorted([f(word) for word in words])
        
        result = []
        for query in queries:
            query_freq = f(query)
            # Use binary search to find how many words have f(W) > f(query)
            # bisect_right finds the insertion point where query_freq would be inserted
            # to keep the list sorted. All elements after this point are > query_freq.
            count = len(word_freqs) - bisect.bisect_right(word_freqs, query_freq)
            result.append(count)
        
        return result


# Test cases
if __name__ == "__main__":
    sol = Solution()
    
    test_cases = [
        (["cbd"], ["zaaaz"], [1]),
        (["bbb", "cc"], ["a", "aa", "aaa", "aaaa"], [1, 2]),
    ]
    
    print("="*60)
    print("Testing SIMPLE approach (O(Q × W)):")
    print("="*60)
    
    for queries, words, expected in test_cases:
        result = sol.numSmallerByFrequency(queries, words)
        print(f"\nqueries = {queries}, words = {words}")
        print(f"Result: {result} (expected {expected})")
        assert result == expected
    
    print("\n" + "="*60)
    print("Testing OPTIMIZED approach (O(W log W + Q log W)):")
    print("="*60)
    
    for queries, words, expected in test_cases:
        result_simple = sol.numSmallerByFrequency(queries, words)
        result_optimized = sol.numSmallerByFrequency_optimized(queries, words)
        print(f"\nqueries = {queries}, words = {words}")
        print(f"  Simple:    {result_simple}")
        print(f"  Optimized:  {result_optimized}")
        assert result_simple == result_optimized == expected
    
    print("\n" + "="*60)
    print("✅ All test cases passed!")
    print("\n💡 TIP:")
    print("  - Use numSmallerByFrequency() for simplicity")
    print("  - Use numSmallerByFrequency_optimized() when Q (queries) is large!")
    print("="*60)