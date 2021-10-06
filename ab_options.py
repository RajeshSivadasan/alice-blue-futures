# pylint: disable=unused-wildcard-import
# Refer to ab.py verison comments for previous changes
#============= ab_options.py created from here ============= 
# Used v6.9.2 as the base to start the options 
# v6.9.2 Implemented try block in subscribe_ins()
# v7.0  Revamp of the program for Options Trading (Nifty/BankNifty)
#   Replace Nifty futures with Nifty 50 Index. Use it for option trading
#   First phase we will implement NIfty then Banknifty
#v7.0.1 Fixed expiry date holiday issue
#v7.0.2 Fixed buy_signal():Optional parameter price not of type float
#v7.0.3 Removed RSI range and momentum check, print change 
#v7.0.4 fixed ins_nifty_opt incorrect token assignment
#v7.0.5 fixed issue with strMsg assignment in buy_nifty_options()
#v7.0.6 fixed indentation of program exit code at 3.30 pm
#v7.0.7 reworked for MIS support. Removed unwanted code 
#v7.1.0 Added banknifty support 
#v7.1.4 Banknifty support updates, order management, threading
#v7.1.5 check_orders() for order management. can implement trailing SL concept as well.
#v7.1.6-7 buy_nifty_options() MIS SL order
#v7.1.8-9 Fixed place_sl_order main_order_id bug, added debug comments
#v7.2.0 Fixed place_sl_order bug - Trading Symbol Doesn't exist for the exchange
#v7.2.1 check_orders() - TSL update and comments, logging

###### STRATEGY / TRADE PLAN #####
# Trading Style : Intraday
# Trade Timing : Morning 9:15 to 10:40 AM , After noon 1.30 PM to 3.30 PM 
# Trading Capital : Rs 20,000
# Trading Qty : 1 Lot for short goal, 1 lot long goal
# Premarket Routine : TBD
# Trading Goals : Nifty(Short Goal = 20 Points, Long Goal = 200 pts with TSL)
# Time Frame : 3 min
# Entry Criteria : Nifty50 Supertrend buy(CE)/Sell(PE)
# Exit Criteria : BO Set for Target/SL, Exit CE position on Supertrend Sell/PE trigger, exit PE position the other way  
# Risk Capacity : Taken care by BO
# Order Management : BO orders else MIS/Normal(may need additional exit criteria)

# Supertrend Buy signal will trigger ATM CE buy
# Supertrend Sell signal will trigger ATM PE buy 
# Existing positions to be closed before order trigger
# For option price, ATM ltp CE and ATM ltp PE to be subscribed dynamically and stored in global variables
# Nifty option order trigger to be based on Nifty50 Index movement hence nifty50 dataframe required 
# BankNifty option order trigger to be based on BankNifty Index movement hence banknifty dataframe required to be maintained seperately

# bg process
# 2020-09-01 09:59:18.152555|1|chat_id=670221062 text=Cmd ls
# exception= list index out of range
# 2020-09-01 10:00:18.565516|1|chat_id= text=Cmd ls
# exception= list index out of range

# Open issues/tasks:
# Check use of float in buy_signal() as it is working in ab.py without it
# Instead of check_trade_time_zone() plan for no_trade_zone() 
# Update Contract Symbol ab.update_contract_symbol(). If last friday is holiday this code dosent run and the symbol is not updated and the program fails
# Consider seperate sl_buffer for nifty and bank in get_trade_price()
# Check if order parameters like order type and others can be paramterised
# Look at close pending orders, my not be efficient, exception handling and all
# WebSocket disconnection and subscription/tick loss issue. Upgraded the package  
# Option of MIS orders for bank to be added, maybe for nifty as well. Can test with nifty 
# check_MTM_Limit() limitation : if other nifty or bank scrips are traded this will messup the position
# trade_limit_reached() moved before check_pending_orders(). Need to check if this is the correct approach
# get_trade_price bo_level to be parameterised from .ini 0 , 1 (half of atr), 2 (~atr)
# If ATR > 10 or something activate BO3
# In ST up/down if ST_MEDIUM is down/Up - If high momentum (check rate of change) chances are it will break medium SL 
# Look at 3 min to 6 min crossover points , compare ST values of low and medium for possible override
# Retun/Exit function after Postion check in buy/sell function fails 
# Look at df_nifty.STX.values; Can we use tail to get last n values in the list
# Can have few tasks to be taken care/check each min like MTM/Tradefalg check/set. This is apart from interval
# Delay of 146 secs, 57 secs, 15 secs etc seen. Check and Need to handle 
# Look at 5/10 mins trend, dont take positions against the trend
# Keep limit price at 10% from ST and Sl beyond 10% from ST
# Relook at supertrend multiplier=2.5 option instead of current 3
# NSE Premarket method values may not be current as bank open time is considered . Need to fetch this realtime around 915 
# May need try/catch in reading previous day datafile due to copy of ini file or failed runs
# Can look at frequency of data export through parameter, say 60,120,240 etc.. 

# Guidelines:
# TSL to be double of SL (Otherwise mostly SLs are hit as they tend to )
# SL will be hit in high volatility. SL may be set to ATR*3 or medium df Supertrend Value
# Always buy market, in case SL reverse and get out cost to cost. Market has to come up, but mind expiry :)  
# SLs are usually hit in volatile market, so see if you can use less qty and no SLs, especially bank.
# Dont go against the trend in any case. 
# Avoid manual trades

# To Manually run program use following command
# python3 ab.py &


# Release notes for ab_options.py


# from pandas.core.indexing import is_label_like
import ab_lib
from ab_lib import *
import sys
import time
import threading

# Reduce position to cut loss if price is going against the trade, can close BO1

# Manual Activities
# Frequency - Monthly , Change Symbol of nifty/bank in .ini

# Enable logging to file 
sys.stdout = sys.stderr = open(r"./log/ab_options_" + datetime.datetime.now().strftime("%Y%m%d") +".log" , "a")


######################################
#       Initialise variables
######################################
INI_FILE = "ab_options.ini"              # Set .ini file name used for storing config info.
# Load parameters from the config file
cfg = configparser.ConfigParser()
cfg.read(INI_FILE)

# Set user profile; Access token and other user specific info from .ini will be pulled from this section
ab_lib.strChatID = cfg.get("tokens", "chat_id")
ab_lib.strBotToken = cfg.get("tokens", "options_bot_token")    #Bot include "bot" prefix in the token
strMsg = "Initialising " + __file__
iLog(strMsg,sendTeleMsg=True)


# crontabed this at 9.00 am instead of 8.59 
# Set initial sleep time to match the bank market opening time of 9:00 AM to avoid previous junk values
init_sleep_seconds = int(cfg.get("info", "init_sleep_seconds"))
strMsg = "Setting up initial sleep time of " + str(init_sleep_seconds) + " seconds."
iLog(strMsg,sendTeleMsg=True)
time.sleep(init_sleep_seconds)

susername = cfg.get("tokens", "uid")
spassword = cfg.get("tokens", "pwd")

# Realtime variables also loaded in get_realtime_config()
enableBO2_nifty = int(cfg.get("realtime", "enableBO2_nifty"))   # True = 1 (or non zero) False=0 
enableBO3_nifty = int(cfg.get("realtime", "enableBO3_nifty"))   # True = 1 (or non zero) False=0 
enableBO2_bank = int(cfg.get("realtime", "enableBO2_bank"))         # BankNifty ;True = 1 (or non zero) False=0 
enableBO3_bank = int(cfg.get("realtime", "enableBO3_bank"))         # BankNifty ;True = 1 (or non zero) False=0 
trade_nfo = int(cfg.get("realtime", "trade_nfo"))                 # Trade Nifty options. True = 1 (or non zero) False=0
trade_bank = int(cfg.get("realtime", "trade_bank"))                 # Trade Bank Nifty options. True = 1 (or non zero) False=0
nifty_sl = float(cfg.get("realtime", "nifty_sl"))               #15.0 ?
bank_sl = float(cfg.get("realtime", "bank_sl"))                     #30.0 ?
mtm_sl = int(cfg.get("realtime", "mtm_sl"))                     #amount below which program exit all positions 
mtm_target = int(cfg.get("realtime", "mtm_target"))             #amount above which program exit all positions and not take new positions
nifty_bo1_qty = int(cfg.get("realtime", "nifty_bo1_qty"))
nifty_bo2_qty = int(cfg.get("realtime", "nifty_bo2_qty"))
nifty_bo3_qty = int(cfg.get("realtime", "nifty_bo3_qty"))
bank_bo1_qty = int(cfg.get("realtime", "bank_bo1_qty"))
bank_bo2_qty = int(cfg.get("realtime", "bank_bo2_qty"))
bank_bo3_qty = int(cfg.get("realtime", "bank_bo3_qty"))
sl_buffer = int(cfg.get("realtime", "sl_buffer"))
nifty_ord_type = cfg.get("realtime", "nifty_ord_type")      # BO / MIS
bank_ord_type = cfg.get("realtime", "bank_ord_type")      # MIS / BO
# atr * level * 0.5 (lvl = 0->close, -1->Mkt Price, 1,2,3..based on times of atr gap required)
nifty_ord_exec_level1 = float(cfg.get("realtime", "nifty_ord_exec_level1"))
nifty_ord_exec_level2 = float(cfg.get("realtime", "nifty_ord_exec_level2"))
nifty_ord_exec_level3 = float(cfg.get("realtime", "nifty_ord_exec_level3"))

bank_ord_exec_level1 = float(cfg.get("realtime", "bank_ord_exec_level1"))
bank_ord_exec_level2 = float(cfg.get("realtime", "bank_ord_exec_level2"))
bank_ord_exec_level3 = float(cfg.get("realtime", "bank_ord_exec_level3"))

