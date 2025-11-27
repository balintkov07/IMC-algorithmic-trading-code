from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import numpy as np

class Trader:
  
    def __init__(self):
        self.offer_VWAP = 0
        self.bid_VWAP = 0
        self.position = 0
        self.position_limit = 20
        self.prices_storer = []
        self.position_limit_orchid = 100

    # unused (since yielding suboptimal performance) EMA helper function 
    def calculate_ema(self, prices, period, weighting_factor=0.2):
      ema_values = []
  
      # Calculate SMA for the initial window
      sma = np.mean(prices[:period])
      ema_values.append(sma)
  
      # Calculate EMA for subsequent data points
      for i in range(period, len(prices)):
        ema = (prices[i] - ema_values[-1]) * weighting_factor + ema_values[-1]
        ema_values.append(ema)

      return ema_values

    def run(self, state: TradingState):
        # Only method required. It takes all buy and sell orders for all symbols as an input, and outputs a list of orders to be sent
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))
        
        result = {}
        
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []

            print(product + ": Buy orders (OrderDepths): " + str(order_depth.buy_orders))
            print(product + ": Sell orders (OrderDepths): " + str(order_depth.sell_orders))

            #### our creation 

            if product == "AMETHYSTS" or product == "STARFRUIT":
          
              self.position = int(state.position.get(product,0)) # sanity check
              
              if len(order_depth.sell_orders) != 0:
                sp = list(order_depth.sell_orders.keys())
                sv = [-1 * value for value in order_depth.sell_orders.values()]
                self.offer_VWAP = sum([x*y for x,y in zip(sp, sv)])/np.sum([-1 * value for value in order_depth.sell_orders.values()])
      
              if len(order_depth.buy_orders) != 0:
                bp = list(order_depth.buy_orders.keys())
                bv = list(order_depth.buy_orders.values())
                self.bid_VWAP = sum([x*y for x,y in zip(bp,bv)])/sum(order_depth.buy_orders.values())
      
      
              acceptable_price = (self.offer_VWAP + self.bid_VWAP)/2 
              
              print("Acceptable price : " + str(acceptable_price))
              print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))
      
              if len(order_depth.sell_orders) != 0:
                  for price , volume in order_depth.sell_orders.items():
                    if price <= acceptable_price:
                       max_buy = self.position_limit - self.position
                       orders.append(Order(product, price, min(-volume, max_buy)))
                       self.position += min(-volume, max_buy)
      
              if len(order_depth.buy_orders) != 0:
                for price , volume in order_depth.buy_orders.items():
                  if price >= acceptable_price:
                    max_sell = -self.position_limit - self.position
                    orders.append(Order(product, price, max(-volume, max_sell)))
                    self.position += max(-volume, max_sell)


            if product == "ORCHIDS":
              self.position = int(state.position.get(product, 0))

            result[product] = orders
              
        traderData = "SAMPLE" 

        conversions = 1
        return result, conversions, traderData