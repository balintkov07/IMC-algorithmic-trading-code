from datamodel import OrderDepth, UserId, TradingState, Order, ConversionObservation
from typing import List
import string
import numpy as np

class Trader:

    def __init__(self):
      self.position = 0
      self.position_limit = 100
      self.time_to_buy = False
      self.prices_storer = []

    def sunlight_impact (self,current_sunlight):
      if current_sunlight < 2520:
        change_sunlight = ((2520 - current_sunlight) / 60)
        decrease_sunlight = (1 - 0.04) ** change_sunlight
        return 1 - decrease_sunlight
      else:
        return 0

    def humidity_impact (self, current_humidity):
      if current_humidity < 60:
        change_humidity = ((60 - current_humidity) / 5)
        decrease_humidity = (1 - 0.02) ** change_humidity
        return 1 - decrease_humidity
      elif current_humidity > 80:
        change_humidity = ((current_humidity - 80) / 5)
        decrease_humidity = (1 - 0.02) ** change_humidity
        return 1 - decrease_humidity
      else:
        return 0

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

    def costs (self, transport_fees, export_fees, import_fees):
      buy_costs = transport_fees + import_fees
      sell_costs = transport_fees + export_fees

      return buy_costs, sell_costs

      
    
    def run(self, state: TradingState):
      # Only method required. It takes all buy and sell orders for all symbols as an input, and outputs a list of orders to be sent
      print("traderData: " + state.traderData)
      print("Observations: " + str(state.observations))
      print(vars(state))

      result = {}
      for product in state.order_depths:
        if product == "ORCHIDS":
          order_depth: OrderDepth = state.order_depths[product]
          orders: List[Order] = []

            # sourcing and transforming the values:
          
          current_humidity = state.observations.conversionObservations[product].humidity
          current_sunlight = state.observations.conversionObservations[product].sunlight
          transport_fees = state.observations.conversionObservations[product].transportFees
          export_fees = state.observations.conversionObservations[product].exportTariff
          import_fees = state.observations.conversionObservations[product].importTariff

          if (current_humidity < 60 or current_humidity > 80) and current_sunlight < 2520:
            self.time_to_buy = True 
          else:
            self.time_to_buy = False
          
          best_sell_pr = min(order_depth.sell_orders.keys())
          best_buy_pr = max(order_depth.buy_orders.keys())

          self.prices_storer.append((best_sell_pr + best_buy_pr) / 2)
          # Store the average of the best sell and best buy prices
          # Idea: store the values from previous trades from TradingState -> market_trades

          deviation = np.std(self.prices_storer)
          ema = self.calculate_ema(self.prices_storer, 100, 0)

          #unpack trading_costs 
          buy_costs, sell_costs = self.costs(transport_fees, export_fees, import_fees)
          

          if len(order_depth.sell_orders) != 0:
            for price, volume in order_depth.sell_orders.items():
              if (price + buy_costs <= ema[-1] - deviation) or self.time_to_buy:
                max_buy = self.position_limit - self.position
                orders.append(Order(product, price, min(-volume, max_buy)))
                self.position += min(-volume, max_buy)

          if len(order_depth.buy_orders) != 0:
            for price, volume in order_depth.buy_orders.items():
              if price - sell_costs >= ema[-1] + deviation:
                max_sell = -self.position_limit - self.position
                orders.append(Order(product, price, max(-volume, max_sell)))
                self.position += max(-volume, max_sell)
                  
      
          result[product] = orders
        else:
          result[product] = []

      
            # determining optimal sell / buy moment     
            # determining relative max / minimum 
            # Regression output: Sunlingt = -2702.019724 + 67.28507569*Humidity
            # both coefficients are statistically significant !!!
            # => They are positively associatied (they move in tandem), so we can
            # => create a "feature" that measure their combined intensivity 
            # +> compute some relative threshold after which it is optimal to sell/buy
          
      traderData = "SAMPLE" 

      conversions = 1
      return result, conversions, traderData