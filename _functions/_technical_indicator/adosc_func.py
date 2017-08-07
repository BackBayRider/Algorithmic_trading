# -*- coding: utf-8 -*-
import numpy as np
from talib import ADOSC, EMA, SMA

#Deux façon de calculer : à la façon de talib avec EMA. A la façon de bloomberg avec SMA. Talib > bloomberg dans la litérature.
#Du coup 3 façon de l'implémenter:
#   - avec le package Ta-Lib. (avec EMA sur ADL).
#   - avec la formule fournie par ChartSchool (avec EMA sur ADL).
#   - avec la formule fournie par la notice technique Bloomberg (avec SMA sur ADL).
#La function ta-lib admet des np.array (donc .values sur colonne de dataframe).
#Les autres admettent des pandas dataFrames.


def adosc_talib(my_close, my_high, my_low, my_volume, fastperiod, slowperiod):

    x = ADOSC(my_high.values, my_low.values, my_close.values, my_volume.values, fastperiod = fastperiod, slowperiod = slowperiod)
    return x


def adosc_chartschool(my_close, my_high, my_low, my_volume, fastperiod, slowperiod):

    MFV = (((my_close - my_low)-(my_high - my_close)) / (my_high - my_low)) * my_volume
    ADL = np.cumsum(MFV)
    ADOSC = EMA(ADL.values, timeperiod=fastperiod) - EMA(ADL.values, timeperiod=slowperiod)
    return ADOSC


def adosc_bloomberg(my_close, my_high, my_low, my_volume, fastperiod, slowperiod):

    MFV = (((my_close - my_low)-(my_high - my_close)) / (my_high - my_low)) * my_volume
    ADL = np.cumsum(MFV)
    ADOSC = SMA(ADL.values, timeperiod=fastperiod) - SMA(ADL.values, timeperiod=slowperiod)

    return ADOSC
