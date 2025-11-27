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
              print("           PRINT DEBUGGING HERE               ")
              self.position_A = state.position.get(product,0) # sanity check
              print("SELF position: " + str(self.position_A))
              max_buy = 20 - self.position_A
              print("max buy: " + str(max_buy))
              max_sell = -self.position_limit - self.position_A
              print("max sell: " + str(max_sell))

              # optimal price determination 
              optimal_spread = 2 # to be backtested 
              fair_value_buy = 1000 - optimal_spread
              fair_value_sell = 1000 + optimal_spread

              # extract the best price and the best associated volume 
              if len(order_depth.sell_orders) and len(order_depth.buy_orders) != 0:
                print(product + ": Sell orders (OrderDepths): " + str(order_depth.sell_orders))
                print(product + ": Buy orders (OrderDepths): " + str(order_depth.buy_orders))
                # best_buy_price = min(order_depth.sell_orders.keys())
                # print("Best buy: " + str(best_buy_price))
                # best_buy_volume = order_depth.sell_orders[best_buy_price]
                # best_sell_price = max(order_depth.buy_orders.keys())
                # best_sell_volume = order_depth.buy_orders[best_sell_price]
                
                # we are fucking market makers here !!!!!!!!
                # in every round ....
                orders.append(Order(product, 1000, max_buy)) # try to enter the short position above 1000 
                orders.append(Order(product, 9999, max_sell)) # try to enter the long position below 1000 
                
                print("              FINISHED PRINTING!                     ")
              result[product] = orders

        traderData = "SAMPLE" 

        conversions = 0
        return result, conversions, traderData