nifty_strike_ce_offset = float(cfg.get("realtime", "nifty_strike_ce_offset"))
nifty_strike_pe_offset = float(cfg.get("realtime", "nifty_strike_pe_offset"))
bank_strike_ce_offset = float(cfg.get("realtime", "bank_strike_ce_offset"))
bank_strike_pe_offset = float(cfg.get("realtime", "bank_strike_pe_offset"))

# nifty_lot_size = int(cfg.get("info", "nifty_lot_size"))
# criude_lot_size = int(cfg.get("info", "bank_lot_size"))

#List of thurshdays when its NSE holiday, hence reduce 1 day to get expiry date 
weekly_expiry_holiday_dates = cfg.get("info", "weekly_expiry_holiday_dates").split(",")


# Below will be derived dynamically. Would be the ATM strike
# nifty_symbol = cfg.get("info", "nifty_symbol")
# bank_symbol = cfg.get("info", "bank_symbol")

nifty_tgt1 = float(cfg.get("info", "nifty_tgt1"))   #30.0
nifty_tgt2 = float(cfg.get("info", "nifty_tgt2"))   #60.0 medium target
nifty_tgt3 = float(cfg.get("info", "nifty_tgt3"))   #150.0 high target
bank_tgt1 = float(cfg.get("info", "bank_tgt1"))     #30.0
bank_tgt2 = float(cfg.get("info", "bank_tgt2"))     #90.0
bank_tgt3 = float(cfg.get("info", "bank_tgt2"))     #200.0

olhc_duration = int(cfg.get("info", "olhc_duration"))   #3
nifty_sqoff_time = int(cfg.get("info", "nifty_sqoff_time")) #1512 time after which orders not to be processed and open orders to be cancelled
# bank_sqoff_time = int(cfg.get("info", "bank_sqoff_time")) #2310 time after which orders not to be processed and open orders to be cancelled

nifty_tsl = int(cfg.get("info", "nifty_tsl"))   #Trailing Stop Loss for Nifty
bank_tsl = int(cfg.get("info", "bank_tsl"))     #Trailing Stop Loss for BankNifty
rsi_buy_param = int(cfg.get("info", "rsi_buy_param"))   #may need exchange/indicator specific; ML on this?
rsi_sell_param = int(cfg.get("info", "rsi_sell_param"))
premarket_advance = int(cfg.get("info", "premarket_advance"))
premarket_decline = int(cfg.get("info", "premarket_decline"))
premarket_flag = int(cfg.get("info", "premarket_flag"))          # whether premarket trade enabled  or not 1=yes
nifty_last_close = float(cfg.get("info", "nifty_last_close"))
# file_bank = cfg.get("info", "file_bank")

# Below 2 Are Base Flag For nifty /bank nifty trading_which is used to reset daily(realtime) flags(trade_nfo,trade_bn) as 
# they might have been changed during the day in realtime 
enable_bank = int(cfg.get("info", "enable_bank"))                         # 1=Original flag for BANKNIFTY trading. Daily(realtime) flag to be reset eod based on this.  
enable_NFO = int(cfg.get("info", "enable_NFO"))                         # 1=Original flag for Nifty trading. Daily(realtime) flag to be reset eod based on this.
enable_bank_data = int(cfg.get("info", "enable_bank_data"))               # 1=CRUDE data subscribed, processed and saved/exported 
enable_NFO_data = int(cfg.get("info", "enable_NFO_data"))               # 1=NIFTY data subscribed, processed and saved/exported
file_nifty = cfg.get("info", "file_nifty")
file_nifty_med = cfg.get("info", "file_nifty_med")
file_bank = cfg.get("info", "file_bank")
file_bank_med = cfg.get("info", "file_bank_med")
no_of_trades_limit = int(cfg.get("info", "no_of_trades_limit"))         # 2 BOs trades per order; 6 trades for 3 orders
pending_ord_limit_mins = int(cfg.get("info", "pending_ord_limit_mins")) # Close any open orders not executed beyond the set limit

# curde_trade_start_time = int(cfg.get("info", "curde_trade_start_time"))
# curde_trade_end_time = int(cfg.get("info", "curde_trade_end_time"))
nifty_trade_start_time = int(cfg.get("info", "nifty_trade_start_time"))
nifty_trade_end_time = int(cfg.get("info", "nifty_trade_end_time"))
sl_wait_time = int(cfg.get("info", "sl_wait_time"))

lst_nifty_ltp = []
lst_bank_ltp = []


socket_opened = False

# Counters for dataframe indexes
df_nifty_cnt = 0           
df_nifty_med_cnt = 0       
df_bank_cnt = 0
df_bank_med_cnt = 0   


df_cols = ["cur_HHMM","open","high","low","close","signal","sl"]  # v1.1 added signal column

df_nifty = pd.DataFrame(data=[],columns=df_cols)        # Low - to store 3 mins level OHLC data for nifty
df_bank = pd.DataFrame(data=[],columns=df_cols)         # Low - to store 3 mins level OHLC data for banknifty

df_bank_med = pd.DataFrame(data=[],columns=df_cols)     # Medium - to store 6 mins level OHLC data bn
df_nifty_med = pd.DataFrame(data=[],columns=df_cols)    # Medium - to store 6 mins level OHLC nifty

dict_ltp = {}       #Will contain dictionary of token and ltp pulled from websocket
dict_sl_orders = {} #Dictionary to store SL Order ID, token,symbol, target price; if ltp > target price then update the SL order limit price.

# lst_nifty = []  
cur_min = 0
flg_min = 0
flg_med_nifty = 0               # Flag for avoiding consecutive orders when medium signal is generated 
flg_med_bank = 0
MTM = 0.0                       # Float
pos_bank = 0                    # current banknifty position 
pos_nifty = 0                   # current nifty position


super_trend_nifty = []          # Supertrend list Nifty
super_trend_bank = []           # Supertrend list BankNifty
interval = olhc_duration        # Time interval of candles in minutes; 3 
processNiftyEOD = False         # Process pending Nifty order cancellation and saving of df data; Flag to run procedure only once
export_data = 0                 # Realtime export of bn and nifty dataframe; triggered through .ini; reset to 0 after export


token_nifty_ce = 1111           # Set by get instrument later in the code
token_nifty_pe = 2222
token_bank_ce = 1111           
token_bank_pe = 2222


ltp_nifty_ATM_CE = 0            # Last traded price for Nifty ATM CE
ltp_nifty_ATM_PE = 0            # Last traded price for Nifty ATM PE
ltp_bank_ATM_CE = 0             # Last traded price for BankNifty ATM CE
ltp_bank_ATM_PE = 0             # Last traded price for BankNifty ATM PE


############################################################################
#       Functions
############################################################################
def get_realtime_config():
    '''This procedure can be called during execution to get realtime values from the .ini file'''

    global trade_nfo, trade_bank, enableBO2_bank, enableBO2_nifty, enableBO3_nifty,nifty_ord_exec_level1,bank_ord_exec_level1\
    ,mtm_sl,mtm_target, cfg, nifty_sl, bank_sl, export_data, sl_buffer, nifty_ord_type, bank_ord_type\
        ,nifty_strike_ce_offset, nifty_strike_pe_offset, bank_strike_ce_offset, bank_strike_pe_offset

    cfg.read(INI_FILE)
    
    trade_nfo = int(cfg.get("realtime", "trade_nfo"))                   # True = 1 (or non zero) False=0
    trade_bank = int(cfg.get("realtime", "trade_bank"))                 # True = 1 (or non zero) False=0
    enableBO2_nifty = int(cfg.get("realtime", "enableBO2_nifty"))       # True = 1 (or non zero) False=0
    enableBO3_nifty = int(cfg.get("realtime", "enableBO3_nifty"))       # True = 1 (or non zero) False=0
    enableBO2_bank = int(cfg.get("realtime", "enableBO2_bank"))         # True = 1 (or non zero) False=0 
    nifty_sl = float(cfg.get("realtime", "nifty_sl"))                   #20.0
    bank_sl = float(cfg.get("realtime", "bank_sl"))                     #15.0
    export_data = float(cfg.get("realtime", "export_data"))
    mtm_sl = float(cfg.get("realtime", "mtm_sl"))
    mtm_target  = float(cfg.get("realtime", "mtm_target"))
    #print(enableBO2,enableBO3,trade_nfo,trade_bn,flush=True)
    sl_buffer = int(cfg.get("realtime", "sl_buffer"))
    nifty_ord_type = cfg.get("realtime", "nifty_ord_type")      # BO / MIS
    bank_ord_type = cfg.get("realtime", "bank_ord_type")        # MIS / BO
    nifty_ord_exec_level1 = float(cfg.get("realtime", "nifty_ord_exec_level1"))
    bank_ord_exec_level1 = float(cfg.get("realtime", "bank_ord_exec_level1"))
    nifty_strike_ce_offset = float(cfg.get("realtime", "nifty_strike_ce_offset"))
    nifty_strike_pe_offset = float(cfg.get("realtime", "nifty_strike_pe_offset"))
    bank_strike_ce_offset = float(cfg.get("realtime", "bank_strike_ce_offset"))
    bank_strike_pe_offset = float(cfg.get("realtime", "bank_strike_pe_offset"))

def savedata(flgUpdateConfigFile=True):
    '''flgUpdateConfigFile = True Updates datafilename in the .ini file for nextday reload.
    
     In case of intermediary exports you may not want to update the datafile in the .ini file'''

    iLog("In savedata(). Exporting dataframes to .csv files.",6)    # Log as activity

    try:
        ts_ext = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".csv"
        if enable_NFO_data:
            file_nifty = "./data/NIFTY_OPT_" + ts_ext 
            file_nifty_med = "./data/NIFTY_OPT_MED_" + ts_ext
            df_nifty.to_csv(file_nifty,index=False)
            df_nifty_med.to_csv(file_nifty_med,index=False)

        if enable_bank_data:
            file_bn = "./data/BN_" + ts_ext
            file_bn_med = "./data/BN_MED_" + ts_ext
            df_bank.to_csv(file_bn,index=False)
            df_bank_med.to_csv(file_bn_med,index=False)

        # Save nifty and bn filenames for use in next day to load last 10 rows
        if flgUpdateConfigFile :
            if enable_NFO_data:
                cfg.set("info","file_nifty",file_nifty)
                cfg.set("info","file_nifty_med",file_nifty_med)
            
            if enable_bank_data:
                cfg.set("info","file_bn",file_bn)
                cfg.set("info","file_bn_med",file_bn_med)

            with open(INI_FILE, 'w') as configfile:
                cfg.write(configfile)
                configfile.close()

    except Exception as ex:
        iLog("In savedata(). Exception occured = " + str(ex),3)

