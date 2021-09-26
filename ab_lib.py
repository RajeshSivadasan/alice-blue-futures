# pylint: disable=unused-wildcard-import
# v1.0 - Baseline
# v1.1 - BotToken Parameterization, enabled import requests
# v1.2.1 - documented iLog function
# v1.3 - getAccessToken(): Implemented hour based generation and change in tokenurltime format to include hour and minute
# v1.4 - Merged Tele() function into iLog() to send telegram messages 
# v1.5 - update_contract_symbol() implemented to update nifty and crude active contract symbol parameter update
# v1.6 - strBotTokenWObot for Telegram bot object 
# v1.7 - Logging of nifty contract symbol update message 
# v1.8 - access token retry functionality added. need testing
# v1.9 - #18-Jun-2021 Disabled Nifty Fut symbol update. Plan to use Nifty 50 index and option trading
# v2.0 - 28-Jun-2021 Enabled Nifty Fut symbol update. Plan to use Nifty fut with option hedging 
# v2.1 - 01-Ju1-2021 getAccessToken() updating wrong .ini file, hence added .ini file parameter  
#       Also updated update_contract_symbol() with the above changes 
#       More exception haldling in getAccessToken()

from alice_blue import *
import configparser
import datetime
import requests
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta, FR
import time

strChatID = <strChatID>
strBotToken = '<strBotToken>'  
strBotTokenWObot = '<strBotTokenWObot>'  # For Telegram bot object. need to revisit this.
supertrend_period = 7 #5 #7 #30 NOte: This changes the ATR period also
supertrend_multiplier = 2.5 #1.5 #3


# Custom logging: Default Info=1, data =0
def iLog(strLogText,LogType=1,sendTeleMsg=False):
    '''0=data, 1=Info, 2-Warning, 3-Error, 4-Abort, 5-Signal(Buy/Sell) ,6-Activity/Task done

        sendTelegramMsg=True - Send Telegram message as well. 
        Do not use special characters like #,& etc  
    '''
    #0- Data format TBD; symbol, price, qty, SL, Tgt, TSL
    
    print("{}|{}|{}".format(datetime.datetime.now(),LogType,strLogText),flush=True)
    
    if sendTeleMsg :
        try:
            requests.get("https://api.telegram.org/"+strBotToken+"/sendMessage?chat_id="+strChatID+"&text="+strLogText)
        except:
            iLog("Telegram message failed."+strLogText)

def getAccessToken(strToken="tokens", INI_FILE="ab.ini"):
    '''Generates and returns new access token in case last generated token is earlier than 6 hours.
    strToken: Section to be used for getting the user details. Default value is tokens '''

    retval = "-1"
    
    iLog("getAccessToken().Reading Config file.")
    # print(str(datetime.datetime.now())+"getAccessToken().Reading Config file.",flush=True)
    #Load parameters from the config file
    cfg = configparser.ConfigParser()
    cfg.read(INI_FILE)

    susername = cfg.get(strToken, "uid")
    spassword = cfg.get(strToken, "pwd")
    sapi_secret = cfg.get(strToken, "api_secret")
    stwoFA = cfg.get(strToken, "twoFA")
    tokenUrlTime = cfg.get(strToken, "tokenUrlTime")
    # today = datetime.datetime.now().strftime("%Y%m%d%H%M")
    
    today = datetime.datetime.now()
    last_token_time = datetime.datetime.strptime(tokenUrlTime,"%Y%m%d%H%M")
    
    # today = datetime.datetime.strptime("202006120200","%Y%m%d%H%M")
    # last_token_time = datetime.datetime.strptime("202006120100","%Y%m%d%H%M")
    
    diff =  today - last_token_time
    
    #if today == tokenUrlTime :
    # Generate new access token only if last generated time is > 6 hours else use existing one
    if (diff.total_seconds() / 3600) < 6:
        #do nothing
        access_token = cfg.get(strToken, "access_token")
        strMsg="Current access token used as last token generated is within last 6 hours"
        # print(strMsg,flush=True)
        iLog(strMsg)
        retval = access_token
    else:
        #Generate access_token
        try:
            # print("spassword=",spassword)
            access_token = AliceBlue.login_and_get_access_token(username=susername, password=spassword, twoFA=stwoFA,  api_secret=sapi_secret)
            # print("access_token try 1=",access_token,flush=True)
            if access_token==None:
                raise Exception("Access token not generated!") 
            else:
                iLog("Access token generated successfully after 1st try.")

        except Exception as ex:
            # print("Exception occured fetching access_token:",ex,flush=True)
            iLog("Exception occured fetching access_token 1st try:"+str(ex),3)
            time.sleep(30)  #wait for 30 seconds and retry
            try:
                access_token = AliceBlue.login_and_get_access_token(username=susername, password=spassword, twoFA=stwoFA,  api_secret=sapi_secret)
                # print("access_token try 2=",access_token,flush=True)
                if access_token==None:
                    raise Exception("Access token not generated!")
                else:
                    iLog("Access token generated successfully after 2nd try.")

            except Exception as ex:
                iLog("Exception occured fetching access_token 2nd try:"+str(ex),3)
                return retval

        # Whatever access token is generated put in the ini file 
        cfg.set(strToken,"access_token",access_token)
        cfg.set(strToken,"tokenUrlTime",datetime.datetime.now().strftime("%Y%m%d%H%M")) 

        with open(INI_FILE, 'w') as configfile:
            cfg.write(configfile)
            configfile.close()
    
        retval = access_token


    return retval

