import numpy as np
from talib import ADOSC

#Incertitude quant à la façon de calculer l'indicateur. Impossible de retrouver la même série. A voir.
#Du coup 3 façon de l'implémenter:
#   - avec le package Ta-Lib.
#   - avec la formule fournie par ChartSchool (avec EMA sur ADL).
#   - avec la formule fournie par la notice technique Bloomberg (avec SMA sur ADL).
#Les functions suivantes admettent des np.array (donc .values sur colonne de dataframe).

def adosc_talib(my_close, my_high, my_low, my_volume, fastperiod, slowperiod):
  x = ADOSC(high_price, low_price, close_price, volume, fastperiod = fastoeriod, slowperiod = slowperiod)
  return x

def adosc_chartschool(my_close, my_high, my_low, my_volume, fastperiod, slowperiod):
  
  return x
