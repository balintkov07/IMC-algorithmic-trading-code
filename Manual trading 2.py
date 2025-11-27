import numpy as np

commodities = {0: "Pizza", 1: "Wasabi", 2: "Snowball", 3: "To_Shells"}
data = [
    [1, 0.48, 1.52, 0.71],
    [2.05, 1, 3.26, 1.56],
    [0.64, 0.3, 1, 0.46],
    [1.41, 0.61, 2.08, 1]
]

matrix = np.array(data)

def two_trades(matrix):
  trades = []
  value = 0
  for i in range(3):
      first_trade = commodities[i]
      mult1 = matrix[3][i]

      for j in range(3):
        if j != i:
            val_new = mult1 * matrix[i][j] * matrix[j][3]
            if val_new > value:
              trades = [first_trade, commodities[j], commodities[3]]
              value = val_new

  return value, trades



# Function for three trades
def three_trades(matrix):
    trades = []
    value = 0
    for i in range(3):
        first_trade = commodities[i]
        mult1 = matrix[3][i]

        for j in range(3):
            if j != i:
                mult2 = matrix[i][j]

                for k in range(3):
                    if k != j:
                        val_new = mult1 * mult2 * matrix[j][k] * matrix[k][3]
                        if val_new > value:
                            trades = [first_trade, commodities[j], commodities[k], commodities[3]]
                            value = val_new
    return value, trades

# Function for four trades
def four_trades(matrix):
    trades = []
    value = 0
    for i in range(3):
        first_trade = commodities[i]
        mult1 = matrix[3][i]

        for j in range(3):
            if j != i:
                mult2 = matrix[i][j]

                for k in range(3):
                    if k != j:
                        mult3 = matrix[j][k]

                        for l in range(3):
                            if l != k:
                                val_new = mult1 * mult2 * mult3 * matrix[k][l] * matrix[l][3]
                                if val_new > value:
                                    trades = [first_trade, commodities[j], commodities[k], commodities[l], commodities[3]]
                                    value = val_new
    return value, trades

def five_trades(matrix):
    trades = []
    value = 0
    for i in range(3):
        first_trade = commodities[i]
        mult1 = matrix[3][i]

        for j in range(3):
            if j != i:
                mult2 = matrix[i][j]

                for k in range(3):
                    if k != j:
                        mult3 = matrix[j][k]

                        for l in range(3):
                            if l != k:
                              mult4 = matrix[k][l]

                              for z in range(3):
                                if z != l:
                                  val_new = mult1 * mult2 * mult3 * mult4 *matrix[l][z]*matrix[z][3]
                                  if val_new > value:
                                    trades = [first_trade, commodities[j], commodities[k], commodities[l],commodities[z], commodities[3]]
                                    value = val_new

    return value, trades


max_val_2, path_2 = two_trades(matrix)
print("Max value for two trades:", max_val_2)
print("Trade path for two trades:", path_2)
# Calculate for three trades
max_val_3, path_3 = three_trades(matrix)
print("Max value for three trades:", max_val_3)
print("Trade path for three trades:", path_3)

# Calculate for four trades
max_val_4, path_4 = four_trades(matrix)
print("Max value for four trades:", max_val_4)
print("Trade path for four trades:", path_4)

# Calculate for four trades
max_val_5, path_5 = five_trades(matrix)
print("Max value for four trades:", max_val_5)
print("Trade path for four trades:", path_5)

# calculate total gain
gain = 2000000*(max_val_5 - 1)
print("Total gain: " + str(gain) +" Shells")
  
    

  
  
  