def update_contract_symbol(INI_FILE="ab.ini"):
    '''Updates nifty_symbol(on expiry date which is one day earlier) and crude_symbol in the ab.ini file
        To be called daily before start of market
     '''
    dt_today = datetime.date.today().isoformat()
    # dt_today = datetime.date(2020,7,31).isoformat()

    cfg = configparser.ConfigParser()
    cfg.read(INI_FILE)
    crude_expiry_dates = cfg.get("info", "crude_expiry_dates").split(",")
    update_flag = False

    # For CRUDE
    if dt_today in crude_expiry_dates:
        strMonth = (datetime.datetime.strptime(dt_today,"%Y-%m-%d") + relativedelta(months=1)).strftime("%b").upper()
        iLog("Setting CRUDEOIL contract value in ab.ini to " + "CRUDEOIL " + strMonth + " FUT",6)
        cfg.set("info","crude_symbol","CRUDEOIL " + strMonth + " FUT")
        update_flag = True

    # This will not run if last friday is holiday. Like 25 dec 2020. Need to handle this.
    # For NIFTY
    dt_last_friday =  datetime.datetime.strptime(dt_today,"%Y-%m-%d") + relativedelta(day=31, weekday=FR(-1))
    if datetime.datetime.strptime(dt_today,"%Y-%m-%d") == dt_last_friday:
        strMonth =  (dt_last_friday + relativedelta(days=10)).strftime("%b").upper()
        iLog("Setting NIFTY contract value in ab.ini to " + "NIFTY " + strMonth + " FUT",6)
        cfg.set("info","nifty_symbol","NIFTY " + strMonth + " FUT")
        update_flag = True
    
    #18-Jun-2021 Disabled Nifty Fut symbol update. Plan to use Nifty 50 index and option trading
    #28-Jun-2021 Enabled Nifty Fut symbol update. Plan to use Nifty fut with option hedging 
    if update_flag :
        with open(INI_FILE, 'w') as configfile:
            cfg.write(configfile)
            configfile.close()
        iLog("Updated CRUDEOIL/NIFTY contract month in ab.ini",6)

