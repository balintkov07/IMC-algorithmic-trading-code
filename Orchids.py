from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import numpy as np
# start copying
import collections
from collections import defaultdict
import copy
import numpy as np 

class Trader:

  def __init__(self):
    self.position = {"STARFRUIT": 0, "AMETHYSTS": 0, "ORCHIDS": 0, "CHOCOLATE": 0, "STRAWBERRIES": 0, "ROSES": 0, "GIFT_BASKET": 0,"COCONUT": 0,"COCONUT_COUPON":0}
    self.position_limit = {"STARFRUIT": 20, "AMETHYSTS": 20, "ORCHIDS": 100, "CHOCOLATE": 250, "STRAWBERRIES": 350, "ROSES": 60, "GIFT_BASKET": 60,"COCONUT": 300,"COCONUT_COUPON":600}
    self.offer_VWAP = 0
    self.bid_VWAP = 0
    self.position_BASKET = 0
    self.position_limit_BASKET = 60 
    self.residual = 0
    self.MACD_storer = []
    self.B_ingredients = ["CHOCOLADE","ROSES","STRAWBERRIES"]
    self.storer = {"CHOCOLADE": [], "ROSES": [], "STRAWBERRIES": []}
    self.orchids_profits = 0

  def run(self, state: TradingState):
    # Only method required. It takes all buy and sell orders for all symbols as an input, and outputs a list of orders to be sent

    print("timestamp: ")
    print(state.timestamp)
    # print("listings: ")
    # print(state.listings)
    # print("observations: ")
    # print(state.observations)

    conversions = 0

    result = {}
    for product in state.order_depths:
      order_depth: OrderDepth = state.order_depths[product]
      orders: List[Order] = []
      conversion_observations = state.observations.conversionObservations

      
    
      if product == "ORCHIDS":
        print(product + ": Buy orders (OrderDepths): " + str(order_depth.buy_orders))
        print(product + ": Sell orders (OrderDepths): " + str(order_depth.sell_orders))

        print("Conversion observations: ")
    
        print(conversion_observations[product])

        position = int(state.position.get(product, 0))  # sanity check

        print("Orchid positions: " + str(position))

        best_sell_pr = min(order_depth.sell_orders.keys())
        best_buy_pr = max(order_depth.buy_orders.keys())
        spread = best_sell_pr - best_buy_pr

        max_long = self.position_limit[product] - position
        max_short = -self.position_limit[product] - position
        
        #They sell, we buy
        foreign_ask = conversion_observations[product].askPrice + conversion_observations[product].transportFees + conversion_observations[product].importTariff
        #They buy, we sell
        foreign_bid = conversion_observations[product].bidPrice - conversion_observations[product].transportFees - conversion_observations[product].exportTariff
    
        print(f"foreign_ask: {foreign_ask} vs best_buy_price: {best_buy_pr}, foreing_bid: {foreign_bid} vs best_sell_price: {best_sell_pr}")

        #We sell
        for domestic_price, volume in order_depth.buy_orders.items():
          if foreign_ask < domestic_price: # Import and sell domestically: They sell it abroad for less than they will buy it for domestically
            position_size = max(max_short, -volume)
            orders.append(Order(product, domestic_price, position_size))
            conversions += position_size
            self.position[product] += position_size
            self.orchids_profits += -position_size * (domestic_price - foreign_ask)
    
        for domestic_price, volume in order_depth.sell_orders.items():
          if foreign_bid > domestic_price: # Buy domestically and export: They sell it domestically for lower than they will buy it abroad
            position_size = min(max_long, -volume)
            orders.append(Order(product, domestic_price, position_size))
            conversions += position_size
            self.position[product] += -position_size
            self.orchids_profits += position_size * (foreign_bid - domestic_price)
    
        result[product] = orders

    traderData = "SAMPLE"

    print("New Orchid positions: " + str(result['ORCHIDS']))
    print("Conversions: " + str(conversions))
    print("Orchids profits: " + str(self.orchids_profits))
      
    return result, conversions, traderData