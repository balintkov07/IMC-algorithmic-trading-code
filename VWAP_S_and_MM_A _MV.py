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
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []

            print(product + ": Buy orders (OrderDepths): " + str(order_depth.buy_orders))
            print(product + ": Sell orders (OrderDepths): " + str(order_depth.sell_orders))

            #### our creation 
            if product == "STARFRUIT":
              self.position_S = int(state.position.get(product,0)) # sanity check

              if len(order_depth.sell_orders) != 0:
                sp = list(order_depth.sell_orders.keys())
                sv = [-1 * value for value in order_depth.sell_orders.values()]
                self.offer_VWAP = sum([x*y for x,y in zip(sp, sv)])/np.sum([-1 * value for value in order_depth.sell_orders.values()])

              if len(order_depth.buy_orders) != 0:
                bp = list(order_depth.buy_orders.keys())
                bv = list(order_depth.buy_orders.values())
                self.bid_VWAP = sum([x*y for x,y in zip(bp,bv)])/sum(order_depth.buy_orders.values())


              acceptable_price = (self.offer_VWAP + self.bid_VWAP)/2 # Participant should calculate this value
              print("Acceptable price : " + str(acceptable_price))
              print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))

              if len(order_depth.sell_orders) != 0:
                  for price , volume in order_depth.sell_orders.items():
                    if price <= acceptable_price:
                       max_buy = self.position_limit - self.position_S
                       orders.append(Order(product, price, min(-volume, max_buy)))
                       self.position_S += min(-volume, max_buy)
                       # self.max_buy -= min(-volume, self.max_buy)
                  # best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                  # if int(best_ask) < acceptable_price:
                  #     print("BUY", str(-best_ask_amount) + "x", best_ask)
                  #     orders.append(Order(product, best_ask, -best_ask_amount))

              if len(order_depth.buy_orders) != 0:
                for price , volume in order_depth.buy_orders.items():
                  if price >= acceptable_price:
                    max_sell = -self.position_limit - self.position_S
                    orders.append(Order(product, price, max(-volume, max_sell)))
                    self.position_S += max(-volume, max_sell)

                  # best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                  # if int(best_bid) > acceptable_price:
                  #     print("SELL", str(best_bid_amount) + "x", best_bid)
                  #     orders.append(Order(product, best_bid, -best_bid_amount))

              result[product] = orders

            if product == "AMETHYSTS": # extreme oscilation here 

              spread_threshold = 5  # Adjust this threshold (to be optimized)

              if len(order_depth.buy_orders) == 0 or len(order_depth.sell_orders) == 0:
                result[product] = orders
                continue  # Skip if there are no buy or sell orders
  
              self.position_A = int(state.position.get(product, 0))  # Update position for the current product

              if len(order_depth.buy_orders) > 1: 
                highest_bid_price, second_highest_bid_price = sorted(order_depth.buy_orders.keys(), reverse=True)[:2]
                average_buy_volume = int(round((order_depth.buy_orders[highest_bid_price] + order_depth.buy_orders[second_highest_bid_price]) / 2))
              else:
                highest_bid_price = max(order_depth.buy_orders.keys())
                average_buy_volume = order_depth.buy_orders[highest_bid_price]
                
                
              if len(order_depth.sell_orders) > 1:
                lowest_ask_price, second_lowest_ask_price = sorted(order_depth.sell_orders.keys())[:2]
                average_sell_volume = int(round((order_depth.sell_orders[lowest_ask_price] + order_depth.sell_orders[second_lowest_ask_price]) / 2))
              else:
                lowest_ask_price = min(order_depth.sell_orders.keys())
                average_sell_volume = order_depth.sell_orders[lowest_ask_price]

              # Calculate spread
              spread = lowest_ask_price - highest_bid_price

              # Check if spread is above threshold and there's a profitable spread
              if spread > spread_threshold and highest_bid_price < lowest_ask_price:
                # Calculate buy price slightly above highest bid price
                buy_price = highest_bid_price + 1
                max_buy_volume = min(average_buy_volume, 20)  # Consider maximum position size
                max_buy_volume = min(max_buy_volume, self.position_limit - self.position_A)  # Consider position limit
                if max_buy_volume > 0:
                  orders.append(Order(product, buy_price, max_buy_volume))

                  # Calculate sell price slightly below lowest ask price
                sell_price = lowest_ask_price - 1
                max_sell_volume = min(average_sell_volume, 20)  # Consider maximum position size
                max_sell_volume = min(max_sell_volume, -self.position_limit - self.position_A)  # Consider position limit
                if max_sell_volume < 0:
                  orders.append(Order(product, sell_price, max_sell_volume))
                  

              result[product] = orders

        traderData = "SAMPLE" 

        conversions = 0
        return result, conversions, traderData