def place_sl_order(main_order_id, nifty_bank, ins_opt):
    ''' nifty_bank = NIFTY | BANK '''

    print(f"In place_sl_order():main_order_id={main_order_id}, nifty_bank={nifty_bank}",flush=True)

    lt_price = 0.0
    wait_time = sl_wait_time      # Currently set to 60 * 2 (sleep) = 120 seconds(2 mins). Can be parameterised 
    order_executed = False
    strMsg = ""
    
    while wait_time > 0:
        print(f"wait_time={wait_time}",flush=True)
        try:
            orders = alice.get_order_history()["data"]["completed_orders"]
            for ord in orders:
                if ord["oms_order_id"]==main_order_id:
                    print(f"In place_sl_order(): ord['order_status']={ord['order_status']},ord['price']={ord['price']}. Ord =\n",ord, flush=True)
                    # Order may be rejected as well
                    if ord["order_status"]=="complete": 
                        lt_price = ord["price"]
                        order_executed = True
                    break   #break for loop
        except Exception as ex:
            print("In place_sl_order(): Exception = ",ex,flush=True)
        
        if order_executed : break   #break while loop

        time.sleep(2)

        wait_time = wait_time - 1

    if order_executed:
        time.sleep(10)  #As order might not be completely filled / alice blue takes time to recognise margin.
        #place SL order
        #---- Intraday order (MIS) , SL Order
        
        if nifty_bank == "NIFTY": 
            # ins_opt =  ins_bank_opt
            bo1_qty = nifty_bo1_qty
            sl = bank_sl
            tgt1 = bank_tgt1
        elif nifty_bank == "BANK":
            # ins_opt =  ins_nifty_opt
            bo1_qty = bank_bo1_qty
            sl = nifty_sl
            tgt1 = nifty_tgt1
        

        order = squareOff_MIS(TransactionType.Sell, ins_opt, bo1_qty, OrderType.StopLossLimit, float(lt_price-sl))
        if order['status'] == 'success':
            strMsg = f"In place_sl_order(): MIS SL order_id={order['data']['oms_order_id']}, Target Price={float(lt_price-sl)}"
            #update dict with SL order ID : [token, target price, instrument]
            dict_sl_orders.update({order['data']['oms_order_id']:[ins_opt[1], lt_price+tgt1, ins_opt] } )
            print("dict_sl_orders=",dict_sl_orders, flush=True)
        else:
            strMsg = f"In place_sl_order(): MIS SL Order Failed.={order['message']}" 
        
    else:
        #cancel main order
        ret = alice.cancel_order(main_order_id)
        print("ret=alice.cancel_order()=>",ret, flush=True)
        strMsg = "place_sl_order(): main order= not executed within the wait time of 120 seconds, hence cancelled the order " + main_order_id

    iLog(strMsg,sendTeleMsg=True)

def squareOff_MIS(buy_sell,ins_scrip,qty, order_type = OrderType.Market, limit_price=0.0,order_tag= None):
    '''Square off MIS positions at EoD or when mtm limit is reached. Also used for placing Market orders. 
    buy_sell = TransactionType.Buy/TransactionType.Sell

    order_type = OrderType.StopLossLimit Default is Market order

    limit_price = limit price in case SL order needs to be placed 
    '''
    global alice

    ord_obj = {}

    if limit_price > 1 : 
        trigger_price = limit_price
    else:
        trigger_price = None

    try:
        ord_obj=alice.place_order(transaction_type = buy_sell,
                         instrument = ins_scrip,
                         quantity = qty,
                         order_type = order_type,
                         product_type = ProductType.Intraday,
                         price = limit_price,
                         trigger_price = trigger_price,
                         stop_loss = None,
                         square_off = None,
                         trailing_sl = None,
                         is_amo = False,
                         order_tag = order_tag)

        strMsg = "In squareOff_MIS(): buy_sell={},ins_scrip={},qty={},order_type={},limit_price={}".format(buy_sell,ins_scrip,qty,order_type,limit_price)
        iLog(strMsg,6,sendTeleMsg=True)
    
    except Exception as ex:
        iLog("Exception occured in squareOff_MIS():"+str(ex),3)

    return ord_obj

def buy_signal(ins_scrip,qty,limit_price,stop_loss_abs,target_abs,trailing_sl_abs,product_type=ProductType.BracketOrder):
    global alice
    #ord=
    #{'status': 'success', 'message': 'Order placed successfully', 'data': {'oms_order_id': '200416000176487'}}
    #{'status': 'error', 'message': 'Error Occurred :Trigger price cannot be greater than Limit Price', 'data': {}}
    #ord1['status']=='success'
    #print(ord['data']['oms_order_id'])
    try:
        ord_obj=alice.place_order(transaction_type = TransactionType.Buy,
                         instrument = ins_scrip,
                         quantity = qty,
                         order_type = OrderType.Limit,
                         product_type = product_type,
                         price = float(limit_price),
                         trigger_price = float(limit_price),
                         stop_loss = float(stop_loss_abs),
                         square_off = target_abs,
                         trailing_sl = trailing_sl_abs,
                         is_amo = False)
    except Exception as ex:
            # print("Exception occured in buy_signal():",ex,flush=True)
            #ord_obj={'status': 'error'} not required as api gives this in case of actual error
    #print("buy_signal():ins_scrip,qty,limit_price,stop_loss_abs,target_abs,trailing_sl_abs:",ins_scrip,qty,limit_price,stop_loss_abs,target_abs,trailing_sl_abs,flush=True)
            iLog("Exception occured in buy_signal():"+str(ex),3)

    return ord_obj

def sell_signal(ins_scrip,qty,limit_price,stop_loss_abs,target_abs,trailing_sl_abs,product_type=ProductType.BracketOrder):
    global alice
    try:
        ord_obj=alice.place_order(transaction_type = TransactionType.Sell,
                         instrument = ins_scrip,
                         quantity = qty,
                         order_type = OrderType.Limit,
                         product_type = product_type,
                         price = limit_price,
                         trigger_price = limit_price,
                         stop_loss = stop_loss_abs,
                         square_off = target_abs,
                         trailing_sl = trailing_sl_abs,
                         is_amo = False)
          
    except Exception as ex:
            # print("Exception occured in sell_signal():",ex,flush=True)
            iLog("Exception occured in sell_signal():"+str(ex),3)
    #print("sell_signal():ins_scrip,qty,limit_price,stop_loss_abs,target_abs,trailing_sl_abs:",ins_scrip,qty,limit_price,stop_loss_abs,target_abs,trailing_sl_abs,flush=True)
    
    return ord_obj

def buy_nifty_options(strMsg):
   
    global df_nifty

    df_nifty.iat[-1,5] = "B"  # v1.1 set signal column value


    # strMsg == NIFTY_CE | NIFTY_PE 
    lt_price, nifty_sl = get_trade_price_options(strMsg,"BUY",nifty_ord_exec_level1)   # Get trade price and SL for BO1 
   
    df_nifty.iat[-1,6] = nifty_sl  # v3.7 set sl column value. This is only for BO1; rest BOs will different SLs 

    # iLog(strMsg)    #can be commented later

    #Warning: No initialisation done
    if strMsg == "NIFTY_CE" :
        ins_nifty_opt = ins_nifty_ce
    elif strMsg == "NIFTY_PE" :
        ins_nifty_opt = ins_nifty_pe
    

    strMsg = strMsg + " Limit Price=" + str(lt_price) + " SL=" + str(nifty_sl)

    # Can be parameterised
    if lt_price<30 or lt_price>300 :
        strMsg = strMsg + " buy_nifty(): Limit Price not in buying range."
        iLog(strMsg,2,sendTeleMsg=True)
        return
    
    if not trade_nfo:
        strMsg = strMsg + " buy_nifty(): trade_nfo=0. Order not initiated."
        iLog(strMsg,2,sendTeleMsg=True)
        return

    if not check_trade_time_zone("NIFTY"):
        strMsg = strMsg + " buy_nifty(): No trade time zone. Order not initiated."
        iLog(strMsg,2,sendTeleMsg=True)
        return


    # Find CE or PE Position
    if pos_nifty > 0:   # Position updates in MTM check
        strMsg = "buy_nifty(): Position already exists. " + strMsg    #do not buy if position already exists; 
    else:

        if trade_limit_reached("NIFTY"):
            strMsg = strMsg + "buy_nifty(): NIFTY Trade limit reached."
            iLog(strMsg,2,sendTeleMsg=True)
            return

        # Cancel pending buy orders and close existing sell orders if any
        close_all_orders("NIFTY")
        
        if nifty_ord_type == "MIS" : 
            #---- Intraday order (MIS) , Market Order
            # order = squareOff_MIS(TransactionType.Buy, ins_nifty_opt,nifty_bo1_qty)
            # order_tag = datetime.datetime.now().strftime("NF_%H%M%S")
            order = squareOff_MIS(TransactionType.Buy, ins_nifty_opt,nifty_bo1_qty, OrderType.Limit, lt_price)
            if order['status'] == 'success':
                strMsg = strMsg + " buy_nifty(): Initiating place_sl_order(). main_order_id==" +  str(order['data']['oms_order_id'])
                iLog(strMsg,sendTeleMsg=True)   # Can be commented later
                t = threading.Thread(target=place_sl_order,args=(order['data']['oms_order_id'],"NIFTY",ins_nifty_opt,))
                t.start()

            else:
                strMsg = strMsg + ' buy_nifty(): MIS Order Failed.' + order['message']


        elif nifty_ord_type == "BO" :
            #---- First Bracket order for initial target
            order = buy_signal(ins_nifty_opt,nifty_bo1_qty,lt_price,nifty_sl,nifty_tgt1,nifty_tsl)    #SL to be float; 
            if order['status'] == 'success' :
                # buy_order1_nifty = order['data']['oms_order_id']
                strMsg = strMsg + " 1st BO order_id=" + str(order['data']['oms_order_id'])
            else:
                strMsg = strMsg + ' buy_nifty() 1st BO Failed.' + order['message']

            #---- Second Bracket order for open target
            if enableBO2_nifty:
                # lt_price, nifty_sl = get_trade_price("NIFTY","BUY",nifty_ord_exec_level2)   # Get trade price and SL for BO2
                order = buy_signal(ins_nifty_opt,nifty_bo2_qty,lt_price,nifty_sl,nifty_tgt2,nifty_tsl)
                strMsg = strMsg + " BO2 Limit Price=" + str(lt_price) + " SL=" + str(nifty_sl)
                if order['status'] == 'success':
                    # buy_order2_nifty = order['data']['oms_order_id']
                    strMsg = strMsg + " 2nd BO order_id=" + str(order['data']['oms_order_id'])
                else:
                    strMsg=strMsg + ' buy_nifty() 2nd BO Failed.' + order['message']

            #---- Third Bracket order for open target
            if enableBO3_nifty:  
                # lt_price, nifty_sl = get_trade_price("NIFTY","BUY",nifty_ord_exec_level3)   # Get trade price and SL for BO3
                order = buy_signal(ins_nifty_opt,nifty_bo3_qty,lt_price,nifty_sl,nifty_tgt3,nifty_tsl)
                strMsg = strMsg + " BO3 Limit Price=" + str(lt_price) + " SL=" + str(nifty_sl)
                if order['status']=='success':
                    # buy_order3_nifty = order['data']['oms_order_id']
                    strMsg = strMsg + " 3rd BO order_id=" + str(order['data']['oms_order_id'])
                else:
                    strMsg=strMsg + ' buy_nifty() 3rd BO Failed.' + order['message']

    iLog(strMsg,sendTeleMsg=True)