#################################
##     INDICATORS
#################################
# Source for tech indicator : https://github.com/arkochhar/Technical-Indicators/blob/master/indicator/indicators.py
def EMA(df, base, target, period, alpha=False):
    """
    Function to compute Exponential Moving Average (EMA)
    Args :
        df : Pandas DataFrame which contains ['date', 'open', 'high', 'low', 'close', 'volume'] columns
        base : String indicating the column name from which the EMA needs to be computed from
        target : String indicates the column name to which the computed data needs to be stored
        period : Integer indicates the period of computation in terms of number of candles
        alpha : Boolean if True indicates to use the formula for computing EMA using alpha (default is False)
    Returns :
        df : Pandas DataFrame with new column added with name 'target'
    """

    con = pd.concat([df[:period][base].rolling(window=period).mean(), df[period:][base]])

    if (alpha == True):
        # (1 - alpha) * previous_val + alpha * current_val where alpha = 1 / period
        df[target] = round(con.ewm(alpha=1 / period, adjust=False).mean(),1) #Rajesh - added round function
    else:
        # ((current_val - previous_val) * coeff) + previous_val where coeff = 2 / (period + 1)
        df[target] = round(con.ewm(span=period, adjust=False).mean(),1) #Rajesh - added round function

    df[target].fillna(0, inplace=True)
    return df

def ATR(df, period, ohlc=['open', 'high', 'low', 'close']):
    """
    Function to compute Average True Range (ATR)
    Args :
        df : Pandas DataFrame which contains ['date', 'open', 'high', 'low', 'close', 'volume'] columns
        period : Integer indicates the period of computation in terms of number of candles
        ohlc: List defining OHLC Column names (default ['Open', 'High', 'Low', 'Close'])
    Returns :
        df : Pandas DataFrame with new columns added for
            True Range (TR)
            ATR (ATR_$period)
    """
    #atr = 'ATR_' + str(period)
    atr = 'ATR'
    # Compute true range only if it is not computed and stored earlier in the df
    #if not 'TR' in df.columns:
    df['h-l'] = df[ohlc[1]] - df[ohlc[2]]
    df['h-yc'] = abs(df[ohlc[1]] - df[ohlc[3]].shift())
    df['l-yc'] = abs(df[ohlc[2]] - df[ohlc[3]].shift())

    #Rajesh - Updated round function below
    df['TR'] = round(df[['h-l', 'h-yc', 'l-yc']].max(axis=1),1)

    df.drop(['h-l', 'h-yc', 'l-yc'], inplace=True, axis=1)

    # Compute EMA of true range using ATR formula after ignoring first row
    EMA(df, 'TR', atr, period, alpha=True)

    return df

