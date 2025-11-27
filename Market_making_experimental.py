from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import numpy as np


class Trader:

  def __init__(self):
    self.position_limit = {"STARFRUIT": 20, "AMETHYSTS": 20, "ORCHIDS": 100, "CHOCOLATE": 250, "STRAWBERRIES": 350, "ROSES": 60, "GIFT_BASKET": 60}

  def run(self, state: TradingState):
    # Only method required. It takes all buy and sell orders for all symbols as an input, and outputs a list of orders to be sent

    print("timestamp: ")
    print(state.timestamp)
    print("listings: ")
    print(state.listings)
    print("observations: ")
    print(state.observations)

    conversions = 0
    
    result = {}
    for product in state.order_depths:
      order_depth: OrderDepth = state.order_depths[product]
      orders: List[Order] = []
      conversion_observations = state.observations.conversionObservations

      print(product + ": Buy orders (OrderDepths): " + str(order_depth.buy_orders))
      print(product + ": Sell orders (OrderDepths): " + str(order_depth.sell_orders))

      position = int(state.position.get(product, 0))  # sanity check

      best_sell_pr = min(order_depth.sell_orders.keys())
      best_buy_pr = max(order_depth.buy_orders.keys())
      spread = best_sell_pr - best_buy_pr
      print("Price spread: " + str(spread))

      max_long = self.position_limit[product] - position
      max_short = -self.position_limit[product] - position
      
      if product == "AMETHYSTS":
        print("Considering: " + str(product))
        
        std = 3
        mean = 10000
        
        if spread > 3:
          ask = best_sell_pr - 1
          bid = best_buy_pr + 1
          orders.append(Order(product, bid, max_long))
          orders.append(Order(product, ask, max_short))
          
          result[product] = orders
          
      if product == "STARFRUIT":
        print("Considering: " + str(product))

        std = 12.5 #13.5
        mean = 5050
        spread_threshold = 4

        if spread > spread_threshold:
          if (best_sell_pr)/2 >= mean + std: # Anticipating a top
            ask = best_sell_pr - 2
            bid = best_buy_pr + 1
          if (best_buy_pr)/2 < mean - std: # Anticipating a bottom
            ask = best_sell_pr - 1
            bid = best_buy_pr + 2
          else:
            ask = best_sell_pr - 1
            bid = best_buy_pr + 1
          orders.append(Order(product, bid, max_long))
          orders.append(Order(product, ask, max_short))

          result[product] = orders

      if product == ("ORCHIDS"):
        print("Considering: " + str(product))

        print(conversion_observations[product])
        foreign_ask = conversion_observations[product].askPrice + conversion_observations[product].transportFees + conversion_observations[product].importTariff
        foreign_bid = conversion_observations[product].bidPrice - conversion_observations[product].transportFees - conversion_observations[product].exportTariff

        print(f"foreign_ask: {foreign_ask} vs best_buy_price: {best_buy_pr}, foreing_bid: {foreign_bid} vs best_sell_price: {best_sell_pr}")

        for price, volume in order_depth.buy_orders.items():
          if foreign_ask < price: # Import and sell domestically: They sell it abroad for less than they will buy it for domestically
            position_size = max(max_short, -volume)
            orders.append(Order(product, price, position_size))
            conversions += position_size
            
        for price, volume in order_depth.sell_orders.items():
          if foreign_bid > best_sell_pr: # Buy domestically and export: They sell it domestically for lower than they will buy it abroad
            position_size = min(max_long, -volume)
            orders.append(Order(product, price, position_size))
            conversions += position_size

        result[product] = orders
        
      print(f"Orders for {product}: {str(orders)}")
      
    traderData = "SAMPLE"

    return result, conversions, traderData