def buy_bank_options(strMsg):
    '''Buy Banknifty options '''
    global df_bank

    df_bank.iat[-1,5] = "B"  # v1.1 set signal column value


    # strMsg == CE | PE 
    lt_price, bank_sl = get_trade_price_options(strMsg,"BUY",bank_ord_exec_level1)   # Get trade price and SL for BO1 
   
    df_bank.iat[-1,6] = bank_sl  # v3.7 set sl column value. This is only for BO1; rest BOs will different SLs 

    # iLog(strMsg)    #can be commented later

    #Warning: No initialisation done
    if strMsg == "BANK_CE" :
        ins_bank_opt = ins_bank_ce
    elif strMsg == "BANK_PE" :
        ins_bank_opt = ins_bank_pe
    

    strMsg = strMsg + " Limit Price=" + str(lt_price) + " SL=" + str(bank_sl)

    
    if lt_price<50 or lt_price>350 :
        strMsg = strMsg + " buy_bank(): Limit Price not in buying range."
        iLog(strMsg,2,sendTeleMsg=True)
        return

    if not trade_bank :
        strMsg = strMsg + " buy_bank(): trade_bank=0. Order not initiated."
        iLog(strMsg,2,sendTeleMsg=True)
        return

    if not check_trade_time_zone("NIFTY"):
        strMsg = strMsg + " buy_bank(): No trade time zone. Order not initiated."
        iLog(strMsg,2,sendTeleMsg=True)
        return


    # Find CE or PE Position
    if pos_bank > 0:   # Position updates in MTM check
        strMsg = "buy_bank(): Position already exists. " + strMsg    #do not buy if position already exists; 
    else:

        if trade_limit_reached("BANKN"):
            strMsg = strMsg + "buy_bank(): BankNIFTY Trade limit reached."
            iLog(strMsg,2,sendTeleMsg=True)
            return

        # Cancel pending buy orders and close existing sell orders if any
        close_all_orders("BANK")
        
        if bank_ord_type == "MIS" : 
            #---- Intraday order (MIS) , Market Order
            # order = squareOff_MIS(TransactionType.Buy, ins_bank_opt,bank_bo1_qty)
            # order_tag = datetime.datetime.now().strftime("BN_%H%M%S")
            order = squareOff_MIS(TransactionType.Buy, ins_bank_opt,bank_bo1_qty, OrderType.Limit, lt_price)
            if order['status'] == 'success':
                strMsg = strMsg + " buy_bank(): Initiating place_sl_order(). main_order_id=" + str(order['data']['oms_order_id']) 
                iLog(strMsg,sendTeleMsg=True)   # Can be commented later
                t = threading.Thread(target=place_sl_order,args=(order['data']['oms_order_id'],"BANK",ins_bank_opt,))
                t.start()


            else:
                strMsg = strMsg + ' buy_bank(): MIS Order Failed.' + order['message']



        elif bank_ord_type == "BO" :
            #---- First Bracket order for initial target
            order = buy_signal(ins_bank_opt,bank_bo1_qty,lt_price,bank_sl,bank_tgt1,bank_tsl)    #SL to be float; 
            if order['status'] == 'success' :
                # buy_order1_bank = order['data']['oms_order_id']
                strMsg = strMsg + " 1st BO order_id=" + str(order['data']['oms_order_id'])
            else:
                strMsg = strMsg + ' buy_bank() 1st BO Failed.' + order['message']

            #---- Second Bracket order for open target
            if enableBO2_bank:
                # lt_price, bank_sl = get_trade_price("NIFTY","BUY",bank_ord_exec_level2)   # Get trade price and SL for BO2
                order = buy_signal(ins_bank_opt,bank_bo2_qty,lt_price,bank_sl,bank_tgt2,bank_tsl)
                strMsg = strMsg + " BO2 Limit Price=" + str(lt_price) + " SL=" + str(bank_sl)
                if order['status'] == 'success':
                    # buy_order2_bank = order['data']['oms_order_id']
                    strMsg = strMsg + " 2nd BO order_id=" + str(order['data']['oms_order_id'])
                else:
                    strMsg=strMsg + ' buy_bank() 2nd BO Failed.' + order['message']

            #---- Third Bracket order for open target
            if enableBO3_bank:  
                # lt_price, bank_sl = get_trade_price("NIFTY","BUY",bank_ord_exec_level3)   # Get trade price and SL for BO3
                order = buy_signal(ins_bank_opt,bank_bo3_qty,lt_price,bank_sl,bank_tgt3,bank_tsl)
                strMsg = strMsg + " BO3 Limit Price=" + str(lt_price) + " SL=" + str(bank_sl)
                if order['status']=='success':
                    # buy_order3_bank = order['data']['oms_order_id']
                    strMsg = strMsg + " 3rd BO order_id=" + str(order['data']['oms_order_id'])
                else:
                    strMsg=strMsg + ' buy_bank() 3rd BO Failed.' + order['message']

    iLog(strMsg,sendTeleMsg=True)

def subscribe_ins():
    global alice,ins_nifty,ins_bank

    try:
        if enable_NFO_data : 
            # Check if one cal
            alice.subscribe(ins_nifty, LiveFeedType.COMPACT)
            alice.subscribe(ins_nifty_ce, LiveFeedType.COMPACT)
            alice.subscribe(ins_nifty_pe, LiveFeedType.COMPACT)

        if enable_bank_data : 
            # Check if one cal
            alice.subscribe(ins_bank, LiveFeedType.COMPACT)
            alice.subscribe(ins_bank_ce, LiveFeedType.COMPACT)
            alice.subscribe(ins_bank_pe, LiveFeedType.COMPACT)

        # if enable_bn_data : alice.subscribe(ins_bn, LiveFeedType.COMPACT)
        pass     
    except Exception as ex:
        iLog("subscribe_ins(): Exception="+ str(ex),3)

    # print(datetime.datetime.now() ,"In subscribe_ins()",flush=True)
    iLog("subscribe_ins().")

