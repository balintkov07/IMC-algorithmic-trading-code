#TradingState will contain a per product overview of all the outstanding buy and sell orders (also called “quotes”) originating from the bots. Based on the logic in the run method the algorithm can then decide to either send orders that will fully or partially match with the existing orders

from datamodel import OrderDepth, UserId, TradingState, Order

class Trader:

  #Volume weighted average price
  #state: Trading state = 'state' parameter given in the argument should be of 'TradingState' class (nonbinding hint)
  # Dict[str, int] = it specifies the expected return type of the method (nonbinding hint)
  #Output = dictionary, label-price, value-int that descirbes volume
  def vwap_condensation(self, state: TradingState) -> Dict[str, int]:
    # Merging the buy and sell orders into one dictionary
    # We assume that we get an uncrossed book
    orders = state.order_depths()
    result = {} # A dictionary that stores the positions open for a specific price level
    
    for price in orders.buy_orders.keys():
      result[price] = orders.buy_orders[price] - orders.sell_orders[price]

    print(result)
    return result
    
      
  def run(self, state: TradingState):

class TradingState:
  
  def __init__(self,
     traderData: str,
     timestamp: Time,
     listings: Dict[Symbol, Listing],
     order_depths: Dict[Symbol, OrderDepth],
     own_trades: Dict[Symbol, List[Trade]],
     market_trades: Dict[Symbol, List[Trade]],
     position: Dict[Product, Position],
     observations: Observation):
  self.traderData = traderData
  self.timestamp = timestamp
  self.listings = listings
  self.order_depths = order_depths
  self.own_trades = own_trades
  self.market_trades = market_trades #dictionary, label = symbol, value = list of trades
  self.position = position
  self.observations = observations
    