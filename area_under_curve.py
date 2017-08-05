#!/usr/bin/env python
# -*- coding: utf-8 -*-
from scipy.integrate import simps
import numpy as np
import pandas as pd
import talib as ta
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema
import os
from pykalman import KalmanFilter
import quandl as qd

qd.ApiConfig.api_key = "iPyQWysSc6cfaVsqegWa"

def kalman_serie(mySerie):

    init_stat_mean = mySerie[0]

    kf = KalmanFilter(transition_matrices=[1],
                      observation_matrices=[1],
                      initial_state_mean=init_stat_mean,
                      initial_state_covariance=1,
                      observation_covariance=1,
                      transition_covariance=.01)

    # Use the observed values of the price to get a rolling mean
    state_means, _ = kf.filter(mySerie)
    state_means = pd.Series(state_means.flatten())
    return state_means


def elder_ray(myMM, myHigh, myLow):

    bear_power = []
    bull_power = []
    x = 0

    while x < len(myMM):
        bear_diff = myHigh[x] - myMM[x]
        bull_diff = myLow[x] - myMM[x]
        bear_power.append(bear_diff)
        bull_power.append(bull_diff)

        x += 1

    return bear_power, bull_power


def patternRecognition(open, high, low, close):

    tempx = [0] * len(close)
    for name in dir(ta):
        if name.startswith("CDL"):
            might_be_function = getattr(ta, name)
            if callable(might_be_function):
                tesstx = might_be_function(open, high, low, close)
                tempx = [x + y for x, y in zip(tempx, tesstx)]

    return tempx


def stats_sliced_range(type, my_data, start_index, n, delay=0):

    if type == "backward":
        my_data = my_data[(start_index - n - delay):(start_index - delay)]
    elif type == "forward":
        my_data = my_data[(start_index + delay + 1):(start_index + n + delay + 1)]

    maximum = max(my_data)
    minimum = min(my_data)


    moyenne = np.mean(my_data)
    variance = np.var(my_data)
    ecart_type = np.sqrt(variance)

    return maximum, minimum, moyenne, variance, ecart_type


def crosszeroline_analysis(type_signal, my_y):
    """
    Serie d'indice juste après croisement de zero

    """
    i = len(my_y) - 1
    cross_zero_line = []

    if type_signal == "PUT":
        while i > 0:
            if y[i] < 0 < y[i-1]:
                cross_zero_line.append(i)
            i -= 1

    if type_signal == "CALL":
        while i > 0:
            if y[i] > 0 > y[i-1]:
                cross_zero_line.append(i)
            i -= 1

    return cross_zero_line


def divergence_analysis(type_signal, my_y, my_serie):
    """
    A faire avec adosc 3 10
    Retourne 3 arrays, un contenant les premiers points, un autre les derniers, et un troisième la divergence :
    3 conditions sont respectées :
    - Cette droite ne doit être coupée par aucun éléments.
    - Les deux sommets doivent appartenir à la même zone (positive ou négative).
    - La série a donc le droit de s'aventurer en territoire opposé au territoire d'appartenance de ses deux sommets.

    my_y : série de l'indicateur
    my_serie : série du cours
    z : indice du premier sommet formant le couple (le plus ancien)
    i : indice du second sommet formant le couple (le plus récent)
    """
    first_point = []
    last_point = []
    divergence = []
    a = 0
    b = 0
    if type_signal == "PUT":
        max_index = argrelextrema(my_y, np.greater)
        max_index = list(max_index[0])

        i = len(max_index) - 1
        while i > 0:
            for z in range(i):
                if z != i:

                    a = float(my_y[max_index[i]] - my_y[max_index[z]]) / float(max_index[i] - max_index[z])
                    b = float(my_y[max_index[i]]) - a * float(max_index[i])

                    for u in range(max_index[z] + 1, max_index[i], 1):
                        test_y = a * u + b

                        if test_y < my_y[u] or a > 0 or my_y[max_index[i]] < 0 or my_y[max_index[i]] < 0:
                            s = False
                            break
                        else:
                            s = True

                    a_c = float(my_serie[max_index[i]] - my_serie[max_index[z]]) / float(max_index[i] - max_index[z])

                    if a < 0 < a_c:
                        reponse = 1
                    else:
                        reponse = 0

                if s == True:
                    #print "Coordonnées: (%s, %s) - Divergence Ind.: %s" % (max_index[i], max_index[z], reponse)
                    first_point.append(max_index[z])
                    last_point.append(max_index[i])
                    divergence.append(reponse)
            i -= 1

    if type_signal == "CALL":
        min_index = argrelextrema(my_y, np.less)
        min_index = list(min_index[0])

        i = len(min_index) - 1
        while i > 0:
            for z in range(i):
                if z != i:

                    a = float(my_y[min_index[i]] - my_y[min_index[z]]) / float(min_index[i] - min_index[z])
                    b = float(my_y[min_index[i]]) - a * float(min_index[i])

                    for u in range(min_index[z] + 1, min_index[i], 1):
                        test_y = a * u + b

                        if test_y > my_y[u] or a < 0 or my_y[min_index[i]] > 0 or my_y[min_index[i]] > 0:
                            s = False
                            break
                        else:
                            s = True

                    a_c = float(my_serie[min_index[i]] - my_serie[min_index[z]]) / float(min_index[i] - min_index[z])

                    if a > 0 > a_c:
                        reponse = 1
                    else:
                        reponse = 0

                if s == True:
                    #print "Coordonnées: (%s, %s) - Divergence Ind.: %s" % (min_index[i], min_index[z], reponse)
                    first_point.append(min_index[z])
                    last_point.append(min_index[i])
                    divergence.append(reponse)
            i -= 1

    return first_point, last_point, divergence, a, b


