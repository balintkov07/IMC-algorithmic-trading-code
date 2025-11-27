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
    #self.N = norm.cdf
  # BLACK_SCHOLES:


  # def BS_CALL(self, S, K, T, r, sigma):
  #     d1 = (np.log(S/K) + (r + sigma**2/2)*T) / (sigma*np.sqrt(T))
  #     d2 = d1 - sigma * np.sqrt(T)
  #     return S * self.N(d1) - K * np.exp(-r*T)* self.N(d2)

  # def BS_PUT(self, S, K, T, r, sigma):
  #     d1 = (np.log(S/K) + (r + sigma**2/2)*T) / (sigma*np.sqrt(T))
  #     d2 = d1 - sigma* np.sqrt(T)
  #     return K*np.exp(-r*T)*self.N(-d2) - S*self.N(-d1)

  # REGRESSION STRATEGY
  def values_extract(self, order_dict, buy=0):
    tot_vol = 0
    best_val = -1
    mxvol = -1

    for ask, vol in order_dict.items():
        if(buy==0):
            vol *= -1
        tot_vol += vol
        if tot_vol > mxvol:
            mxvol = vol
            best_val = ask

    return tot_vol, best_val

  def compute_next_price_product(self,product):
    if product == "CHOCOLADE":
      coeff_choclate = [0.1334, 0.9837, 0.0163]
      implied_price = coeff_choclate[0]+np.dot(coeff_choclate[-2:], self.storer[product][-2:])
    elif product == "ROSES":
      coeff_roses = [4.2207, 0.9927, 0.0161,0, -0.0091]
      implied_price = coeff_roses[0]+np.dot(coeff_roses[-3:], self.storer[product][-3:])
    else : 
      coeff_straw = [0.3486, 0.8672, 0.1125, 0.0316, -0.113]
      implied_price = coeff_straw[0]+np.dot(coeff_straw[-4:], self.storer[product][-4:])
    return int(round(implied_price))

  def compute_orders_regression(self, product, order_depth, acc_bid, acc_ask, LIMIT):
    orders: list[Order] = []

    osell = collections.OrderedDict(sorted(order_depth.sell_orders.items()))
    obuy = collections.OrderedDict(sorted(order_depth.buy_orders.items(), reverse=True))

    sell_vol, best_sell_pr = self.values_extract(osell)
    buy_vol, best_buy_pr = self.values_extract(obuy, 1)

    cpos = self.position[product]

    for ask, vol in osell.items():
        if ((ask <= acc_bid) or ((self.position[product]<0) and (ask == acc_bid+1))) and cpos < LIMIT:
            order_for = min(-vol, LIMIT - cpos)
            cpos += order_for
            assert(order_for >= 0)
            orders.append(Order(product, ask, order_for))

    undercut_buy = best_buy_pr + 1
    undercut_sell = best_sell_pr - 1

    bid_pr = min(undercut_buy, acc_bid) # we will shift this by 1 to beat this price
    sell_pr = max(undercut_sell, acc_ask)

    if cpos < LIMIT:
        num = LIMIT - cpos
        orders.append(Order(product, bid_pr, num))
        cpos += num

    cpos = self.position[product]


    for bid, vol in obuy.items():
        if ((bid >= acc_ask) or ((self.position[product]>0) and (bid+1 == acc_ask))) and cpos > -LIMIT:
            order_for = max(-vol, -LIMIT-cpos)
            # order_for is a negative number denoting how much we will sell
            cpos += order_for
            assert(order_for <= 0)
            orders.append(Order(product, bid, order_for))

    if cpos > -LIMIT:
        num = -LIMIT-cpos
        orders.append(Order(product, sell_pr, num))
        cpos += num

    return orders
    # finish REGRESSION STARTEGY

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

      if product in self.B_ingredients:
        self.position[product] = int(state.position.get(product,0))
        self.storer[product].append(self.compute_mid_price(state,product))
        if len(self.storer[product]) > 4:
          implied_price = self.compute_next_price_product(product)
          LB = implied_price -1
          UP = implied_price +1 
          orders = self.compute_orders_regression(product, order_depth, LB, UP, self.position_limit[product])
        result[product] = orders

      #MACD
      if product == "ROSES":
        self.position[product] = int(state.position.get(product,0))
        self.storer[product].append(self.compute_mid_price(state,product))

        if len(self.storer[product]) > 15: 
          # STRATEGY PARAMETERS 
          look_back_value_short = 5 # to be optimized
          look_back_value_long = 50 # to be optimized
          max_deviation = 2 # to be optimized

          LMA = np.mean(self.storer[product][look_back_value_long:])
          SMA = np.mean(self.storer[product][-look_back_value_short:])

          MACD = SMA - LMA 
          self.MACD_storer.append(MACD)

          if len(order_depth.sell_orders) != 0:
            if self.MACD_storer[-2] > 0 and self.MACD_storer[-1] < 0:
              price_buy = min(order_depth.sell_orders.keys())
              volume = order_depth.sell_orders[price_buy]
              max_buy = self.position_limit[product] - self.position[product]
              orders.append(Order(product, price_buy, min(-volume, max_buy)))
              self.position[product] += min(-volume, max_buy)

          if len(order_depth.buy_orders) != 0:
            if self.MACD_storer[-2] < 0 and self.MACD_storer[-1] > 0:
              price_sell = max(order_depth.buy_orders.keys())
              volume = order_depth.buy_orders[price_sell]
              max_sell = -self.position_limit[product] - self.position[product]
              orders.append(Order(product, price_sell, max(-volume, max_sell)))
              self.position[product] += max(-volume, max_sell)

        result[product] = orders

    traderData = "SAMPLE"

    return result, conversions, traderData