def SuperTrend(df, period = supertrend_period, multiplier=supertrend_multiplier, ohlc=['open', 'high', 'low', 'close']):
    """
    Function to compute SuperTrend
    Args :
        df : Pandas DataFrame which contains ['date', 'open', 'high', 'low', 'close', 'volume'] columns
        period : Integer indicates the period of computation in terms of number of candles
        multiplier : Integer indicates value to multiply the ATR
        ohlc: List defining OHLC Column names (default ['Open', 'High', 'Low', 'Close'])
    Returns :
        df : Pandas DataFrame with new columns added for
            True Range (TR), ATR (ATR_$period)
            SuperTrend (ST_$period_$multiplier)
            SuperTrend Direction (STX_$period_$multiplier)
    """

    ATR(df, period, ohlc=ohlc)
    atr = 'ATR' #+ str(period)
    st = 'ST' #+ str(period) + '_' + str(multiplier)
    stx = 'STX' #  + str(period) + '_' + str(multiplier)

    """
    SuperTrend Algorithm :
        BASIC UPPERBAND = (HIGH + LOW) / 2 + Multiplier * ATR
        BASIC LOWERBAND = (HIGH + LOW) / 2 - Multiplier * ATR
        FINAL UPPERBAND = IF( (Current BASICUPPERBAND < Previous FINAL UPPERBAND) or (Previous Close > Previous FINAL UPPERBAND))
                            THEN (Current BASIC UPPERBAND) ELSE Previous FINALUPPERBAND)
        FINAL LOWERBAND = IF( (Current BASIC LOWERBAND > Previous FINAL LOWERBAND) or (Previous Close < Previous FINAL LOWERBAND)) 
                            THEN (Current BASIC LOWERBAND) ELSE Previous FINAL LOWERBAND)
        SUPERTREND = IF((Previous SUPERTREND = Previous FINAL UPPERBAND) and (Current Close <= Current FINAL UPPERBAND)) THEN
                        Current FINAL UPPERBAND
                    ELSE
                        IF((Previous SUPERTREND = Previous FINAL UPPERBAND) and (Current Close > Current FINAL UPPERBAND)) THEN
                            Current FINAL LOWERBAND
                        ELSE
                            IF((Previous SUPERTREND = Previous FINAL LOWERBAND) and (Current Close >= Current FINAL LOWERBAND)) THEN
                                Current FINAL LOWERBAND
                            ELSE
                                IF((Previous SUPERTREND = Previous FINAL LOWERBAND) and (Current Close < Current FINAL LOWERBAND)) THEN
                                    Current FINAL UPPERBAND
    """

    # Compute basic upper and lower bands
    df['basic_ub'] = (df[ohlc[1]] + df[ohlc[2]]) / 2 + multiplier * df[atr]
    df['basic_lb'] = (df[ohlc[1]] + df[ohlc[2]]) / 2 - multiplier * df[atr]

    # Compute final upper and lower bands
    df['final_ub'] = 0.00
    df['final_lb'] = 0.00
    for i in range(period, len(df)):
        df['final_ub'].iat[i] = df['basic_ub'].iat[i] if df['basic_ub'].iat[i] < df['final_ub'].iat[i - 1] or \
                                                         df[ohlc[3]].iat[i - 1] > df['final_ub'].iat[i - 1] else \
        df['final_ub'].iat[i - 1]
        df['final_lb'].iat[i] = df['basic_lb'].iat[i] if df['basic_lb'].iat[i] > df['final_lb'].iat[i - 1] or \
                                                         df[ohlc[3]].iat[i - 1] < df['final_lb'].iat[i - 1] else \
        df['final_lb'].iat[i - 1]

    # Set the Supertrend value
    df[st] = 0.00
    for i in range(period, len(df)):
        df[st].iat[i] = df['final_ub'].iat[i] if df[st].iat[i - 1] == df['final_ub'].iat[i - 1] and df[ohlc[3]].iat[
            i] <= df['final_ub'].iat[i] else \
            df['final_lb'].iat[i] if df[st].iat[i - 1] == df['final_ub'].iat[i - 1] and df[ohlc[3]].iat[i] > \
                                     df['final_ub'].iat[i] else \
                df['final_lb'].iat[i] if df[st].iat[i - 1] == df['final_lb'].iat[i - 1] and df[ohlc[3]].iat[i] >= \
                                         df['final_lb'].iat[i] else \
                    df['final_ub'].iat[i] if df[st].iat[i - 1] == df['final_lb'].iat[i - 1] and df[ohlc[3]].iat[i] < \
                                             df['final_lb'].iat[i] else 0.00

        # Mark the trend direction up/down
    df[stx] = np.where((df[st] > 0.00), np.where((df[ohlc[3]] < df[st]), 'down', 'up'), np.NaN)

    # Remove basic and final bands from the columns
    df.drop(['basic_ub', 'basic_lb', 'final_ub', 'final_lb'], inplace=True, axis=1)

    df.fillna(0, inplace=True)
    return df

def RSI(df, base="close", period=7):
    """
    Function to compute Relative Strength Index (RSI)
    
    Args :
        df : Pandas DataFrame which contains ['date', 'open', 'high', 'low', 'close', 'volume'] columns
        base : String indicating the column name from which the MACD needs to be computed from (Default Close)
        period : Integer indicates the period of computation in terms of number of candles
        
    Returns :
        df : Pandas DataFrame with new columns added for 
            Relative Strength Index (RSI_$period)
    """
 
    delta = df[base].diff()
    up, down = delta.copy(), delta.copy()

    up[up < 0] = 0
    down[down > 0] = 0
    
    rUp = up.ewm(com=period - 1,  adjust=False).mean()
    rDown = down.ewm(com=period - 1, adjust=False).mean().abs()

    # df['RSI_' + str(period)] = round(100 - 100 / (1 + rUp / rDown))
    # df['RSI_' + str(period)].fillna(0, inplace=True)
    df['RSI'] = round(100 - 100 / (1 + rUp / rDown))
    df['RSI'].fillna(0, inplace=True)
    
    return df