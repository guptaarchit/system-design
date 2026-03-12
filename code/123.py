# 123. Best Time to Buy and Sell Stock III
# Hard
# Topics
# conpanies icon
# Companies
# You are given an array prices where prices[i] is the price of a given stock on the ith day.

# Find the maximum profit you can achieve. You may complete at most two transactions.

# Note: You may not engage in multiple transactions simultaneously (i.e., you must sell the stock before you buy again).

 

# Example 1:

# Input: prices = [3,3,5,0,0,3,1,4]
# Output: 6
# Explanation: Buy on day 4 (price = 0) and sell on day 6 (price = 3), profit = 3-0 = 3.
# Then buy on day 7 (price = 1) and sell on day 8 (price = 4), profit = 4-1 = 3.
# Example 2:

# Input: prices = [1,2,3,4,5]
# Output: 4
# Explanation: Buy on day 1 (price = 1) and sell on day 5 (price = 5), profit = 5-1 = 4.
# Note that you cannot buy on day 1, buy on day 2 and sell them later, as you are engaging multiple transactions at the same time. You must sell before buying again.
# Example 3:

# Input: prices = [7,6,4,3,1]
# Output: 0
# Explanation: In this case, no transaction is done, i.e. max profit = 0.
 

# Constraints:

# 1 <= prices.length <= 105
# 0 <= prices[i] <= 105

from typing import List

"""
PROBLEM EXPLANATION:
===================

This is "Best Time to Buy and Sell Stock III" - a harder version where you can make
AT MOST 2 transactions (buy + sell = 1 transaction).

KEY DIFFERENCES FROM PROBLEM II:
- Problem II: Unlimited transactions → Just capture all profit opportunities
- Problem III: At most 2 transactions → Need to strategically choose when to trade

WHY IT'S HARDER:
- You can't just capture every profit opportunity
- You need to decide: Should I make 1 big transaction or 2 smaller ones?
- Example: [1,2,3,4,5]
  - 1 transaction: Buy at 1, sell at 5 → profit = 4
  - 2 transactions: Buy at 1, sell at 2 (profit 1), buy at 3, sell at 5 (profit 2) → total = 3
  - Best: 1 transaction = 4

SOLUTION APPROACH:
=================

We use Dynamic Programming with 4 states to track the maximum profit at each stage:

State 1: buy1  - Maximum profit after buying the first stock
         (Negative value because we spent money)
         
State 2: sell1 - Maximum profit after selling the first stock
         (Positive value = profit from first transaction)
         
State 3: buy2  - Maximum profit after buying the second stock
         (Can only happen after sell1, so we subtract price from sell1 profit)
         
State 4: sell2 - Maximum profit after selling the second stock
         (Final answer = profit from both transactions)

At each day, we can:
- Stay in the same state (do nothing)
- Transition to the next state (buy or sell)

EXAMPLE WALKTHROUGH:
===================

prices = [3,3,5,0,0,3,1,4]

Day 0 (price=3):
  buy1 = -3   (buy at 3)
  sell1 = 0   (can't sell yet)
  buy2 = -3   (can't buy twice yet, but initialize)
  sell2 = 0

Day 1 (price=3):
  buy1 = max(-3, -3) = -3   (keep previous buy)
  sell1 = max(0, -3+3) = 0  (no profit if sell)
  buy2 = max(-3, 0-3) = -3  (can buy after sell1=0)
  sell2 = max(0, -3+3) = 0

Day 2 (price=5):
  buy1 = max(-3, -5) = -3   (keep buying at 3)
  sell1 = max(0, -3+5) = 2   (sell: profit 2!)
  buy2 = max(-3, 2-5) = -3  (better to keep previous buy2)
  sell2 = max(0, -3+5) = 2

Day 3 (price=0):
  buy1 = max(-3, -0) = 0    (better to buy at 0!)
  sell1 = max(2, 0+0) = 2   (keep previous profit)
  buy2 = max(-3, 2-0) = 2   (buy at 0 after selling first)
  sell2 = max(2, 2+0) = 2

Day 4 (price=0):
  buy1 = max(0, -0) = 0     (already bought at 0)
  sell1 = max(2, 0+0) = 2
  buy2 = max(2, 2-0) = 2    (already bought at 0)
  sell2 = max(2, 2+0) = 2

Day 5 (price=3):
  buy1 = 0                   (bought at 0)
  sell1 = max(2, 0+3) = 3    (sell first: profit 3!)
  buy2 = max(2, 3-3) = 2     (can buy again)
  sell2 = max(2, 2+3) = 5    (sell second: profit 5)

Day 6 (price=1):
  buy1 = max(0, -1) = 0
  sell1 = max(3, 0+1) = 3
  buy2 = max(2, 3-1) = 2     (better: buy at 1 after selling first)
  sell2 = max(5, 2+1) = 5

Day 7 (price=4):
  buy1 = 0
  sell1 = max(3, 0+4) = 4
  buy2 = 2                   (bought at 1)
  sell2 = max(5, 2+4) = 6    (sell second: profit 6!)
  
Final answer: 6

This represents:
- Transaction 1: Buy at 0 (day 4), sell at 3 (day 6) → profit = 3
- Transaction 2: Buy at 1 (day 7), sell at 4 (day 8) → profit = 3
- Total = 6
"""