def multi_summit_analysis(first_point, last_point):
    source = []
    cible = []

    for elem_source in first_point:
        count = 0
        for x in first_point:
            if elem_source == x:
                count += 1
        source.append(count)

    for elem_cible in last_point:
        count = 0
        for x in last_point:
            if elem_cible == x:
                count +=1
        cible.append(count)
    print first_point
    print source
    print "interpretation: elem a été n fois la source de n points"
    print last_point
    print cible
    print "interpretation: elem a n source"
    return source, cible


def main_action(my_y, my_serie, my_high, my_low, my_open, my_rsi):

    v1_put, v2_put, v3_put, v4_put, v5_put = divergence_analysis("PUT", my_y, my_serie)
    v1_call, v2_call, v3_call, v4_call, v5_call = divergence_analysis("CALL", my_y, my_serie)
    patternRes = patternRecognition(my_open, my_high, my_low, my_serie)

    for day in [1,2,3,4,5,6,7,8,9,10]:
        return10j_put_good = []
        return10j_put_bad = []
        return10j_put_good_c = []
        return10j_put_bad_c = []

        # RETURN PUT 10J ALL

        for elem in v2_put:
            return10j_good = (my_serie[elem+1] / stats_sliced_range("forward", my_low, elem, day, 1)[1])-1
            return10j_put_good.append(return10j_good)
            return10j_bad = (my_serie[elem+1] / stats_sliced_range("forward", my_high, elem, day, 1)[0])-1
            return10j_put_bad.append(return10j_bad)

        for elem in v2_call:
            return10j_good_c = (stats_sliced_range("forward", my_high, elem, day, 1)[0] / my_serie[elem+1])-1
            return10j_put_good_c.append(return10j_good_c)
            return10j_bad_c = (stats_sliced_range("forward", my_low, elem, day, 1)[1] / my_serie[elem+1])-1
            return10j_put_bad_c.append(return10j_bad_c)

        print v2_put
        print return10j_put_good
        print return10j_put_bad
        print "PUT: Mean - Good situation (Lowest price %s day after): %.4f" %(day, np.mean(return10j_put_good))
        print "PUT: Mean - Bad situation (Highest price %s day after): %.4f" % (day, np.mean(return10j_put_bad))
        print len(return10j_put_good)

        print "CALL: Mean - Good situation (Highest price %s day after): %.4f" % (day, np.mean(return10j_put_good_c))
        print "CALL: Mean - Bad situation (Lowest price %s day after): %.4f" % (day, np.mean(return10j_put_bad_c))
        print len(return10j_put_good_c)
        print "/////////////////////"
    return "non"

list_cac40 = ["EURONEXT/AC","EURONEXT/AIR","EURONEXT/AI","EURONEXT/MT","EURONEXT/ATO","EURONEXT/CS","EURONEXT/BNP","EURONEXT/EN","EURONEXT/CAP","EURONEXT/CA","EURONEXT/ACA","EURONEXT/BN","EURONEXT/EI","EURONEXT/KER","EURONEXT/OR","EURONEXT/LR","EURONEXT/MC","EURONEXT/ML","EURONEXT/NOKIA","EURONEXT/RI","EURONEXT/UG","EURONEXT/PUB","EURONEXT/RNO","EURONEXT/SAF","EURONEXT/SGO","EURONEXT/SAN","EURONEXT/SU","EURONEXT/GLE","EURONEXT/SW","EURONEXT/SOLB","EURONEXT/TEC","EURONEXT/FP","EURONEXT/UL","EURONEXT/FR","EURONEXT/VIE","EURONEXT/DG","EURONEXT/VIV","EURONEXT/LHN","EURONEXT/ENGI","EURONEXT/FR"]

for stock in list_cac40:

    data = qd.get(stock)

    dates = data.index
    close_price = data["Last"].values
    open_price = data["Open"].values
    high_price = data["High"].values
    low_price = data["Low"].values
    volume = data["Volume"].values
    adosc310 = ta.ADOSC(high_price, low_price, close_price, volume, fastperiod = 3, slowperiod = 10)
    adosc620 = ta.ADOSC(high_price, low_price, close_price, volume, fastperiod = 6, slowperiod = 20)
    rsi = ta.RSI(close_price)

    print "********** %s - %s ***********" %(stock, dates[len(dates)-1])
    print len(close_price)
    main_action(adosc310, close_price, high_price, low_price, open_price, rsi)


#for file in os.listdir("./datas/"):
#    if file.endswith("PUB.PA.csv"):
#        my_path = os.path.join("./datas/", file)
#        csv = np.genfromtxt(my_path, delimiter=",")
#        y = csv[:,7]
#        cours = csv[:, 5]
#        myMin = csv[:, 3]
#        myMax = csv[:, 2]
#        myOpen = csv[:,1]
#        rsi = csv[:, 9]
#        print my_path
#        main_action(y,cours,myMax,myMin, myOpen, rsi)




        #break

   # print np.percentile(return10j_put_good, 25)

   # n, bins, patches = plt.hist(return10j_put_bad, 30, normed=1, facecolor='green', alpha=0.75)
   # plt.show()