def close_all_orders(opt_index="ALL",buy_sell="ALL",ord_open_time=0):
    '''Cancel pending orders. opt_index=ALL/BANKN/NIFTY , buy_sell = ALL/BUY/SELL'''
    # print(datetime.datetime.now(),"In close_all_orders().",opt_index,flush=True)

    #Square off MIS Positions if any
    if (opt_index=='NIFTY' or opt_index=='ALL') and nifty_ord_type == "MIS":
        if pos_nifty > 0 :
            iLog(f"Closing Nifty Open Positions pos_nifty={pos_nifty} - Execution Commented",2,sendTeleMsg=True)   
            # squareOff_MIS(TransactionType.Sell, ins_nifty_opt,pos_nifty)
            # needs to be managed with SL orders
        elif pos_nifty < 0 :
            iLog(f"Option position cannot be negative pos_nifty={pos_nifty}",2,sendTeleMsg=True)
            # squareOff_MIS(TransactionType.Buy, ins_nifty_opt, abs(pos_nifty))

    if (opt_index=='BANK'  or opt_index=='ALL') and nifty_ord_type == "MIS":
        if pos_bank > 0 :
            iLog(f"Closing BankNifty Open Positions pos_bank={pos_bank} - Execution Commented",2,sendTeleMsg=True)   
            # squareOff_MIS(TransactionType.Sell, ins_bank_opt ,pos_bank)
            # needs to be managed with SL orders
        elif pos_bank < 0 :
            iLog(f"Option position cannot be negative pos_bank={pos_bank}",2,sendTeleMsg=True)


    # Get pending orders and cancel them
    try:
        orders = alice.get_order_history()['data']['pending_orders'] #Get all orders
        if not orders:
            # print(datetime.datetime.now(),"In close_all_orders(). No Pending Orders found.",opt_index,flush=True)
            iLog("close_all_orders(): No Pending Orders found for "+ str(opt_index))
            return    
        # Else is captured below exception
        
    except Exception as ex:
        orders = None
        # print("In close_all_orders(). Exception="+ str(ex),flush=True)
        iLog("close_all_orders(): Exception="+ str(ex),3)
        return

    if opt_index == "ALL":
        # If this proc is called in each interval, Check for order open time and leg indicator is blank for main order
        if ord_open_time > 0 :
            today = datetime.datetime.now()
            
            for c_order in orders:
                diff =  today - datetime.datetime.fromtimestamp(c_order['order_entry_time'])
                # print("diff.total_seconds()=",diff.total_seconds(), "c_order['leg_order_indicator']=",c_order['leg_order_indicator'], flush=True)
                
                if (c_order['leg_order_indicator'] == '') and  (diff.total_seconds() / 60) > ord_open_time :
                    iLog("close_all_orders(): Cancelling order due to order open limit time crossed for Ord. no. : " + c_order['oms_order_id'],sendTeleMsg=True)
                    alice.cancel_order(c_order['oms_order_id'])

        else:
            #Cancel all open orders
            iLog("close_all_orders(): Cancelling all orders ") #+ c_order['oms_order_id'])
            alice.cancel_all_orders()
    else:
        for c_order in orders:
            #if c_order['leg_order_indicator']=='' then its actual pending order not leg order
            if opt_index == c_order['trading_symbol'][:5]:
                if buy_sell == "ALL" :
                    iLog("close_all_orders(): Cancelling order "+c_order['oms_order_id'])
                    alice.cancel_order(c_order['oms_order_id'])    

                elif buy_sell == c_order['transaction_type']:
                    iLog("close_all_orders(): Cancelling order "+c_order['oms_order_id'])
                    alice.cancel_order(c_order['oms_order_id'])


    iLog("close_all_orders(): opt_index={},buy_sell={},ord_open_time={}".format(opt_index,buy_sell,ord_open_time)) #6 = Activity/Task done

def check_MTM_Limit():
    ''' Checks and returns the current MTM and sets the trading flag based on the limit specified in the 
    .ini. This needs to be called before buy/sell signal generation in processing. 
    Also updates the postion counter for Nifty and bank which are used in buy/sell procs.'''
    
    global trade_bank, trade_nfo, pos_nifty, pos_bank

    trading_symbol = ""
    mtm = 0.0
    pos_bank = 0
    pos_nifty = 0

    # Get position and mtm
    try:    # Get netwise postions (MTM)
        pos = alice.get_netwise_positions()
        if pos:
            pos_bank = 0
            pos_nifty = 0
            for p in  pos['data']['positions']:
                mtm = float(p['m2m'].replace(",","")) + mtm
                # print("get_position()",p['trading_symbol'],p['net_quantity'],flush=True)
                trading_symbol = p['trading_symbol'][:5]
                if trading_symbol == 'NIFTY':
                    pos_nifty = pos_nifty + int(p['net_quantity'])

                elif trading_symbol == 'BANKN':
                    pos_bank = pos_bank + int(p['net_quantity'])

    except Exception as ex:
        mtm = -1.0  # To ignore in calculations in case of errors
        print("check_MTM_Limit(): Exception=",ex, flush = True)
    
    # print(mtm,mtm_sl,mtm_target,flush=True)

    # Enable trade flags based on MTM limits set
    if (mtm < mtm_sl or mtm > mtm_target) and (trade_bank==1 or trade_nfo==1): # or mtm>mtm_target:
        trade_bank = 0
        trade_nfo = 0
        # Stop further trading and set both the trading flag to 0
        cfg.set("realtime","trade_nfo","0")
        cfg.set("realtime","trade_bank","0")

        try:
            with open(INI_FILE, 'w') as configfile:
                cfg.write(configfile)
                configfile.close()
            
            strMsg = "check_MTM_Limit(): Trade flags set to false. MTM={}, trade_nfo={}, trade_bn={}".format(mtm,trade_nfo,trade_bank)
            iLog(strMsg,6)  # 6 = Activity/Task done
            
        except Exception as ex:
            strMsg = "check_MTM_Limit(): Trade flags set to false. May be overwritten. Could not update ini file. Ex="+str(ex)
            iLog(strMsg,3)

        iLog("check_MTM_Limit(): MTM {} out of SL or Target range. Squareoff will be triggered for MIS orders...".format(mtm),2,sendTeleMsg=True)

        close_all_orders("ALL")

    return mtm

def get_trade_price_options(bank_nifty,buy_sell,bo_level=1):
    '''Returns the trade price and stop loss abs value for bank/nifty=CRUDE/NIFTY
    buy_sell=BUY/SELL, bo_level or Order execution level = 1(default means last close),2,3 and 0 for close -1 for market order
    '''

    lt_price = 0.0

    # atr = 0
    sl = nifty_sl

    # Refresh the tokens and ltp
    if bank_nifty == "NIFTY_CE" or bank_nifty == "NIFTY_PE":
        get_option_tokens("NIFTY")
    elif bank_nifty == "BANK_CE" or bank_nifty == "BANK_PE":
        get_option_tokens("BANK")

    # 1. Set default limit price, below offset can be parameterised
    if bank_nifty == "NIFTY_CE" :
        lt_price = round(ltp_nifty_ATM_CE) + 2 # Set Default trade price
    elif bank_nifty == "NIFTY_PE" :
        lt_price = round(ltp_nifty_ATM_PE) + 2 # Set Default trade price
    elif bank_nifty == "BANK_CE" :
        lt_price = round(ltp_bank_ATM_CE) + 5
    elif bank_nifty == "BANK_PE" :
        lt_price = round(ltp_bank_ATM_PE) + 5
    else:
        print("get_trade_price_options1",flush=True)
    
    lt_price = float(lt_price)
    print("get_trade_price_options(): lt_price={}".format(lt_price),flush=True)
    
    return lt_price, sl

def trade_limit_reached(bank_nifty="NIFTY"):
    # Check if completed order can work here
    '''Check if number of trades reached/crossed the parameter limit . Return true if reached or crossed else false.
     Dont process the Buy/Sell order if returns true
     bank_nifty=CRUDE/NIFTY '''
    
    trades_cnt = 0  # Number of trades, needs different formula in case of nifty / bank
    buy_cnt = 0
    sell_cnt = 0

    try:
        trade_book = alice.get_trade_book()
        if len(trade_book['data']) == 0 :
            return False        # No Trades
        else:
            trades = trade_book['data']['trades'] #Get all trades
    
    except Exception as ex:
        iLog("trade_limit_reached(): Exception="+ str(ex),3)
        return True     # To be safe in case of exception

    if not trades:
        iLog("trade_limit_reached(): No Trades found for "+ str(bank_nifty))
        return False        # No trades, hence go ahead

    for c_trade in trades:
        if bank_nifty == c_trade['trading_symbol'][:5]:
            if c_trade['transaction_type'] == "BUY" :
                buy_cnt = buy_cnt + 1
            elif c_trade['transaction_type'] == "SELL" :
                 sell_cnt = sell_cnt + 1

    iLog(f"trade_limit_reached(): buy_cnt={buy_cnt}, sell_cnt={sell_cnt}")            
    
    if buy_cnt > sell_cnt:
        trades_cnt = buy_cnt
    else:
        trades_cnt = sell_cnt

    if trades_cnt >= no_of_trades_limit:
        return True
    else:
        return False

def set_config_value(section,key,value):
    '''Set the config file (.ini) value. Applicable for setting only one parameter value. 
    All parameters are string

    section=info/realtime,key,value
    '''
    cfg.set(section,key,value)
    try:
        with open(INI_FILE, 'w') as configfile:
            cfg.write(configfile)
            configfile.close()
    except Exception as ex:
        iLog("Exception writing to config. section={},key={},value={},ex={}".format(section,key,value,ex),2)

def check_trade_time_zone(bank_nifty="NIFTY"):
    result = False

    cur_time = int(datetime.datetime.now().strftime("%H%M"))

    # if bank_nifty=="CRUDE" and (cur_time > curde_trade_start_time and cur_time < curde_trade_end_time) :
    #     result = True

    if bank_nifty=="NIFTY" and (cur_time > nifty_trade_start_time and cur_time < nifty_trade_end_time) :
        result = True

    return result

