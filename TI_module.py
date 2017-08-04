def TI_price(type, S, K, P, Ch):
    if type == "call":
        price = (S - K)/(P * Ch)
    elif type == "put":
        price = (K - S)/(P * Ch)
    return price

def TI_strike(type, S, price, P, Ch):
    if type == "call":
        K = -1 * price * (P * Ch) + S
    elif type == "put":
        K = price * (P * Ch) + S
    return K

def TI_underlying_price(type, K, price, P, Ch):
    if type == "call":
        S = K + price * (P * Ch)
    elif type == "put":
        S = K - price * (P * Ch)
    return S
