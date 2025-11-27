from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import numpy as np


class Trader:

  def __init__(self):
    self.position_limit = {"CHOCOLATE": 250, "ROSES": 350, "STRAWBERRIES": 60}
    self.prices_storer = {"CHOCOLATE": [1], "ROSES": [1], "STRAWBERRIES": [1]} #append to the list, the past prices. First is always one because intercept 
    coeff_roses = [4.2207, 0.9927, 0.0161,0, -0.0091]
    coeff_choclate = [0.1334, 0.9837, 0.0163]
    coeff_straw = [0.3486, 0.8672, 0.1125, 0.0316, -0.113]
    self.coeff_dict = {"CHOCOLATE": coeff_choclate, "ROSES": coeff_roses, "STRAWBERRIES": coeff_straw}
    self.positions = {"CHOCOLATE": 0, "ROSES": 0, "STRAWBERRIES": 0}
    self.dev_mid_price = 3
  
  #Given order depth for pratiuclar product return the mid price
  def compute_mid_price(self, state: OrderDepth): 
    best_bid = next(iter(state.buy_orders))
    best_ask = next(iter(state.sell_orders))
    return (best_bid + best_ask) / 2

  #Used to ocmpute the predicted price
  def dot_product(self,list1: List[int], list2: List[int]) -> int:
    result = 0
    for i in range(len(list1)):
      result += list1[i] * list2[i]
    return result
  
  def run(self, state: TradingState):
    result = {}
    for product in state.order_depths:
      order_depth: OrderDepth = state.order_depths[product]
      orders: List[Order] = []
      if product in ["CHOCOLATE", "ROSES", "STRAWBERRIES"]:
        #First we need at least number of lags amount of histoical prices
        if len(self.prices_storer[product]) < len(self.coeff_dict[product]):
          self.prices_storer[product] = self.prices_storer[product] + [self.compute_mid_price(state.order_depths[product])]
          continue
        else:
          #to the list of last price append in front the most recnet price, shift everything one to the right and remove the last elements 
          self.prices_storer[product] = [1]+[self.compute_mid_price(state.order_depths[product])] + self.prices_storer[product][1:-1]
  
        predicted_price = self.compute_mid_price(state.order_depths[product])
          
        #We buy
        for price, volume in order_depth.sell_orders.items():
            if price - self.dev_mid_price <= int(predicted_price):
              max_buy = self.position_limit[product] - self.positions[product]
              orders.append(Order(product, price, min(-volume, max_buy)))
              self.positions[product] += min(-volume, max_buy)
  
        #We sell
        for price, volume in order_depth.buy_orders.items():
            if price + self.dev_mid_price >= int(predicted_price)+1:
              max_sell = -self.position_limit[product] - self.positions[product]
              orders.append(Order(product, price, max(-volume, max_sell)))
              self.positions[product] += max(-volume, max_sell)
  
        result[product] = orders

    traderData = "SAMPLE"

    conversions = 1
    return result, conversions, traderData
