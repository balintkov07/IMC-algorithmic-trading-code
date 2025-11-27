from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import numpy as np

class Trader:

    def __init__(self):
        self.offer_VWAP = 0
        self.bid_VWAP = 0
        self.position_S = 0
        self.position_A = 0
        self.position_limit = 20
        print("This fucking code is running")

    def run(self, state: TradingState):
        # Only method required. It takes all buy and sell orders for all symbols as an input, and outputs a list of orders to be sent
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))

        result = {}
      
        if product == "AMETHYSTS":
          order_depth: OrderDepth = state.order_depths[product]
  
          orders: List[Order] = []
          self.position_A = int(state.position.get(product,0)) # sanity check
  
          # optimal price determination 
          optimal_spread = 0 # to be backtested 
          fair_value_buy = 10000 - optimal_spread
          fair_value_sell = 10000 + optimal_spread
  
          print("Acceptable price to buy : " + str(fair_value_buy) + " and to sell : " + str(fair_value_sell) )
          print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))
  
          if len(order_depth.sell_orders) != 0:
            for price, volume in order_depth.sell_orders.items():
                if price < fair_value_buy:
                    position_remain = self.position_limit - self.position_A
                    max_buy = min(position_remain, -volume) 
                    orders.append(Order(product, price, max_buy))
                    self.position_A += max_buy
  
          if len(order_depth.buy_orders) != 0:
            for price, volume in order_depth.buy_orders.items():
                if price > fair_value_sell:
                    position_remain = -self.position_limit - self.position_A
                    max_sell = max(position_remain, -volume) #max takes the less negative value
                    orders.append(Order(product, price, max_sell))
                    self.position_A += max_sell
  
          result[product] = orders

        traderData = "SAMPLE" 

        conversions = 0
        return result, conversions, traderData