def get_option_tokens(nifty_bank="ALL"):
    '''This procedure sets the current option tokens to the latest ATM tokens
    nifty_bank="NIFTY" | "BANK" | "ALL"
    '''

    #WIP
    global token_nifty_ce, token_nifty_pe, ins_nifty_ce, ins_nifty_pe, \
        token_bank_ce, token_bank_pe, ins_bank_ce, ins_bank_pe

    expiry_date = datetime.date.today() + datetime.timedelta( (3-datetime.date.today().weekday()) % 7 )

    # Reduce one day if thurshday is a holiday
    if str(expiry_date) in weekly_expiry_holiday_dates :
        expiry_date = expiry_date - datetime.timedelta(days=1)

    # print("expiry_date=",expiry_date,flush=True)
    # print("weekly_expiry_holiday_dates=",weekly_expiry_holiday_dates,flush=True)



    if nifty_bank=="NIFTY" or nifty_bank=="ALL":
        if len(lst_nifty_ltp)>0:
          
            nifty50 = int(lst_nifty_ltp[-1])
            # print("nifty50=",nifty50,flush=True)

            nifty_atm = round(int(nifty50),-2)
            print("nifty_atm=",nifty_atm,flush=True)

            strike_ce = float(nifty_atm - nifty_strike_ce_offset)   #ITM Options
            strike_pe = float(nifty_atm + nifty_strike_pe_offset)


            ins_nifty_ce = alice.get_instrument_for_fno(symbol = 'NIFTY', expiry_date=expiry_date, is_fut=False, strike=strike_ce, is_CE = True)
            ins_nifty_pe = alice.get_instrument_for_fno(symbol = 'NIFTY', expiry_date=expiry_date, is_fut=False, strike=strike_pe, is_CE = False)

            alice.subscribe(ins_nifty_ce, LiveFeedType.COMPACT)
            alice.subscribe(ins_nifty_pe, LiveFeedType.COMPACT)
            
            print("ins_nifty_ce=",ins_nifty_ce,flush=True)
            print("ins_nifty_pe=",ins_nifty_pe,flush=True)

            token_nifty_ce = int(ins_nifty_ce[1])
            token_nifty_pe = int(ins_nifty_pe[1])

            # print("token_nifty_ce=",token_nifty_ce,flush=True)
            # print("token_nifty_pe=",token_nifty_pe,flush=True)

        else:
            print("len(lst_nifty_ltp)=",len(lst_nifty_ltp),flush=True)

    if nifty_bank=="BANK" or nifty_bank=="ALL":
        if len(lst_bank_ltp)>0:
            bank50 = int(lst_bank_ltp[-1])
            # print("Bank50=",bank50,flush=True)

            bank_atm = round(int(bank50),-2)
            print("bank_atm=",bank_atm,flush=True)

            strike_ce = float(bank_atm - bank_strike_ce_offset) #ITM Options
            strike_pe = float(bank_atm + bank_strike_pe_offset)

            ins_bank_ce = alice.get_instrument_for_fno(symbol = 'BANKNIFTY', expiry_date=expiry_date, is_fut=False, strike=strike_ce, is_CE = True)
            ins_bank_pe = alice.get_instrument_for_fno(symbol = 'BANKNIFTY', expiry_date=expiry_date, is_fut=False, strike=strike_pe, is_CE = False)

            alice.subscribe(ins_bank_ce, LiveFeedType.COMPACT)
            alice.subscribe(ins_bank_pe, LiveFeedType.COMPACT)
            
            print("ins_bank_ce=",ins_bank_ce,flush=True)
            print("ins_bank_pe=",ins_bank_pe,flush=True)

            token_bank_ce = int(ins_bank_ce[1])
            token_bank_pe = int(ins_bank_pe[1])

            # print("token_bank_ce=",token_bank_ce,flush=True)
            # print("token_bank_pe=",token_bank_pe,flush=True)

        else:
            print("len(lst_bank_ltp)=",len(lst_bank_ltp),flush=True)

    time.sleep(2)
    
    if nifty_bank=="NIFTY" or nifty_bank=="ALL":
        print("ltp_nifty_ATM_CE=",ltp_nifty_ATM_CE,flush=True)
        print("ltp_nifty_ATM_PE=",ltp_nifty_ATM_PE,flush=True)        
    
    if nifty_bank=="BANK" or nifty_bank=="ALL":
        print("ltp_bank_ATM_CE=",ltp_bank_ATM_CE,flush=True)
        print("ltp_bank_ATM_PE=",ltp_bank_ATM_PE,flush=True)  

def check_orders():
    ''' 1. Checks for pending SL orders and update/maintain local sl order dict 
        2. Updates SL order to target price if reached
        2.1 Update SL order target price to TSL
    '''
    iLog("In check_orders()")   # can be disabled later to reduce logging  

    #1 Remove completed orders/keep only pending orders from the SL orders dict
    try:
        orders = alice.get_order_history()['data']['pending_orders']
        if orders:
        # loop through Sl orders dict and check if current price has exceeded target price
            for key, value in dict_sl_orders.items():
                order_found = False
                for order in orders:
                    if key == order['oms_order_id']:
                        order_found = True
                        break
                
                # remove the order from sl dict which is not pending
                if not order_found:
                    dict_sl_orders.pop(key)
                    iLog(f"In check_orders(): Removed order {key} from dict_sl_orders")
        
        else:
            dict_sl_orders.clear()
        
    except:
        pass
    
    print("dict_sl_orders=",dict_sl_orders,Flush=True)
    print("dict_ltp=",dict_ltp,Flush=True)

    #2. Check the current price of the SL orders and if they are above tgt modify them to target price
    # dict_sl_orders => key=order ID : value = [0-token, 1-target price, 2-instrument]
    for oms_order_id, value in dict_sl_orders.items():
        #Set Target Price : current ltp > target price
        if float(dict_ltp[value[0]]) > float(value[1]) :
            try:
                alice.modify_order(TransactionType.Sell,value[2],ProductType.Intraday,oms_order_id,OrderType.Limit,price=float(value[1]))
                iLog(f"In check_orders(): Target price for OrderID {oms_order_id} modified to {value[1]}")
            
            except Exception as ex:
                iLog("In check_orders(): Exception occured during Target price modification = " + str(ex),3)

        #Set Target Price to Training SL
        # Need nifty / banknift identificaiton        
        elif float(dict_ltp[value[0]]) < float(value[1] - bank_tsl):
            tsl_price = float(value[1] - bank_tsl)
            try:
                alice.modify_order(TransactionType.Sell,value[2],ProductType.Intraday,oms_order_id,OrderType.Limit,price=tsl_price )
                iLog(f"In check_orders(): TSL for OrderID {oms_order_id} modified to {tsl_price}")
            
            except Exception as ex:
                iLog("In check_orders(): Exception occured during TSL modification = " + str(ex),3)


########################################################################
#       Events
########################################################################
def event_handler_quote_update(message):
    global dict_ltp, lst_bank_ltp,ltp_bank_ATM_CE,ltp_bank_ATM_PE, lst_nifty_ltp, ltp_nifty_ATM_CE, ltp_nifty_ATM_PE

    # if(message['exchange']=='MCX'): 
    #     lst_bank_ltp.append(message['ltp'])
    # print("message['token'],token_nifty_ce",message['token'],token_nifty_ce)
    if(message['token']==token_nifty_ce):
        ltp_nifty_ATM_CE=message['ltp']

    if(message['token']==token_nifty_pe):
        ltp_nifty_ATM_PE=message['ltp']

    if(message['token']==token_bank_ce):
        ltp_bank_ATM_CE=message['ltp']

    if(message['token']==token_bank_pe):
        ltp_bank_ATM_PE=message['ltp']


    #For Nifty 50, token number should ideally not change
    if(message['token']==26000):
        lst_nifty_ltp.append(message['ltp'])

    #For BankNifty 50,
    if(message['token']==26009):
        lst_bank_ltp.append(message['ltp'])

    #Update the ltp for all the tokens
    dict_ltp.update({message['token']:message['ltp']})

def open_callback():
    global socket_opened
    socket_opened = True
    iLog("In open_callback().")
    # Call the instrument subscription, Hope this will resolve the tick discontinuation issue
    subscribe_ins()   # 2020-08-13 moving this to main call
    # 2020-08-14 Didnt worked So upgraded the alice_blue package. Lets observe on monday 
    #

def error_callback(error):
    iLog("In error_callback(). {}".format(error),3)
  
def close_callback():
    iLog("In close_callback().")


# Main program starts from here...
iLog("User = " + susername)
#print(str(datetime.datetime.now().strftime("%H:%M:%S")) + ' : '+susername,flush=True)

# Get access token
access_token = getAccessToken(INI_FILE=INI_FILE)
# print("access_token",access_token)
if access_token=="-1": exit()
 
# Connect to AliceBlue and download contracts
alice = AliceBlue(username=susername, password=spassword, access_token=access_token, master_contracts_to_download=['NFO','NSE'])

ins_nifty = alice.get_instrument_by_symbol('NSE', 'Nifty 50')
ins_bank = alice.get_instrument_by_symbol('NSE', 'Nifty Bank')
# ins_nifty = alice.get_instrument_by_symbol('NFO', nifty_symbol)
# ins_nifty50 = alice.get_instrument_by_symbol('NSE', 'Nifty 50')     #Instead of futures get Nifty 50 Index price 
#ins_bank = alice.get_instrument_by_symbol('MCX', bank_symbol)

#Temp assignment for CE/PE instrument tokens
ins_nifty_ce = ins_nifty
ins_nifty_pe = ins_nifty
ins_nifty_opt = ins_nifty

ins_bank_ce = ins_bank
ins_bank_pe = ins_bank
ins_bank_opt = ins_bank


# Code Test area, can be above access_token generation if testing under maintenance window.
# sell_bank("Testing")
# buy_nifty("test")
# close_all_orders('NIFTY')
# iLog("Testing Done..")
# exit()

# Start Websocket
strMsg = "Starting Websocket."
iLog(strMsg,sendTeleMsg=True)
alice.start_websocket(subscribe_callback=event_handler_quote_update,
                      socket_open_callback=open_callback,
                      socket_close_callback=close_callback,
                      socket_error_callback=error_callback,
                      run_in_background=True)

# Check with Websocket open status
while(socket_opened==False):
    pass



# # Get instrument of Nifty ATM Option
# ins_nifty50 = alice.get_instrument_by_symbol('NSE', 'Nifty 50')     #Instead of futures get Nifty 50 Index price 
# print(ins_nifty50,flush=True)
# alice.subscribe(ins_nifty50, LiveFeedType.COMPACT)
time.sleep(2)


get_option_tokens("ALL")

# ins_options = []
# ins_options.append(ins_nifty_ce)
# ins_options.append(ins_nifty_pe)

# print("Before Subscribe")
# alice.subscribe(ins_options, LiveFeedType.COMPACT)
# print("After Subscribe")
# print("Done.")
# exit()


strMsg = "Starting tick processing."
iLog(strMsg,sendTeleMsg=True)



