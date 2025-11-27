from types import EllipsisType
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
        self.position_BASKET = 0
        self.position_limit_BASKET = 60 
        self.residual = 0
        self.B_ingredients = ["CHOCOLADE","ROSES","STRAWBERRIES"]
        print("This fucking code is running")

    def compute_mid_price(self, state: TradingState, product): 
      order_depth: OrderDepth = state.order_depths[product]
      best_sell_pr = min(order_depth.sell_orders.keys())
      best_buy_pr = max(order_depth.buy_orders.keys())
      mid_price = (best_sell_pr + best_buy_pr) /2
      return mid_price

    def price_basket_implied(self, state: TradingState):
      implied_basket_price = 300 + 4 * self.compute_mid_price(state, "CHOCOLATE") + 6 * self.compute_mid_price(state, "STRAWBERRIES") + self.compute_mid_price(state, "ROSES")
      return implied_basket_price          

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

            # if product == "STARFRUIT":
            #   self.position_S = int(state.position.get(product,0)) # sanity check

            #   if len(order_depth.sell_orders) != 0:
            #     sp = list(order_depth.sell_orders.keys())
            #     sv = [-1 * value for value in order_depth.sell_orders.values()]
            #     self.offer_VWAP = sum([x*y for x,y in zip(sp, sv)])/np.sum([-1 * value for value in order_depth.sell_orders.values()])

            #   if len(order_depth.buy_orders) != 0:
            #     bp = list(order_depth.buy_orders.keys())
            #     bv = list(order_depth.buy_orders.values())
            #     self.bid_VWAP = sum([x*y for x,y in zip(bp,bv)])/sum(order_depth.buy_orders.values())


            #   acceptable_price = (self.offer_VWAP + self.bid_VWAP)/2 # Participant should calculate this value
            #   print("Acceptable price : " + str(acceptable_price))
            #   print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))

            #   if len(order_depth.sell_orders) != 0:
            #       for price , volume in order_depth.sell_orders.items():
            #         if price <= acceptable_price:
            #            max_buy = self.position_limit - self.position_S
            #            orders.append(Order(product, price, min(-volume, max_buy)))
            #            self.position_S += min(-volume, max_buy)
            #            # self.max_buy -= min(-volume, self.max_buy)
            #       # best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
            #       # if int(best_ask) < acceptable_price:
            #       #     print("BUY", str(-best_ask_amount) + "x", best_ask)
            #       #     orders.append(Order(product, best_ask, -best_ask_amount))

            #   if len(order_depth.buy_orders) != 0:
            #     for price , volume in order_depth.buy_orders.items():
            #       if price >= acceptable_price:
            #         max_sell = -self.position_limit - self.position_S
            #         orders.append(Order(product, price, max(-volume, max_sell)))
            #         self.position_S += max(-volume, max_sell)

            #       # best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
            #       # if int(best_bid) > acceptable_price:
            #       #     print("SELL", str(best_bid_amount) + "x", best_bid)
            #       #     orders.append(Order(product, best_bid, -best_bid_amount))

            #   result[product] = orders

            if product == "GIFT_BASKET": 
              order_depth: OrderDepth = state.order_depths[product]
              orders: List[Order] = []
              
              implied_basket_price = self.price_basket_implied(state)
              basket_price = self.compute_mid_price(state, "GIFT_BASKET")
              self.residual = basket_price - implied_basket_price
              print("BIG PRINTING BEGINS:        ")
              print("Implied basket price: " + str(implied_basket_price) + "|||||||||")
              print("Basket price: " + str(basket_price) + "|||||||||")
              print("Residual: " + str(self.residual) + "|||||||||")
              print("Position in Baskets: " + str(int(state.position.get(product,0))) + "|||||||||")
                    
              self.position_BASKET = int(state.position.get(product,0))
              best_sell_pr = min(order_depth.sell_orders.keys())
              best_buy_pr = max(order_depth.buy_orders.keys())

              #experimental basis 
              worst_sell_price = max(order_depth.sell_orders.keys())
              worst_buy_price = min(order_depth.buy_orders.keys())
              
              # BACKTESTING:
              # enter: 15 - 14.5k, 30 - 24k, 35 - 26k, 37.5 - 27k, 40 - 27.5k, 45 - 20k, 60 - 20k , 90 - 0k
              # close for 40: 10 - 27.5k , 1 - 29.5k, 5 - 29.5k, non-existant - 26.5k,
              deviation_enter =  40 # deviation to be optimized 
              deviation_close = 1 # deviation to be optimized
              fuck_around_chain = 0 # How deep is your love ? 

              # enter the trades if the time has come 
              if self.residual > deviation_enter:
                max_vol_go_short = self.position_BASKET + self.position_limit_BASKET 
                if max_vol_go_short > 0:
                  orders.append(Order(product, worst_buy_price,-max_vol_go_short))

              elif self.residual < - deviation_enter:
                max_vol_go_long = self.position_limit_BASKET - self.position_BASKET
                if max_vol_go_long > 0:
                  orders.append(Order(product, worst_sell_price,max_vol_go_long))

              # close the trades if the time has come 
              elif self.residual < deviation_close and self.position_BASKET < 0:
                volume_close = - self.position_BASKET
                orders.append(Order(product, worst_sell_price,volume_close))
                
              elif self.residual > -deviation_close and self.position_BASKET > 0:
                volume_close = self.position_BASKET
                orders.append(Order(product, worst_buy_price,-volume_close))

              result[product] = orders 

            # doing both sides does not fucking work 
            # if product in self.B_ingredients and int(state.position.get("GIFT_BASKET",0)) != 0: 
            #   num_of_baskets = int(state.position.get("GIFT_BASKET",0))
            #   for product in self.B_ingredients:
            #     best_sell_pr = min(order_depth.sell_orders.keys())
            #     best_buy_pr = max(order_depth.buy_orders.keys())

            #     #experimental basis 
            #     worst_sell_price = max(order_depth.sell_orders.keys())
            #     worst_buy_price = min(order_depth.buy_orders.keys())
            #     if product == "ROSES":
            #       multiplier = 1
            #     elif product =="STRAWBERRIES":
            #       multiplier = 6
            #     else :
            #       multiplier = 4

            #     if self.residual > 40:
            #       optimal_long = multiplier*abs(num_of_baskets)
            #       if optimal_long > 0:
            #         orders.append(Order(product,worst_sell_price,optimal_long))

            #     elif self.residual < - 40:
            #       optimal_short = multiplier*abs(num_of_baskets)
            #       if optimal_short > 0:
            #         orders.append(Order(product,worst_buy_price,-optimal_short))

            #     # close the trades if the time has come 
            #     elif self.residual < 10 and self.position_BASKET < 0:
            #       volume_close = multiplier*abs(self.position_BASKET)
            #       orders.append(Order(product, worst_buy_price,-volume_close))

            #     elif self.residual > - 10 and self.position_BASKET > 0:
            #       volume_close = multiplier*abs(self.position_BASKET)
            #       orders.append(Order(product,worst_sell_price,volume_close))
                  
            #     result[product] = orders
                  
                
                
                
              
            # if product == "AMETHYSTS":
            #   order_depth: OrderDepth = state.order_depths[product]
        
            #   orders: List[Order] = []
            #   self.position_A = int(state.position.get(product,0)) # sanity check
        
            #   # optimal price determination 
            #   optimal_spread = 0 # to be backtested 
            #   fair_value_buy = 10000 - optimal_spread
            #   fair_value_sell = 10000 + optimal_spread
        
            #   if len(order_depth.sell_orders) != 0:
            #     for price, volume in order_depth.sell_orders.items():
            #         if price < fair_value_buy:
            #             position_remain = self.position_limit - self.position_A
            #             max_buy = min(position_remain, -volume) 
            #             orders.append(Order(product, price, max_buy))
            #             self.position_A += max_buy
        
            #   if len(order_depth.buy_orders) != 0:
            #     for price, volume in order_depth.buy_orders.items():
            #         if price > fair_value_sell:
            #             position_remain = -self.position_limit - self.position_A
            #             max_sell = max(position_remain, -volume) #max takes the less negative value
            #             orders.append(Order(product, price, max_sell))
            #             self.position_A += max_sell
        
            #   result[product] = orders
        traderData = "SAMPLE" 

        conversions = 0
        return result, conversions, traderData