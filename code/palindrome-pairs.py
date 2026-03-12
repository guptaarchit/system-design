# 336. Palindrome Pairs
# Hard
# Topics
# conpanies icon
# Companies
# Hint
# You are given a 0-indexed array of unique strings words.

# A palindrome pair is a pair of integers (i, j) such that:

# 0 <= i, j < words.length,
# i != j, and
# words[i] + words[j] (the concatenation of the two strings) is a palindrome.
# Return an array of all the palindrome pairs of words.

# You must write an algorithm with O(sum of words[i].length) runtime complexity.

 

# Example 1:

# Input: words = ["abcd","dcba","lls","s","sssll"]
# Output: [[0,1],[1,0],[3,2],[2,4]]
# Explanation: The palindromes are ["abcddcba","dcbaabcd","slls","llssssll"]
# Example 2:

# Input: words = ["bat","tab","cat"]
# Output: [[0,1],[1,0]]
# Explanation: The palindromes are ["battab","tabbat"]
# Example 3:

# Input: words = ["a",""]
# Output: [[0,1],[1,0]]
# Explanation: The palindromes are ["a","a"]
 

# Constraints:

# 1 <= words.length <= 5000
# 0 <= words[i].length <= 300
# words[i] consists of lowercase English letters.


def is_palindrome(s):
    """Check if a string is a palindrome. O(len(s))"""
    return s == s[::-1]


def palindrome_pairs(words):
    """
    Optimized solution using hash map and prefix/suffix checking.
    
    Time Complexity: O(n * k²) where n = number of words, k = average word length
        - Building hash map: O(n * k)
        - For each word: O(k) iterations
        - For each prefix/suffix: O(k) palindrome check + O(k) reverse
        - Overall: O(n * k²) which satisfies O(sum of words[i].length)
    
    Space Complexity: O(n * k) for hash map
    
    Key Insight - Why Different Pair Orders?
    
    We split words[i] = prefix + suffix and check two cases:
    
    CASE 1: Prefix is palindrome → Pair: [other_word, current_word]
    ----------------------------------------------------------------
    If prefix is palindrome and reverse(suffix) exists as words[j]:
      words[j] + words[i] = reverse(suffix) + prefix + suffix
      
      Since prefix is palindrome: prefix = reverse(prefix)
      So: reverse(suffix) + prefix + suffix = reverse(suffix) + reverse(prefix) + suffix
      This equals: reverse(suffix + prefix + suffix) = PALINDROME ✓
      
      Example: words = ["bat", "tab"]
        words[0] = "bat" = prefix("") + suffix("bat")
        prefix "" is palindrome ✓
        reverse(suffix) = reverse("bat") = "tab" = words[1] ✓
        Pair: [1, 0] = ["tab", "bat"]
        Check: "tab" + "bat" = "tabbat" → palindrome ✓
    
    CASE 2: Suffix is palindrome → Pair: [current_word, other_word]
    -----------------------------------------------------------------
    If suffix is palindrome and reverse(prefix) exists as words[j]:
      words[i] + words[j] = prefix + suffix + reverse(prefix)
      
      Since suffix is palindrome: suffix = reverse(suffix)
      So: prefix + suffix + reverse(prefix) = prefix + reverse(suffix) + reverse(prefix)
      This equals: reverse(reverse(prefix) + suffix + prefix) = PALINDROME ✓
      
      Example: words = ["lls", "ll"]
        words[0] = "lls" = prefix("l") + suffix("ls")
        suffix "ls" is NOT palindrome, try another split...
        words[0] = "lls" = prefix("ll") + suffix("s")
        suffix "s" is palindrome ✓
        reverse(prefix) = reverse("ll") = "ll" = words[1] ✓
        Pair: [0, 1] = ["lls", "ll"]
        Check: "lls" + "ll" = "llsll" → palindrome ✓
    
    Why different orders?
    - Case 1: We put OTHER word FIRST → [j, i] = [other_word, current_word]
    - Case 2: We put CURRENT word FIRST → [i, j] = [current_word, other_word]
    
    This is because:
    - Case 1 forms: words[j] + words[i] (other + current)
    - Case 2 forms: words[i] + words[j] (current + other)
    """
    # Build hash map: word -> index
    word_map = {word: i for i, word in enumerate(words)}
    result = []
    
    for i, word in enumerate(words):
        n = len(word)
        
        # Check all possible splits: word = prefix + suffix
        for j in range(n + 1):
            prefix = word[:j]
            suffix = word[j:]
            
            # Case 1: prefix is palindrome, check if reverse(suffix) exists
            # words[i] + words[j] = prefix + suffix + reverse(suffix) = palindrome
            if is_palindrome(prefix):
                reversed_suffix = suffix[::-1]
                if reversed_suffix in word_map and word_map[reversed_suffix] != i:
                    result.append([word_map[reversed_suffix], i])
            
            # Case 2: suffix is palindrome, check if reverse(prefix) exists
            # words[j] + words[i] = reverse(prefix) + prefix + suffix = palindrome
            # Only check if suffix is non-empty to avoid duplicates with Case 1
            if j < n and is_palindrome(suffix):
                reversed_prefix = prefix[::-1]
                if reversed_prefix in word_map and word_map[reversed_prefix] != i:
                    result.append([i, word_map[reversed_prefix]])
    
    return result


# Test cases
if __name__ == "__main__":
    # Example 1
    words1 = ["abcd", "dcba", "lls", "s", "sssll"]
    print(f"Input: words = {words1}")
    result1 = palindrome_pairs(words1)
    print(f"Output: {result1}")
    print("Expected: [[0,1],[1,0],[3,2],[2,4]]")
    print()
    
    # Example 2
    words2 = ["bat", "tab", "cat"]
    print(f"Input: words = {words2}")
    result2 = palindrome_pairs(words2)
    print(f"Output: {result2}")
    print("Expected: [[0,1],[1,0]]")
    print()
    
    # Example 3
    words3 = ["a", ""]
    print(f"Input: words = {words3}")
    result3 = palindrome_pairs(words3)
    print(f"Output: {result3}")
    print("Expected: [[0,1],[1,0]]")
    print()
    
    # Additional test case
    words4 = ["lls", "s"]
    print(f"Input: words = {words4}")
    result4 = palindrome_pairs(words4)
    print(f"Output: {result4}")
    print("Explanation: 'lls' + 's' = 'llss' (not palindrome)")
    print("            's' + 'lls' = 'slls' (palindrome!)")