# Process tick data/indicators and generate buy/sell and execute orders
while True:
    # Process as per start of market timing
    cur_HHMM = int(datetime.datetime.now().strftime("%H%M"))
    # print("cur_HHMM=",cur_HHMM,flush=True)

    if cur_HHMM > 914:

        cur_min = datetime.datetime.now().minute 

        # Below if block will run after every time interval specifie in the .ini file
        if( cur_min % interval == 0 and flg_min != cur_min):

            flg_min = cur_min     # Set the minute flag to run the code only once post the interval
            t1 = time.time()      # Set timer to record the processing time of all the indicators
            
            # Can include the below code to work in debug mode only
            strMsg = "BN=" + str(len(lst_bank_ltp))
            # if len(df_bank.index) > 0 : strMsg = strMsg + " "+str(df_bank.close.iloc[-1]) 

            strMsg = strMsg +  " N="+ str(len(lst_nifty_ltp))
            # if len(df_nifty.index) > 0 : strMsg = strMsg + " "+str(df_nifty.close.iloc[-1]) 


            # Check MTM and stop trading if limit reached; This can be parameterised to % gain/loss
            MTM = check_MTM_Limit()
           
            
            if len(lst_bank_ltp) > 1:    #BANKNIFTY Candle
                tmp_lst = lst_bank_ltp.copy()  #Copy the ticks to a temp list
                lst_bank_ltp.clear()           #reset the ticks list; There can be gap in the ticks during this step ???
                #print(f"CRUDE: cur_min = {cur_min},len(tmp_lst)={len(tmp_lst)},i={i}",flush=True)
                #Formation of candle
                df_bank.loc[df_bank_cnt, df_cols]=[cur_HHMM, tmp_lst[0], max(tmp_lst), min(tmp_lst), tmp_lst[-1],"",0]
                df_bank_cnt = df_bank_cnt + 1 
                # open = df_bank.close.tail(3).head(1)  # First value  
                flg_med_bank = 0
                strMsg = strMsg + " " + str(tmp_lst[-1])      #Crude close 

                if cur_min % 6 == 0 :
                    df_bank_med.loc[df_bank_med_cnt,df_cols] = [cur_HHMM, df_bank.open.tail(3).head(1).iloc[0], df_bank.high.tail(3).max(), df_bank.low.tail(3).min(), df_bank.close.iloc[-1], "",0 ] 
                    df_bank_med_cnt = df_bank_med_cnt + 1
                    # print(df_bank_med,flush=True )
                    flg_med_bank = 1
                    
            if len(lst_nifty_ltp) > 1: #and cur_HHMM > 914 and cur_HHMM < 1531:    #Nifty Candle
                tmp_lst = lst_nifty_ltp.copy()  #Copy the ticks to a temp list
                lst_nifty_ltp.clear()           #reset the ticks list
                # print(f"NIFTY: cur_min = {cur_min},len(tmp_lst)={len(tmp_lst)}",flush=True)
                # Formation of candle
                df_nifty.loc[df_nifty_cnt,df_cols] = [cur_HHMM,tmp_lst[0],max(tmp_lst),min(tmp_lst),tmp_lst[-1],"",0]
                df_nifty_cnt = df_nifty_cnt + 1
                flg_med_nifty = 0
                strMsg = strMsg + " " + str(tmp_lst[-1])      #Nifty close

                if cur_min % 6 == 0 :
                    df_nifty_med.loc[df_nifty_med_cnt,df_cols] = [cur_HHMM, df_nifty.open.tail(3).head(1).iloc[0], df_nifty.high.tail(3).max(), df_nifty.low.tail(3).min(), df_nifty.close.iloc[-1], "", 0] 
                    df_nifty_med_cnt = df_nifty_med_cnt + 1
                    # print(df_nifty_med,flush=True )
                    flg_med_nifty = 1   # Used to check in the medium ST signal for consecutive orders

            # Get realtime config changes from ab.ini file and reload variables
            get_realtime_config()

            strMsg = strMsg + " POS="+ str(pos_nifty)  + " MTM=" + str(MTM)

            iLog(strMsg,sendTeleMsg=True)

            # #######################################
            #           BANKNIFTY Order Generation
            # #######################################
            if df_bank_cnt > 6 and cur_HHMM > 914 and cur_HHMM < 1531:        # Calculate Nifty indicators and call buy/sell

                SuperTrend(df_bank)                    # Low level (2/3min) timeframe calculations
                RSI(df_bank,period=7)                 # RSI Calculations
                super_trend_bank = df_bank.STX.values     # Get ST values into a list
                SuperTrend(df_bank_med)                # Medium level (6min) timeframe calculations

                strMsg="BankNifty: #={}, ST_LOW={}, ST_LOW_SL={}, ATR={}, ST_MED={}, ST_MED_SL={}, ltp_bank_ATM_CE={}, ltp_bank_ATM_PE={}".format(df_bank_cnt, super_trend_bank[-1], round(df_bank.ST.iloc[-1]), round(df_bank.ATR.iloc[-1],1), df_bank_med.STX.iloc[-1], round(df_bank_med.ST.iloc[-1]), ltp_bank_ATM_CE, ltp_bank_ATM_PE)
                iLog(strMsg)

                # -- ST LOW
                #--BUY---BUY---BUY---BUY---BUY---BUY---BUY---BUY---BUY---BUY
                if super_trend_bank[-1]=='up' and super_trend_bank[-2]=='down' and super_trend_bank[-3]=='down' and super_trend_bank[-4]=='down' and super_trend_bank[-5]=='down' and super_trend_bank[-6]=='down':
                    #Buy only if both medium and lower ST is in buy zone
                    if df_bank_med.STX.iloc[-1] == 'down':
                        strMsg = "BANK ST=up, ST_MEDIUM=down. Sell order to be placed - Deactivated. Closing existing Bank positions."
                        iLog(strMsg,sendTeleMsg=True)
                        close_all_orders("BANK")
                    else:   # ST_MEDIUM=='up'
                        strMsg = "BANK ST=up, ST_MEDIUM=up. CE Buy Order to be placed. "
                        iLog(strMsg,sendTeleMsg=True)
                        buy_bank_options("BANK_CE")
      

                # -- ST LOW        
                #---SELL---SELL---SELL---SELL---SELL---SELL---SELL---SELL---SELL        
                elif super_trend_bank[-1]=='down' and super_trend_bank[-2]=='up' and super_trend_bank[-3]=='up' and super_trend_bank[-4]=='up' and super_trend_bank[-5]=='up' and super_trend_bank[-6]=='up':
                    #Sell only if both medium and lower ST is in sell zone
                    if df_bank_med.STX.iloc[-1] == 'up':
                        strMsg = "BANK ST=down, ST_MEDIUM=up. Buy Order to be placed - Deactivated. Closing existing Bank positions."
                        iLog(strMsg,sendTeleMsg=True)
                        # buy_nifty(strMsg)
                        close_all_orders("BANK")
                    else:
                        strMsg = "BANK ST=down, ST_MEDIUM=down. PE Buy Order to be placed. "
                        iLog(strMsg,sendTeleMsg=True)
                        buy_bank_options("BANK_PE")
      

                # ST MEDIUM
                #--BUY---BUY---BUY
                elif df_bank_med.STX.iloc[-1]=='up' and df_bank_med.STX.iloc[-2]=='down' and df_bank_med.STX.iloc[-3]=='down' and df_bank_med.STX.iloc[-4]=='down':
                    # Ensure both are in same direction
                    if super_trend_bank[-1] == 'up':
                        if flg_med_bank :
                            strMsg = "BANK ST_MEDIUM=up, ST=up. CE Buy Order to be placed. "
                            iLog(strMsg,sendTeleMsg=True)
                            # buy_bank(strMsg)
                            buy_bank_options("BANK_CE")
                        else:
                            iLog("BANK ST_MEDIUM=up, ST=up. Consecutive bank buy order skipped.")


                    else:
                        strMsg="BANK ST_MEDIUM=up, ST=down. Buy not triggered. Need Investigation."
                        iLog(strMsg,sendTeleMsg=True)

                #---SELL---SELL---SELL
                elif df_bank_med.STX.iloc[-1]=='down' and df_bank_med.STX.iloc[-2]=='up' and df_bank_med.STX.iloc[-3]=='up' and df_bank_med.STX.iloc[-4]=='up':
                    # Ensure both are in same direction
                    if super_trend_bank[-1] == 'down':
                        if flg_med_bank :
                            strMsg = "BANK ST_MEDIUM=down, ST=down. PE Buy Order to be placed. "
                            # sell_bank(strMsg)
                            buy_bank_options("BANK_PE")
                        else:
                            iLog("BANK ST_MEDIUM=down, ST=down. Consecutive BANK SELL order skipped.")

                    else:
                        strMsg = "BANK ST_MEDIUM=down, ST=up. Sell not triggered. Need Investigation."
                        iLog(strMsg,sendTeleMsg=True)


      
      
            # Nifty - Only 5 ST values checked in condition as compared to bank
            # ////////////////////////////////////////
            #           NIFTY Order Generation
            # ////////////////////////////////////////
            if df_nifty_cnt > 6 and cur_HHMM > 914 and cur_HHMM < 1531:        # Calculate Nifty indicators and call buy/sell

                SuperTrend(df_nifty)                    # Low level (2/3min) timeframe calculations
                RSI(df_nifty,period=7)                 # RSI Calculations
                super_trend_nifty = df_nifty.STX.values     # Get ST values into a list
                SuperTrend(df_nifty_med)                # Medium level (6min) timeframe calculations

                strMsg="Nifty: #={}, ST_LOW={}, ST_LOW_SL={}, ATR={}, ST_MED={}, ST_MED_SL={}, ltp_nifty_ATM_CE={}, ltp_nifty_ATM_PE={}".format(df_nifty_cnt, super_trend_nifty[-1], round(df_nifty.ST.iloc[-1]), round(df_nifty.ATR.iloc[-1],1), df_nifty_med.STX.iloc[-1], round(df_nifty_med.ST.iloc[-1]), ltp_nifty_ATM_CE, ltp_nifty_ATM_PE)
                iLog(strMsg)

                # -- ST LOW
                #--BUY---BUY---BUY---BUY---BUY---BUY---BUY---BUY---BUY---BUY
                if super_trend_nifty[-1]=='up' and super_trend_nifty[-2]=='down' and super_trend_nifty[-3]=='down' and super_trend_nifty[-4]=='down' and super_trend_nifty[-5]=='down' and super_trend_nifty[-6]=='down':
                    #print("Nifty close=",df_nifty.close.iloc[-1],flush=True)
                    #print("RSI[-1]=",df_nifty.RSI.iloc[-1],flush=True)
                    #Buy only if both medium and lower ST is in buy zone
                    if df_nifty_med.STX.iloc[-1] == 'down':
                        strMsg = "NIFTY ST=up, ST_MEDIUM=down. Sell order to be placed - Deactivated. Closing existing Nifty positions."
                        iLog(strMsg,sendTeleMsg=True)
                        close_all_orders("NIFTY")
                    else:   # ST_MEDIUM=='up'
                        strMsg = "NIFTY ST=up, ST_MEDIUM=up. CE Buy Order to be placed. "
                        iLog(strMsg,sendTeleMsg=True)
                        buy_nifty_options("NIFTY_CE")
                        # sell_nifty(strMsg)
                        # Experiment
                        # Buy 
                    # elif df_nifty.RSI.iloc[-1] > rsi_buy_param and df_nifty.RSI.iloc[-1] < rsi_sell_param:

                    #     c1 = round((df_nifty.RSI.iloc[-2] - df_nifty.RSI.iloc[-3]) / df_nifty.RSI.iloc[-3], 3 )
                    #     c2 = round((df_nifty.RSI.iloc[-1] - df_nifty.RSI.iloc[-2]) / df_nifty.RSI.iloc[-2], 3 )

                    #     iLog("NIFTY ST=up - RSI Rate of change c2(latest)={},c1(previous)={}".format(c2,c1))
                    #     if c2 > c1: #percent Rate of change is increasing 
                    #         strMsg = "NIFTY ST=up, RSI BUY=" + str(df_nifty.RSI.iloc[-1])
                    #         # buy_nifty(strMsg)
                    #         buy_nifty_options("NIFTY_CE")
                    #     else:
                    #         strMsg = "NIFTY ST=up - RSI Rate of change not as per trend"
                    #         iLog(strMsg,sendTeleMsg=True)
                    # else:
                    #     strMsg = "NIFTY ST=up, close=" + str(df_nifty.close.iloc[-1]) + ", RSI NOBUY=" + str(df_nifty.RSI.iloc[-1])    
                    #     iLog(strMsg,sendTeleMsg=True)

                # -- ST LOW        
                #---SELL---SELL---SELL---SELL---SELL---SELL---SELL---SELL---SELL        
                elif super_trend_nifty[-1]=='down' and super_trend_nifty[-2]=='up' and super_trend_nifty[-3]=='up' and super_trend_nifty[-4]=='up' and super_trend_nifty[-5]=='up' and super_trend_nifty[-6]=='up':
                    #Sell only if both medium and lower ST is in sell zone
                    if df_nifty_med.STX.iloc[-1] == 'up':
                        strMsg = "NIFTY ST=down, ST_MEDIUM='up'. Buy Order to be placed - Deactivated. Closing existing Nifty positions."
                        iLog(strMsg,sendTeleMsg=True)
                        # buy_nifty(strMsg)
                        close_all_orders("NIFTY")
                    else:
                        strMsg = "NIFTY ST=down, ST_MEDIUM=down. PE Buy Order to be placed. "
                        iLog(strMsg,sendTeleMsg=True)
                        buy_nifty_options("NIFTY_PE")
                    # elif df_nifty.RSI.iloc[-1] < rsi_sell_param and df_nifty.RSI.iloc[-1] > rsi_buy_param:
                        
                    #     c1 = round( ( df_nifty.RSI.iloc[-2] - df_nifty.RSI.iloc[-3] ) / df_nifty.RSI.iloc[-3] , 3 )
                    #     c2 = round( ( df_nifty.RSI.iloc[-1] - df_nifty.RSI.iloc[-2] ) / df_nifty.RSI.iloc[-2] , 3 )
                        
                    #     iLog("NIFTY ST=down - RSI Rate of change c2(latest)={},c1(previous)={}".format(c2,c1))
                        
                    #     if c2 < c1: # percent Rate of change is decreasing
                    #         strMsg = "NIFTY ST=down, RSI SELL=" + str(df_nifty.RSI.iloc[-1])
                    #         # sell_nifty(strMsg)
                    #         buy_nifty_options("NIFTY_PE")
                    #     else:
                    #         strMsg = "NIFTY ST=down - RSI Rate of change not as per trend"
                    #         iLog(strMsg,sendTeleMsg=True)
                    # else:
                    #     strMsg = "NIFTY ST=down close=" + str(df_nifty.close.iloc[-1]) +", RSI NOSELL=" + str(df_nifty.RSI.iloc[-1])   
                    #     iLog(strMsg,sendTeleMsg=True)

                # ST MEDIUM
                #--BUY---BUY---BUY
                elif df_nifty_med.STX.iloc[-1]=='up' and df_nifty_med.STX.iloc[-2]=='down' and df_nifty_med.STX.iloc[-3]=='down' and df_nifty_med.STX.iloc[-4]=='down':
                    # Ensure both are in same direction
                    if super_trend_nifty[-1] == 'up':
                        if flg_med_nifty :
                            strMsg = "NIFTY ST_MEDIUM=up, ST=up. CE Buy Order to be placed. "
                            # buy_nifty(strMsg)
                            buy_nifty_options("NIFTY_CE")
                        else:
                            iLog("NIFTY ST_MEDIUM=up, ST=up. Consecutive nifty buy order skipped.")


                    else:
                        strMsg="NIFTY ST_MEDIUM=up, ST=down. Buy not triggered. Need Investigation."
                        iLog(strMsg,sendTeleMsg=True)

                #---SELL---SELL---SELL
                elif df_nifty_med.STX.iloc[-1]=='down' and df_nifty_med.STX.iloc[-2]=='up' and df_nifty_med.STX.iloc[-3]=='up' and df_nifty_med.STX.iloc[-4]=='up':
                    # Ensure both are in same direction
                    if super_trend_nifty[-1] == 'down':
                        if flg_med_nifty :
                            strMsg = "NIFTY ST_MEDIUM=down, ST=down. PE Buy Order to be placed. "
                            # sell_nifty(strMsg)
                            buy_nifty_options("NIFTY_PE")
                        else:
                            iLog("NIFTY ST_MEDIUM=down, ST=down. Consecutive Nifty SELL order skipped.")

                    else:
                        strMsg = "NIFTY ST_MEDIUM=down, ST=up. Sell not triggered. Need Investigation."
                        iLog(strMsg,sendTeleMsg=True)


            #-- Find processing time and Log only if processing takes more than 2 seconds
            t2 = time.time() - t1
            if t2 > 2.0: 
                strMsg="Processing time(secs)= {0:.2f}".format(t2)
                iLog(strMsg,2)

            #-- Export data on demand
            if export_data:     
                savedata(False)     # Export dataframe data, both bank and nifty
                export_data = 0     # Reset config value to 0 in both file and variable
                set_config_value("realtime","export_data","0")


            #-- Cancel Nifty open orders, reset flags save data
            if cur_HHMM > nifty_sqoff_time and not processNiftyEOD: 
                close_all_orders()
                processNiftyEOD = True    # Set this flag so that we don not repeatedely process this
 

        if cur_HHMM > 1530 and cur_HHMM < 1532 :   # Exit the program post NSE closure
            # Reset trading flag for bank if bank is enabled on the instance
            if enable_bank : 
                iLog("Enabling BankNifty trading...")
                set_config_value("realtime","trade_bn","1")
            
            # Reset trading flag for nifty if nifty is enabled on the instance
            if enable_NFO : 
                iLog("Enabling NFO trading...")
                set_config_value("realtime","trade_nfo","1")
        
            savedata()      # Export dataframe data, both 
            iLog("Shutter down... Calling sys.exit() @ " + str(cur_HHMM),sendTeleMsg=True)
            sys.exit()
   

            
            # #-- Cancel all open Crude orders after 11:10 PM, time can be parameterised
            # if cur_HHMM > bank_sqoff_time and not processCrudeEOD:
            #     close_all_orders('CRUDE')
            #     processCrudeEOD = True

           
            #-- Check if any open order greater than pending_ord_limit_mins and cancel the same 
            close_all_orders(ord_open_time=pending_ord_limit_mins)

    time.sleep(9)   # May be reduced to accomodate the processing delay

    check_orders()  # Checks SL orders and sets target, should be called every 10 seconds. check logs



''' For async run Option 1 
from multiprocessing import Process

def func1():
  print 'func1: starting'
  for i in xrange(10000000): pass
  print 'func1: finishing'

def func2():
  print 'func2: starting'
  for i in xrange(10000000): pass
  print 'func2: finishing'

if __name__ == '__main__':
  p1 = Process(target=func1)
  p1.start()
  p2 = Process(target=func2)
  p2.start()
  p1.join()
  p2.join()
'''

''' For async run Option 2 
import threading
 import time

 def useless_function(seconds):
     print(f'Waiting for {seconds} second(s)', end = "\n")
     time.sleep(seconds)
     print(f'Done Waiting {seconds}  second(s)')

 start = time.perf_counter()
 t = threading.Thread(target=useless_function, args=[1])
 t.start()
 print(f'Active Threads: {threading.active_count()}')
 t.join()
 end = time.perf_counter()
 print(f'Finished in {round(end-start, 2)} second(s)') 
'''