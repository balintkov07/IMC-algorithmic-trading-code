import math
import copy
import numpy as np
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import pandas as pd


class Trader:

  def __init__(self):
    self.fast_ema_period = 5
    self.emas = [0.0]
    self.prices_storer = []
    self.deviations = []

  # sorter_bid_chain (selling)
  def sort_desc(self, my_dict):
    sorted_dict = dict(
        sorted(my_dict.items(), key=lambda item: item[0], reverse=True))
    return sorted_dict

  # sorter_ask_chain (buying)
  def sort_asc(self, my_dict):
    sorted_dict = dict(
        sorted(my_dict.items(), key=lambda item: item[0], reverse=False))
    return sorted_dict

  # EMA computation
  def calculate_ema(self,
                    prices: List[int],
                    period: int,
                    previous_ema=None) -> float:
    if not prices:
      return previous_ema if previous_ema else 0

    alpha = 2 / (period + 1)
    ema = prices[0] if previous_ema is None else previous_ema
    for price in prices[-period:]:
      ema = alpha * price + (1 - alpha) * ema

    return ema

  def run(self, state: TradingState):

    POSITION_LIMIT = {'STARFRUIT': 20, 'AMETHYSTS': 20}
    result = {}
    for product in state.order_depths.keys():

      if product == "STARFRUIT":
        order_depth = state.order_depths[product]
        orders: list[Order] = []
        result[product] = orders

      if product == "AMETHYSTS":
        order_depth = state.order_depths[product]
        orders: list[Order] = []

        # prices = list(order_depth.sell_orders.keys()) + list(order_depth.buy_orders.keys())
        # deviation = 1 * np.std(list(order_depth.buy_orders.keys()) + list(order_depth.sell_orders.keys()))
        

        ordered_sell = self.sort_asc(order_depth.sell_orders)
        ordered_buy = self.sort_desc(order_depth.buy_orders)

        best_sell_pr = list(ordered_sell.items())[0][0]
        best_buy_pr = list(ordered_buy.items())[0][0]

        # create a list of all the prices
        self.prices_storer.append((best_sell_pr + best_buy_pr) / 2)
        # create a list of deviation where n-th deviation is the deviation for n back
        # we gonna only use the last one
        self.deviations.append(np.std(self.prices_storer))

        deviation = self.deviations[-1]

        ema = self.calculate_ema(self.prices_storer[-1], self.fast_ema_period,
                                 self.emas[-1])
        self.emas.append(ema)

        for price in order_depth.sell_orders.keys():

          if price < ema - deviation:
            if abs(state.position.get('AMETHYSTS',0)) <= POSITION_LIMIT[product]:
              capacity = POSITION_LIMIT[product] - state.position.get('AMETHYSTS', 0)
              orders.append(Order(product, price, min(capacity,-state.sell_orders[price])))

        for price in order_depth.buy_orders.keys():

          if price > ema + deviation:
            if abs(state.position.get('AMETHYSTS',0)) <= POSITION_LIMIT[product]:
              capacity = -(POSITION_LIMIT[product] - state.position.get('AMETHYSTS', 0))
              orders.append(Order(product, price, max(capacity,-state.buy_orders[price])))
        result[product] = orders
    return result
