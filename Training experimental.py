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
    self.prices_storer = []  # List of prices for AMETHYSTS

  # Oscilation strategy with imbedded market-making:
  def oscilation_strategy(self, state: TradingState, product, MA, cap):

    order_depth = state.order_depths[product]
    orders: list[Order] = []

    best_sell_pr = list(order_depth.sell_orders.items())[0][0]
    best_buy_pr = list(order_depth.buy_orders.items())[0][0]

    current_position = int(state.position.get(product, 0))

    for ask, vol in order_depth.sell_orders.items():
      if ((ask < MA) or ((current_position < 0) and
                         (ask == MA))) and current_position < cap:
        order_volume = min(-vol, cap - current_position)
        current_position += order_volume
        orders.append(Order(product, ask, order_volume))

    undercut_buy = best_buy_pr + 1
    undercut_sell = best_sell_pr - 1

    bid_pr = min(undercut_buy,
                 MA - 1)  # we will shift this by 1 to beat this price
    sell_pr = max(undercut_sell, MA + 1)

    if (current_position < cap) and (current_position < 0):
      num = min(cap, cap - current_position)
      orders.append(Order(product, min(undercut_buy + 1, MA - 1), num))
      current_position += num

    if (current_position < cap) and (current_position > 10):
      num = min(cap, cap - current_position)
      orders.append(Order(product, min(undercut_buy - 1, MA - 1), num))
      current_position += num

    if current_position < cap:
      num = min(cap, cap - current_position)
      orders.append(Order(product, bid_pr, num))
      current_position += num

    current_position = int(state.position.get(product, 0))

    for bid, vol in order_depth.buy_orders.items():
      if ((bid > MA) or ((current_position > 0) and
                         (bid == MA))) and current_position > -cap:
        order_volume = max(-vol, -cap - current_position)
        # order_volume is a negative number denoting how much we will sell
        current_position += order_volume
        orders.append(Order(product, bid, order_volume))

    if (current_position > -cap) and (current_position > 0):
      num = max(-cap, -cap - current_position)
      orders.append(Order(product, max(undercut_sell - 1, MA + 1), num))
      current_position += num

    if (current_position > -cap) and (current_position < -10):
      num = max(-cap, -cap - current_position)
      orders.append(Order(product, max(undercut_sell + 1, MA + 1), num))
      current_position += num

    if current_position > -cap:
      num = max(-cap, -cap - current_position)
      orders.append(Order(product, sell_pr, num))
      current_position += num

    return orders

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

  def magic_trans(self, base, deviations) -> float:
    return 1-base**-deviations

  def run(self, state: TradingState):
    # Only method required. It takes all buy and sell orders for all symbols as an input, and outputs a list of orders to be sent

    result = {}
    for product in state.order_depths:
      order_depth: OrderDepth = state.order_depths[product]
      orders: List[Order] = []

      

      # Storing the newly accessed prices in the prices_storer dictionary

      # self.prices_storer[product].extend(state.market_trades[product])

      #### our creation
      # if product == "STARFRUIT":
      #   self.position = int(state.position.get(product, 0))  # sanity check

      #   if len(order_depth.sell_orders) != 0:
      #     sp = list(order_depth.sell_orders.keys())
      #     sv = [-1 * value for value in order_depth.sell_orders.values()]
      #     self.offer_VWAP = sum([x * y for x, y in zip(sp, sv)]) / np.sum(
      #         [-1 * value for value in order_depth.sell_orders.values()])

      #   if len(order_depth.buy_orders) != 0:
      #     bp = list(order_depth.buy_orders.keys())
      #     bv = list(order_depth.buy_orders.values())
      #     self.bid_VWAP = sum([x * y for x, y in zip(bp, bv)]) / sum(
      #         order_depth.buy_orders.values())

      #   acceptable_price = (self.offer_VWAP + self.bid_VWAP) / 2  # Participant should calculate this value
      #   print("Acceptable price : " + str(acceptable_price))
      #   print("Buy Order depth : " + str(len(order_depth.buy_orders)) +
      #         ", Sell order depth : " + str(len(order_depth.sell_orders)))

      #   if len(order_depth.sell_orders) != 0:
      #     for price, volume in order_depth.sell_orders.items():
      #       if price <= acceptable_price:
      #         max_buy = self.position_limit - self.position
      #         orders.append(Order(product, price, min(-volume, max_buy)))
      #         self.position += min(-volume, max_buy)
      #         # self.max_buy -= min(-volume, self.max_buy)
      #     # best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
      #     # if int(best_ask) < acceptable_price:
      #     #     print("BUY", str(-best_ask_amount) + "x", best_ask)
      #     #     orders.append(Order(product, best_ask, -best_ask_amount))

      #   if len(order_depth.buy_orders) != 0:
      #     for price, volume in order_depth.buy_orders.items():
      #       if price >= acceptable_price:
      #         max_sell = -self.position_limit - self.position
      #         orders.append(Order(product, price, max(-volume, max_sell)))
      #         self.position += max(-volume, max_sell)

      #       # best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
      #       # if int(best_bid) > acceptable_price:
      #       #     print("SELL", str(best_bid_amount) + "x", best_bid)
      #       #     orders.append(Order(product, best_bid, -best_bid_amount))

      #   # result[product] = orders

      if product == "AMETHYSTS":
        # result[product] = self.oscilation_strategy(state, product, 1000, self.position_limit)

        print(product + ": Buy orders (OrderDepths): " + str(order_depth.buy_orders))
        print(product + ": Sell orders (OrderDepths): " + str(order_depth.sell_orders))

        self.position = int(state.position.get(product, 0))  # sanity check

        best_sell_pr = min(order_depth.sell_orders.keys())
        best_buy_pr = max(order_depth.buy_orders.keys())

        deviation = 3 # Based on Excel
        considered_pos = 0
        threshold_nostd = 0.25
        base = 10
        
        avg = 10000

        if len(order_depth.sell_orders) != 0:
          for price, volume in order_depth.sell_orders.items():
            no_deviations = abs((price - avg) / deviation) if deviation != 0 else 1
            print("price: " + str(price) + ", Distance from mean: " + str(no_deviations) + " std")
          
            if price <= avg - threshold_nostd * deviation:
              max_buy = self.position_limit - self.position
              considered_pos = min(-volume, int(max_buy))
              
              print("Condsidering buying " + str(considered_pos) + "x " + str(price))
              
              orders.append(Order(product, price, considered_pos))
              self.position += considered_pos

        if len(order_depth.buy_orders) != 0:
          for price, volume in order_depth.buy_orders.items():
            no_deviations = abs((price - avg) / deviation) if deviation != 0 else 1
            print("price: " + str(price) + ", Distance from mean: " + str(no_deviations) + " std")
            
            if price >= avg + threshold_nostd * deviation: 
              max_sell = -self.position_limit - self.position
              considered_pos = max(-volume, int(max_sell))
              
              print("Condsidering selling " + str(considered_pos) + "x " + str(price))
              
              orders.append(Order(product, price, considered_pos))
              self.position += considered_pos

      result[product] = orders
      print("Orders: " + str(orders))
      

    traderData = "SAMPLE"

    conversions = 1
    return result, conversions, traderData
