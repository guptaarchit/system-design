# 122. Best Time to Buy and Sell Stock II
# Medium
# Topics
# conpanies icon
# Companies
# You are given an integer array prices where prices[i] is the price of a given stock on the ith day.

# On each day, you may decide to buy and/or sell the stock. You can only hold at most one share of the stock at any time. However, you can sell and buy the stock multiple times on the same day, ensuring you never hold more than one share of the stock.

# Find and return the maximum profit you can achieve.

 

# Example 1:

# Input: prices = [7,1,5,3,6,4]
# Output: 7
# Explanation: Buy on day 2 (price = 1) and sell on day 3 (price = 5), profit = 5-1 = 4.
# Then buy on day 4 (price = 3) and sell on day 5 (price = 6), profit = 6-3 = 3.
# Total profit is 4 + 3 = 7.
# Example 2:

# Input: prices = [1,2,3,4,5]
# Output: 4
# Explanation: Buy on day 1 (price = 1) and sell on day 5 (price = 5), profit = 5-1 = 4.
# Total profit is 4.
# Example 3:

# Input: prices = [7,6,4,3,1]
# Output: 0
# Explanation: There is no way to make a positive profit, so we never buy the stock to achieve the maximum profit of 0.
 

# Constraints:

# 1 <= prices.length <= 3 * 104
# 0 <= prices[i] <= 104

from typing import List

class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        """
        Greedy Approach - Capture Every Profit Opportunity
        
        KEY INSIGHT: Since we can buy and sell multiple times, we should capture
        every profit opportunity. If the price increases from day i to day i+1,
        we can buy on day i and sell on day i+1 to capture that profit.
        
        STRATEGY: Sum up all positive differences between consecutive days.
        
        Example: prices = [7,1,5,3,6,4]
        Day 0->1: 1-7 = -6 (skip, price decreased)
        Day 1->2: 5-1 = +4 (capture profit: buy at 1, sell at 5)
        Day 2->3: 3-5 = -2 (skip, price decreased)
        Day 3->4: 6-3 = +3 (capture profit: buy at 3, sell at 6)
        Day 4->5: 4-6 = -2 (skip, price decreased)
        
        Total profit = 4 + 3 = 7
        
        WHY THIS WORKS:
        If prices are [a, b, c] where a < b < c:
        - Strategy 1: Buy at a, sell at c → profit = c - a
        - Strategy 2: Buy at a, sell at b, then buy at b, sell at c → profit = (b-a) + (c-b) = c - a
        Both strategies give the same profit! So we can always break down long trades
        into consecutive day trades without losing profit.
        
        Time: O(n)
        Space: O(1)
        """
        profit = 0
        
        for i in range(1, len(prices)):
            # If price increased, capture the profit
            if prices[i] > prices[i-1]:
                profit += prices[i] - prices[i-1]
        
        return profit
    
    def maxProfit_verbose(self, prices: List[int]) -> int:
        """
        Same approach but with more explicit logic for understanding
        """
        if not prices:
            return 0
        
        profit = 0
        buy_price = None
        
        for i in range(len(prices)):
            # Decide when to buy
            if buy_price is None:
                # Buy if next day's price is higher (or if it's the last day, don't buy)
                if i < len(prices) - 1 and prices[i+1] > prices[i]:
                    buy_price = prices[i]
            else:
                # Sell if price is about to drop (or if it's the last day)
                if i == len(prices) - 1 or prices[i+1] < prices[i]:
                    profit += prices[i] - buy_price
                    buy_price = None
        
        return profit
    
    def maxProfit_dp(self, prices: List[int]) -> int:
        """
        Dynamic Programming Approach (for understanding)
        
        State: At each day, we can either:
        - Hold a stock (bought previously)
        - Not hold a stock (sold or never bought)
        
        Example: prices = [7,1,5,3,6,4]
        Day 0: hold=-7 (bought), not_hold=0
        Day 1: hold=max(-7, 0-1)=-1 (buy at 1), not_hold=max(0, -7+1)=0
        Day 2: hold=max(-1, 0-5)=-1 (keep), not_hold=max(0, -1+5)=4 (sell)
        Day 3: hold=max(-1, 4-3)=1 (buy at 3), not_hold=max(4, -1+3)=4
        Day 4: hold=max(1, 4-6)=1 (keep), not_hold=max(4, 1+6)=7 (sell)
        Day 5: hold=max(1, 7-4)=3, not_hold=max(7, 1+4)=7
        Return not_hold=7
        
        Time: O(n)
        Space: O(1) - optimized from O(n)
        """
        # hold: max profit if we hold a stock
        # not_hold: max profit if we don't hold a stock
        hold = -prices[0]  # Buy on first day
        not_hold = 0
        
        for i in range(1, len(prices)):
            # Today's states
            new_hold = max(hold, not_hold - prices[i])  # Keep holding or buy today
            new_not_hold = max(not_hold, hold + prices[i])  # Keep not holding or sell today
            
            hold = new_hold
            not_hold = new_not_hold
        
        return not_hold  # Final state: we want to not hold (sold everything)