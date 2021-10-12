from  binance.client import Client
import numpy as np
import time
import get_data as gd
import notifications
import vp_strtg


tickers = ["FILUSDT","SOLUSDT","ONEUSDT","TFUELUSDT","ATOMUSDT","OMGUSDT","FETUSDT","CELRUSDT","ERNUSDT","ETCUSDT","PERLUSDT","ADAUSDT","EPSUSDT","XRPUSDT","SLPUSDT","MBOXUSDT","LINKUSDT","AVAUSDT","KAVAUSDT"]
ticker = "FILUSDT"

print(notifications.sendMessage("Start Application 🎉🎉🎉🎉"))
pdsTOCalculated = [48,199,484]
#pds = 48
def calculate_SMA(ser, pds):

    sma = ser.rolling(window=pds).mean()
    return sma

def calculate_Zscore(pds,df):

    df['mean'] = ((df['Close']*df['Volume']).rolling(pds).sum())/df['Volume'].rolling(pds).sum()
    #mean = sum(volume * close, pds) / sum(volume, pds)
    df['vwapsd'] = np.sqrt(calculate_SMA(pow(df['Close'] - df['mean'], 2), pds))
    #df['z-scoor'] = (df['Close'] - df['mean']) / df['vwapsd']
    return (df['Close'] - df['mean']) / df['vwapsd']




def startTrackingCrypto():
    for pds in pdsTOCalculated:
        for ticker  in tickers:
            df = gd.get_klines(ticker, Client.KLINE_INTERVAL_5MINUTE, "84 hours ago UTC")
            touchGreenLine(pds,df,ticker=ticker)


tickerToBuy = []

def isTickerBuySend(tickerToAdd):
    for ticker in tickerToBuy:
        if ticker == tickerToAdd:
            return True
        else:
            return False

def addTickerToBuyList(tickerToAdd):
    tickerToBuy.append(tickerToAdd)

def removeTicker(ticker):
    for tk in tickerToBuy:
        if tk == ticker:
            tickerToBuy.remove(tk)

def touchGreenLine(pds,df,ticker):
    result = calculate_Zscore(pds,df)
    score = float(result.tail(1).values)
    message = ""
    close = df["Close"][-1]
    isTimeToBuy = isTickerBuySend(ticker)
    pocValue = vp_strtg.getPoc(ticker=ticker)
    if score <= -2.5 and close< pocValue and not isTimeToBuy:
        message = f"Chri {ticker}, {round(score,2)} bhad taman  {close} o bi3o  mli iwsal: {pocValue}"
        addTickerToBuyList(ticker) 
    elif score < -4 and close < pocValue:
        message= f"Chri 3ad {ticker} ila kayn 💰💰 {round(score,2)}...!"
    elif score > 2.5 and not isTimeToBuy:
         message =f"ila 3adndk  {ticker}  {round(score,2)}, bi3o rah wsal: {close} 💰💰💰 "
         addTickerToBuyList(ticker) 
    elif score > 4:
        message =f"Ila ba9i 3andk  {ticker} bi3o daba {round(score,2)}, {close}"
    elif score >-2.5 and score < 2.5:
        message = f"tracking {ticker} pds {pds}, realtime price is: {close} and point of control is: {pocValue} ======> {round(score,2)}"
        removeTicker(ticker)
    else:
        message = f"tracking {ticker} pds {pds}, realtime price is: {close} and point of control is: {pocValue} ======> {round(score,2)}"


    if "tracking" not in  message: 
        print(notifications.sendMessage(message=message))
    else:
        print(message)
        
while True:
    print("Time: %s" % time.ctime())
    startTrackingCrypto()
    time.sleep(10)

# print("vwapScore : "),
# df  =  pd.DataFrame(result)
# df= df.sort_values(by=['Date'],ascending=False)
#sprint(df)






