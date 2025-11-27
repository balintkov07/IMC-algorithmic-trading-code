import math
import copy
import numpy as np
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import pandas as pd


class Trader:

  # HELPER FUNCTIONS:

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

  def vwap_condensation(self, state: TradingState) -> Dict[str, List[Order]]:
    

  # Oscilation strategy with imbedded market-making:
  def oscilation_strategy(self, state: TradingState, product, MA, cap):

    order_depth = state.order_depths[product]
    orders: list[Order] = []

    ordered_sell = self.sort_asc(order_depth.sell_orders)
    ordered_buy = self.sort_desc(order_depth.buy_orders)

    best_sell_pr = list(ordered_sell.items())[0][0]
    best_buy_pr = list(ordered_buy.items())[0][0]

    current_position = state.position[product]

    for ask, vol in ordered_sell.items():
      if ((ask < MA) or ((state.position[product] < 0) and (ask == MA))) and current_position < cap:
        order_volume = min(-vol, cap - current_position)
        current_position += order_volume
        orders.append(Order(product, ask, order_volume))

    undercut_buy = best_buy_pr + 1
    undercut_sell = best_sell_pr - 1

    bid_pr = min(undercut_buy,
                 MA - 1)  # we will shift this by 1 to beat this price
    sell_pr = max(undercut_sell, MA + 1)

    if (current_position < cap) and (state.position[product] < 0):
      num = min(cap, cap - current_position)
      orders.append(Order(product, min(undercut_buy + 1, MA - 1), num))
      current_position += num

    if (current_position < cap) and (state.position[product] > 15):
      num = min(cap, cap - current_position)
      orders.append(Order(product, min(undercut_buy - 1, MA - 1), num))
      current_position += num

    if current_position < cap:
      num = min(cap, cap - current_position)
      orders.append(Order(product, bid_pr, num))
      current_position += num

    current_position = state.position[product]

    for bid, vol in ordered_buy.items():
      if ((bid > MA) or ((state.position[product] > 0) and (bid == MA))) and current_position > -cap:
        order_volume = max(-vol, -cap - current_position)
        # order_volume is a negative number denoting how much we will sell
        current_position += order_volume
        assert (order_volume <= 0)
        orders.append(Order(product, bid, order_volume))

    if (current_position > -cap) and (state.position[product] > 0):
      num = max(-cap, -cap - current_position)
      orders.append(Order(product, max(undercut_sell - 1, MA + 1), num))
      current_position += num

    if (current_position > -cap) and (state.position[product] < -15):
      num = max(-cap, -cap - current_position)
      orders.append(Order(product, max(undercut_sell + 1, MA + 1), num))
      current_position += num

    if current_position > -cap:
      num = max(-cap, -cap - current_position)
      orders.append(Order(product, sell_pr, num))
      current_position += num

    return orders

  
  def run(self, state: TradingState) -> Dict[str, List[Order]]:

    POSITION_LIMIT = {'STARFRUIT': 20, 'AMETHYSTS': 20}
    result = {}

    for product in state.order_depths.keys():

      # if product == "STARFRUIT":

      #   order_depth = state.order_depths[product]
      #   orders: list[Order] = []

      #   # fair price calculation
      #   if len(order_depth.sell_orders) != 0:
      #     sp = list(order_depth.sell_orders.keys())
      #     sv = list(order_depth.sell_orders.values())
      #     offer_VWAP = sum([x * y for x, y in zip(sp, sv)]) / sum(
      #         order_depth.sell_orders.values())

      #   if len(order_depth.buy_orders) != 0:
      #     bp = list(order_depth.buy_orders.keys())
      #     bv = list(order_depth.buy_orders.values())
      #     bid_VWAP = sum([x * y for x, y in zip(bp, bv)]) / sum(
      #         order_depth.buy_orders.values())

      #   if len(order_depth.sell_orders) != 0 and len(order_depth.buy_orders) != 0:
      #     acceptable_price = (bid_VWAP + offer_VWAP) / 2

      #   # compute the best bid/ask prices and compute current position restrictions
      #   inventory_current = state.position.get("STARFRUIT", 0)
      #   max_buy = POSITION_LIMIT[product] - inventory_current
      #   max_sell = -(POSITION_LIMIT[product] + inventory_current)

      #   # buy all the orders from the ask chain below the predicted price
      #   for price, volume in self.sort_asc(order_depth.sell_orders):
      #     if price <= acceptable_price:
      #       orders.append(Order(product, price, min(-volume, max_buy)))
      #       max_buy -= min(-volume, max_buy)

      #   # sell all the orders from the bid chain above the predicted price
      #   for price, volume in self.sort_desc(order_depth.buy_orders):
      #     if price >= acceptable_price:
      #       orders.append(Order(product, price, max(-volume, max_sell)))
      #       max_sell += max(-volume, max_sell)

      #   result[product] = orders

      if product == "AMETHYSTS":

        storerMA15 = []

        order_depth: OrderDepth = state.order_depths[product]
        orders: list[Order] = []

        # will store the market price at every iteration
        if len(order_depth.sell_orders) != 0 and len(order_depth.buy_orders) != 0:
          best_ask = min(order_depth.sell_orders.keys())
          best_bid = max(order_depth.buy_orders.keys())
          midpoint = (best_ask + best_bid) / 2
          storerMA15.append(midpoint)

        # this starts running after 15 iterations
        if len(storerMA15) >= 15:
          MA = np.mean(storerMA15[-15:])
          result[product] = self.oscilation_strategy(state, product, MA, POSITION_LIMIT[product])
          
    return result