class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        """
        Dynamic Programming Approach - Track States for 2 Transactions
        
        KEY INSIGHT: We need to track 4 states for at most 2 transactions:
        1. buy1:  Max profit if we've bought the stock once (we've spent money)
        2. sell1: Max profit if we've sold once (we've made profit from 1st transaction)
        3. buy2:  Max profit if we've bought the stock twice (we've spent money again)
        4. sell2: Max profit if we've sold twice (we've made profit from 2nd transaction)
        
        At each day, we can:
        - Keep the same state (do nothing)
        - Transition to next state (buy or sell)
        
        Example: prices = [3,3,5,0,0,3,1,4]
        
        Day 0 (price=3):
          buy1 = -3 (buy at 3)
          sell1 = 0 (can't sell without buying)
          buy2 = -3 (can't buy twice yet)
          sell2 = 0
        
        Day 1 (price=3):
          buy1 = max(-3, -3) = -3 (keep previous or buy today - same)
          sell1 = max(0, -3 + 3) = 0 (keep or sell: no profit)
          ...
        
        Day 4 (price=0):
          buy1 = max(-3, -0) = 0 (better to buy at 0!)
          sell1 = max(0, -3 + 0) = 0
          ...
        
        Day 6 (price=3):
          buy1 = 0 (bought at 0)
          sell1 = max(0, 0 + 3) = 3 (sell: profit 3!)
          buy2 = max(-inf, 3 - 3) = 0 (buy again after selling)
          ...
        
        Day 8 (price=4):
          sell2 = max(0, 0 + 4) = 4 (sell second time: profit 4)
          Total: 3 + 4 = 7? Wait, let me recalculate...
        
        Actually: buy at 0, sell at 3 (profit 3), buy at 1, sell at 4 (profit 3)
        Total = 3 + 3 = 6
        
        Time: O(n)
        Space: O(1)
        """
        # Initialize states
        # buy1: profit after first buy (negative because we spent money)
        buy1 = -prices[0]
        # sell1: profit after first sell
        sell1 = 0
        # buy2: profit after second buy (negative because we spent money)
        buy2 = -prices[0]
        # sell2: profit after second sell
        sell2 = 0
        
        for i in range(1, len(prices)):
            # Update states in reverse order to avoid using updated values
            
            # After second sell: max(keep previous sell2, sell the stock we bought in buy2)
            sell2 = max(sell2, buy2 + prices[i])
            
            # After second buy: max(keep previous buy2, buy after first sell)
            buy2 = max(buy2, sell1 - prices[i])
            
            # After first sell: max(keep previous sell1, sell the stock we bought in buy1)
            sell1 = max(sell1, buy1 + prices[i])
            
            # After first buy: max(keep previous buy1, buy today)
            buy1 = max(buy1, -prices[i])
        
        return sell2  # Maximum profit is after completing both transactions
    
    def maxProfit_verbose(self, prices: List[int]) -> int:
        """
        Same approach with more detailed variable names for clarity
        """
        # Track maximum profit at each stage
        first_buy_profit = -prices[0]   # Profit after buying first stock
        first_sell_profit = 0            # Profit after selling first stock
        second_buy_profit = -prices[0]  # Profit after buying second stock
        second_sell_profit = 0           # Profit after selling second stock
        
        for price in prices[1:]:
            # Update in reverse order to use previous day's values
            
            # Can we get more profit by selling the second stock today?
            second_sell_profit = max(second_sell_profit, second_buy_profit + price)
            
            # Can we get more profit by buying second stock today (after first sell)?
            second_buy_profit = max(second_buy_profit, first_sell_profit - price)
            
            # Can we get more profit by selling the first stock today?
            first_sell_profit = max(first_sell_profit, first_buy_profit + price)
            
            # Can we get more profit by buying first stock today?
            first_buy_profit = max(first_buy_profit, -price)
        
        return second_sell_profit
    
    def maxProfit_generalized(self, prices: List[int]) -> int:
        """
        Generalized approach for k transactions (here k=2)
        buy[i] = max profit holding after (i+1)th buy
        sell[i] = max profit after completing (i+1) transactions
        Update in reverse (i=k-1..0) so sell[i-1] is from previous day.

        Example: prices = [1,2,3,4,5], k=2
        Day 0: buy=[-1,-1], sell=[0,0]
        Day 1: sell[1]=max(0,-1+2)=1, buy[1]=max(-1,0-2)=-1
               sell[0]=max(0,-1+2)=1, buy[0]=max(-1,-2)=-1
        Day 2: sell[1]=max(1,-1+3)=2, buy[1]=max(-1,1-3)=-1
               sell[0]=max(1,-1+3)=2, buy[0]=max(-1,-3)=-1
        Day 3: sell[1]=max(2,-1+4)=3, buy[1]=max(-1,2-4)=-1
               sell[0]=max(2,-1+4)=3, buy[0]=max(-1,-4)=-1
        Day 4: sell[1]=max(3,-1+5)=4, buy[1]=max(-1,3-5)=-1
               sell[0]=max(3,-1+5)=4, buy[0]=max(-1,-5)=-1
        Return sell[1]=4 (one transaction: buy 1, sell 5)
        """
        k = 2
        # dp[i][j] where i = transaction number (0-indexed), j = day
        # For space optimization, we only need previous day's values
        buy = [-prices[0]] * k
        sell = [0] * k
        
        for price in prices[1:]:
            # Update in reverse order
            for i in range(k-1, -1, -1):
                if i == 0:
                    sell[i] = max(sell[i], buy[i] + price)
                    buy[i] = max(buy[i], -price)
                else:
                    sell[i] = max(sell[i], buy[i] + price)
                    buy[i] = max(buy[i], sell[i-1] - price)
        
        return sell[k-1]