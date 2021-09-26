# pylint: disable=unused-wildcard-import
# v1.1 Added new column "signal", changed df_cols and reset again, 
# v1.2 Disabled Opening range breakout code, blank initiation of signal column value (as .at was giving float conversion error)
# v1.3 Added parameterization of qty
# v1.3 Premarket trade procedure and logic added
# v1.4 getMTM and check_MTM_Limit() merged into one
# v1.5 Exception handling in savedata(), close_all_orders(), counters for df_nifty and crude implemented,
#       df_crude_med created and data captured
# v1.6 df_nifty_med created and data captured, updated savedata() 
# v1.7 Implemented df_crude_med and df_nifty_med in both buy and sell logic
# v1.8 premarket_tarde(): enabled BO2 condition
# v1.9 Fixed Tele() issue, added premarket_flag
# v2.0 Processing time limit changed to 2 seconds; changed medium level df interval logic, cur_min used
# v2.1 Enabled Telegram notification in premarket_tarde()
# v2.2 Interval set to 3 min in ab.ini and counter trade taken 
# v2.3 Premarket trade condition check. Gap of 50 pts and above, premarket will not trigger
#       Saving datafilename with Savedata(). Reading previous 10 period data for nifty at the start
# v2.4 Changed BO2 lt_price to be offset by half of ATR both buy/sell crude/nifty
# v2.5 Updated if condition for adding nifty dataframe rows. Added time check as blank rows were going into df.
# v2.6 nifty_sl set to ST(SuperTrend price)+3 in buy_nifty() and sell_nifty()
# v2.7 ST buy/Sell logic implemented using nifty_med ST as well
# v2.8 Fixed ST_Medium buy/sell not getting triggered. wrong dataframe name used. copy/paste miss.
#       implemented ST crude_med buy/Sell option, Fix incorrect SL issue in case of medium timeframe override for nifty only. 
#       It was taking low timeframe ST for calculating value of SL which was comming negative and huge.
# v2.9 Pending - crude override trade price and sl logic 
# v3.0 Fixed crude medium ST Sell calling buy_nifty
# v3.1 Added bot_token and ChatID for parameterising telegram bot and chat options
# v3.2 Enable BO3 for Nifty 
# v3.3 buy/sell cancellation handled in close_all_orders(), enable_MCX, enable_NFO implemented
# v3.4 savedata() - Included parameter to update datafilename in the .ini file
# v3.5 Merged iLog() and Tele() functions
# v3.6 get_trade_price() in nifty buy/sell
# v3.7 SL added in the df_nifty for offline MTM calculations
# v3.8 added cur_HHMM > 914 in nifty df and order execution code other optimisations in buy/sell nifty/crude
# v3.9 check_pending_orders() implemented in buy/sell nifty/crude before order execution
# v4.0 trade_limit_reached() implemented in buy/sell nifty/crude
# v4.1 deactivated ST_MEDIUM counter trade execution
# v4.2 ab_lib.update_contract_symbol() implemented, get_trade_price() in crude buy/sell
#       SL added in the df_nifty for offline MTM calculations
# v4.3 enableNFO while reading previous day datafile, logging post check_pending_orders() invocation in buy/sell
# v4.4 Set initial sleep time to match the crude market opening time of 9:00 AM to avoid previous junk values
#       check_pending_orders() and cancellation implementation changes in nifty/crude buy/sell 
#       trade_limit_reached() moved before check_pending_orders(). Need to check if this is the correct approach
# v4.5 Fixed TypeError on init_sleep_seconds. Added CRUDE previous data load functionality. Updated savedata() for crude 
# v4.6 Fixed NameError: name 'ilog' is not defined in trade_limit_reached()
# v4.7 check_pending_orders not required as if there are no position we would need to close all open/pending orders and 
#       initiate fresh buy/sell orders. Hence, close_all_orders() call in nifty/crude buy/sell.
#       get_trade_price - Changed the SL to df_med.ST due to SL hits (4-Aug-2020)  
# v4.8 Consecutive order execution due to ST_Medium fixed.
# v4.9 reverted the v4.7 changes of get_trade_price(), parameterised dl_buffer
# v5.0 Fixed the v4.8 issue as it was not solved by the min flag 
#       Crude/Nifty position updated in check_MTM_Limit() and used in buy/sell nifty/crude()
#       close_pend_ord_post_interval parameter implementation WIP (Cancelled)
# v5.1 close_pend_ord_post_interval changed to pending_ord_limit_mins
#       Implemented cancellation of open orders after n mins in close_all_orders(). This funciton needs to be called every ineterval with ord_open_time>0 from parameter
# v5.2 WebSocket disconnection and subscription/tick loss issue. Upgraded the package 
#       enabled MIS orders apart from previous only BO orders. configurable in ab.ini. Nifty default to BO and Crude default to MIS 
# v5.3 BUG: Fixed reload of updated nifty contract symbol from ab.ini file
# v5.4 get_trade_price(); Ignore ATR addition to lt price if TR is very high (>25); can be parameterised. 
# v5.5 1.Changed reading previous 10 period data to 40 as ATR and ST calculation were not carrying over. ST up changed to down
#       2.For MIS nifty/crude buy/sell, squareoff handled by doubling the ord qty
#       3.Created squareOff_MIS() to handle CRUDE/Nifty MIS Eod position closure and exit position when mtm limit is reached
# v5.6  check_MTM_Limit() updated to keep a SL order at previous open/close instead of market squreoff to get the benefit of one way rally.
#       can check for implementation of trailing SL (update the last order) 
# v5.7  MIS order placing changed to Market orders as partial orders were remaining pending and later cancelled.
#       get_trade_price(): bo_level 0 option added to have market order option in Nifty BO
# v5.8  get_trade_price(): bo_level -1 for market and 0 for last close 
# v5.9  reset trade flags(mcx,nfo) to 1 at EOD crude i.e post 11:30 pm ist 
# v6.0  fixed BUG: error in reading enable_NFO_data 
# v6.1  added and implemented additional parameters for nifty/crude bo execution level -1,0,1,2,3...
# v6.2  fixed (while reading ab.ini) int conversion bug because of the above change
# v6.3  parameterised sl in get_trade_price()
# v6.4  warnings set at buy/sell logging calls. mtm limits,lmt ord strategy level moved to realtime procedure. 
#       commented get_position() method(can be removed later) as position is derived in the check_mtm_limit() method. 
# v6.5.1  check_trade_time_zone() implemented; Check_mtm_limit(): mtm value printed while calling ilog
# v6.6.2  close_all_orders() updated to inlude MIS Square offs. Implemented in ST_MED counter signals.
#       print calculated SL in get_trade_price()
#       Fixed typo error in calling iLog (was calling ilog) L vs l )  
# v6.6.3 Removed dead code, get position proc
# v6.7  get_trade_price(): removed multiplication with 0.5 and updated the effected code. Multiplication factor to be set in bo_level
# v6.8  check_MTM_limit(): Changes made to fix non saving of tradeflag into the ab.ini file.      
# v6.9  get_trade_price(): changed the SL calcuation to consider only ST_Med. sl_buffer may need to be reduced or made 0 or negative values. 
#       Consider seperate sl_buffer for nifty and crude
# v6.9.1 Changed logging of ticks and close in the main while loop
# v6.9.2 Implemented try block in subscribe_ins(), INI_FILE variable
# v6.9.3 mcx_trade_start_time implemented in .ini and in code.
# v6.9.4 condition added to Exit the program post NSE closure

# bg process
# 2020-09-01 09:59:18.152555|1|chat_id=670221062 text=Cmd ls
# exception= list index out of range
# 2020-09-01 10:00:18.565516|1|chat_id= text=Cmd ls
# exception= list index out of range

# Open issues/tasks:
# Consider seperate sl_buffer for nifty and crude in get_trade_price()
# Check if order parameters like order type and others can be paramterised
# Look at close pending orders, my not be efficient, exception handling and all
# WebSocket disconnection and subscription/tick loss issue. Upgraded the package  
# Option of MIS orders for CRUDE to be added, maybe for nifty as well. Can test with nifty 
# check_MTM_Limit() limitation : if other nifty or crude scrips are traded this will messup the position
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
# NSE Premarket method values may not be current as crude open time is considered . Need to fetch this realtime around 915 
# May need try/catch in reading previous day datafile due to copy of ini file or failed runs
# Can look at frequency of data export through parameter, say 60,120,240 etc.. 

# Guidelines:
# TSL to be double of SL (Otherwise mostly SLs are hit as they tend to )
# SL will be hit in high volatility. SL may be set to ATR*3 or medium df Supertrend Value
# Always buy market, in case SL reverse and get out cost to cost. Market has to come up.  
# SLs are usually hit in non volatile market, so see if you can use less qty and no SLs, especially crude.
# Dont go against the trend in any case. 
# Avoid manual trades

# Manual running of program
# python3 ab.py &

import ab_lib
from ab_lib import *
import sys
import time

# Reduce position to cut loss if price is going against the trade, can close BO1

# Manual Activities
# Frequency - Monthly , Change Symbol of nifty/crude in ab.ini

# Enable logging to file 
sys.stdout = sys.stderr = open(r"./log/ab_" + datetime.datetime.now().strftime("%Y%m%d") +".log" , "a")


######################################
#       Initialise variables
######################################
INI_FILE = "ab.ini"              # Set .ini file name used for storing confi info.
# Load parameters from the config file
cfg = configparser.ConfigParser()
cfg.read(INI_FILE)

# Set user profile; Access token and other user specific info from ab.ini will be pulled from this section
ab_lib.strChatID = cfg.get("tokens", "chat_id")
ab_lib.strBotToken = cfg.get("tokens", "bot_token")    #Bot include bot prefix in the token
strMsg = "Initialising " + __file__
iLog(strMsg,sendTeleMsg=True)

# crontabed this at 9.00 am instead of 8.59
# Set initial sleep time to match the crude market opening time of 9:00 AM to avoid previous junk values
init_sleep_seconds = int(cfg.get("info", "init_sleep_seconds"))
strMsg = "Setting up initial sleep time of " + str(init_sleep_seconds) + " seconds."
iLog(strMsg,sendTeleMsg=True)
time.sleep(init_sleep_seconds)

susername = cfg.get("tokens", "uid")
spassword = cfg.get("tokens", "pwd")

# Realtime variables also loaded in get_realtime_config()
enableBO2_nifty = int(cfg.get("realtime", "enableBO2_nifty"))   # True = 1 (or non zero) False=0 
enableBO3_nifty = int(cfg.get("realtime", "enableBO3_nifty"))   # True = 1 (or non zero) False=0 
enableBO2_crude = int(cfg.get("realtime", "enableBO2_crude"))   # True = 1 (or non zero) False=0 
enableBO3_crude = int(cfg.get("realtime", "enableBO3_crude"))   # True = 1 (or non zero) False=0 
tradeNFO = int(cfg.get("realtime", "tradeNFO"))                 # True = 1 (or non zero) False=0
tradeMCX = int(cfg.get("realtime", "tradeMCX"))                 # True = 1 (or non zero) False=0
nifty_sl = float(cfg.get("realtime", "nifty_sl"))               #20.0
crude_sl = float(cfg.get("realtime", "crude_sl"))               #15.0
mtm_sl = int(cfg.get("realtime", "mtm_sl"))                     #amount below which program exit all positions 
mtm_target = int(cfg.get("realtime", "mtm_target"))             #amount above which program exit all positions and not take new positions
nifty_bo1_qty = int(cfg.get("realtime", "nifty_bo1_qty"))
nifty_bo2_qty = int(cfg.get("realtime", "nifty_bo2_qty"))
nifty_bo3_qty = int(cfg.get("realtime", "nifty_bo3_qty"))
crude_bo1_qty = int(cfg.get("realtime", "crude_bo1_qty"))
crude_bo2_qty = int(cfg.get("realtime", "crude_bo2_qty"))
crude_bo3_qty = int(cfg.get("realtime", "crude_bo3_qty"))
sl_buffer = int(cfg.get("realtime", "sl_buffer"))
nifty_ord_type = cfg.get("realtime", "nifty_ord_type")      # BO / MIS
crude_ord_type = cfg.get("realtime", "crude_ord_type")      # MIS / BO
# atr * level * 0.5 (lvl = 0->close, -1->Mkt Price, 1,2,3..based on times of atr gap required)
nifty_ord_exec_level1 = float(cfg.get("realtime", "nifty_ord_exec_level1"))
nifty_ord_exec_level2 = float(cfg.get("realtime", "nifty_ord_exec_level2"))
nifty_ord_exec_level3 = float(cfg.get("realtime", "nifty_ord_exec_level3"))

crude_ord_exec_level1 = float(cfg.get("realtime", "crude_ord_exec_level1"))
crude_ord_exec_level2 = float(cfg.get("realtime", "crude_ord_exec_level2"))
crude_ord_exec_level3 = float(cfg.get("realtime", "crude_ord_exec_level3"))


nifty_lot_size = int(cfg.get("info", "nifty_lot_size"))
criude_lot_size = int(cfg.get("info", "crude_lot_size"))
nifty_symbol = cfg.get("info", "nifty_symbol")
crude_symbol = cfg.get("info", "crude_symbol")
nifty_tgt1 = float(cfg.get("info", "nifty_tgt1"))  #15.0
nifty_tgt2 = float(cfg.get("info", "nifty_tgt2"))  #60.0 medium target
nifty_tgt3 = float(cfg.get("info", "nifty_tgt3"))  #150.0 high target
crude_tgt1 = float(cfg.get("info", "crude_tgt1"))  #10.0
crude_tgt2 = float(cfg.get("info", "crude_tgt2"))  #60.0
crude_tgt3 = float(cfg.get("info", "crude_tgt2"))  #60.0
olhc_duration = int(cfg.get("info", "olhc_duration"))   #3
nifty_sqoff_time = int(cfg.get("info", "nifty_sqoff_time")) #1512 time after which orders not to be processed and open orders to be cancelled
crude_sqoff_time = int(cfg.get("info", "crude_sqoff_time")) #2310 time after which orders not to be processed and open orders to be cancelled
nifty_tsl = int(cfg.get("info", "nifty_tsl"))   #Trailing Stop Loss for Nifty
crude_tsl = int(cfg.get("info", "crude_tsl"))   #Trailing Stop Loss for Nifty
rsi_buy_param = int(cfg.get("info", "rsi_buy_param"))   #may need exchane/indicator specific; ML on this?
rsi_sell_param = int(cfg.get("info", "rsi_sell_param"))
premarket_advance = int(cfg.get("info", "premarket_advance"))
premarket_decline = int(cfg.get("info", "premarket_decline"))
premarket_flag = int(cfg.get("info", "premarket_flag"))          # whether premarket trade enabled  or not 1=yes
nifty_last_close = float(cfg.get("info", "nifty_last_close"))
# file_crude = cfg.get("info", "file_crude")
enable_MCX = int(cfg.get("info", "enable_MCX"))                         # 1=Original flag for CRUDE trading. Daily(realtime) flag to be reset eod based on this.  
enable_NFO = int(cfg.get("info", "enable_NFO"))                         # 1=Original flag for Nifty trading. Daily(realtime) flag to be reset eod based on this.
enable_MCX_data = int(cfg.get("info", "enable_MCX_data"))               # 1=CRUDE data subscribed, processed and saved/exported 
enable_NFO_data = int(cfg.get("info", "enable_NFO_data"))               # 1=NIFTY data subscribed, processed and saved/exported
file_nifty = cfg.get("info", "file_nifty")
file_nifty_med = cfg.get("info", "file_nifty_med")
file_crude = cfg.get("info", "file_crude")
file_crude_med = cfg.get("info", "file_crude_med")
no_of_trades_limit = int(cfg.get("info", "no_of_trades_limit"))         # 2 BOs trades per order; 6 trades for 3 orders
pending_ord_limit_mins = int(cfg.get("info", "pending_ord_limit_mins")) # Close any open orders not executed beyond the set limit


mcx_trade_start_time = int(cfg.get("info", "mcx_trade_start_time"))
mcx_trade_end_time = int(cfg.get("info", "mcx_trade_end_time"))
nifty_trade_start_time = int(cfg.get("info", "nifty_trade_start_time"))
nifty_trade_end_time = int(cfg.get("info", "nifty_trade_end_time"))

nifty_no_trade_zones = eval(cfg.get("info", "nifty_no_trade_zones"))


lst_crude_ltp = []
lst_nifty_ltp = []

socket_opened = False

# Counters for dataframe indexes
df_nifty_cnt = 0           
df_nifty_med_cnt = 0       
df_crude_cnt = 0
df_crude_med_cnt = 0   

df_cols = ["cur_HHMM","open","high","low","close","signal","sl"]  # v1.1 added signal column

df_nifty = pd.DataFrame(data=[],columns=df_cols)
df_crude = pd.DataFrame(data=[],columns=df_cols)        # Low - to store 2/3 mins level data

df_crude_med = pd.DataFrame(data=[],columns=df_cols)    # Medium - to store 4/6 mins level data crude
df_nifty_med = pd.DataFrame(data=[],columns=df_cols)    # Medium - to store 4/6 mins level data nifty

# --------------- Call Initialization functions ------------------------
# Load previous day data files, last 10 rows 
# Maybe we can put this into a load procedure 
try:

    # CRUDE previous data load
    if int(datetime.datetime.now().strftime("%H%M")) < 905:
        # 1. --- Read from previous day. In case of rerun or failures do not load previous day
        # Can clear the prameter file_nifty in the ab.ini if previous day data is not required
        if enable_MCX_data and file_crude.strip()!="":
            iLog("Reading previous 40 period data from " + file_crude)
            #May need try/catch due to copy of ini file or failed runs
            df_crude = pd.read_csv(file_crude).tail(40) 
            df_crude.reset_index(drop=True, inplace=True)   # To reset index from 0 to 9 as tail gets the last 10 indexes
            df_crude_cnt = len(df_crude.index)
            # iLog("df_crude_cnt=" + str(df_crude_cnt))

        if enable_MCX_data and file_crude_med.strip()!="":
            iLog("Reading previous 40 period data from " + file_crude_med)
            #May need try/catch due to copy of ini file or failed runs
            df_crude_med = pd.read_csv(file_crude_med).tail(40) 
            df_crude_med.reset_index(drop=True, inplace=True)   # To reset index from 0 to 9 as tail gets the last 10 indexes
            df_crude_med_cnt = len(df_crude_med.index)
            # iLog("df_crude_med_cnt=" + str(df_crude_med_cnt))

    # NIFTY previous data load and update of nifty/crude current contract symbol in ab.ini
    # if True:
    if int(datetime.datetime.now().strftime("%H%M")) < 915:
        # 1. --- Read from previous day. In case of rerun or failures do not load previous day
        # Can clear the prameter file_nifty in the ab.ini if previous day data is not required
        if enable_NFO_data and file_nifty.strip()!="":
            iLog("Reading previous 40 period data from " + file_nifty)
            #May need try/catch due to copy of ini file or failed runs
            df_nifty = pd.read_csv(file_nifty).tail(40) 
            df_nifty.reset_index(drop=True, inplace=True)   # To reset index from 0 to 9 as tail gets the last 10 indexes
            df_nifty_cnt = len(df_nifty.index)
            # iLog("df_nifty_cnt=" + str(df_nifty_cnt))

        if enable_NFO_data and file_nifty_med.strip()!="":
            iLog("Reading previous 40 period data from " + file_nifty_med)
            df_nifty_med  = pd.read_csv(file_nifty_med).tail(40)
            df_nifty_med.reset_index(drop=True, inplace=True)
            df_nifty_med_cnt = len(df_nifty_med.index)
            # iLog("df_nifty_med_cnt=" + str(df_nifty_med_cnt))

        # 2. --- Update nifty or crude symbol in ab.ini
        iLog("Running contract expiry checks.") 
        ab_lib.update_contract_symbol()
        cfg.read(INI_FILE)  #28-aug-2020 program failed due to picking up of old nifty contract symbol
        nifty_symbol = cfg.get("info", "nifty_symbol")
        crude_symbol = cfg.get("info", "crude_symbol")

except Exception as ex:
    iLog("Loading previous day data, Exception occured = " + str(ex),3)




# Removed
# df_cols = ["cur_HHMM","open","high","low","close"]  # v1.1 Reset to list of columns required for ohlc value assignment

lst_crude_table = []            # index,open,high,low,close
lst_nifty = []  
cur_min = 0
flg_min = 0
flg_med_nifty = 0               # Flag for avoiding consecutive orders when medium signal is generated 
flg_med_crude = 0
MTM = 0.0                       # Float
pos_crude = 0                   # current crude position 
pos_nifty = 0                   # current nifty position


super_trend_n = []              # Supertrend list Nifty
super_trend = []                # Supertrend list Crude
interval = olhc_duration        # Time interval of candles in minutes; 2 
processNiftyEOD = False         # Process pending Nifty order cancellation and saving of df data; Flag to run procedure only once
processCrudeEOD = False         # Process pending Crude order cancellation; Flag to run procedure only once
export_data = 0                 # Realtime export of crude and nifty dataframe; triggered through .ini; reset to 0 after export


############################################################################
#       Functions
############################################################################
def get_realtime_config():
    '''This procedure can be called during execution to get realtime values from the .ini file'''

    global tradeNFO, tradeMCX, enableBO2_crude, enableBO2_nifty, enableBO3_nifty, cfg, nifty_sl\
    ,crude_sl, export_data, sl_buffer, nifty_ord_type, crude_ord_type, mtm_sl, mtm_target\
    ,nifty_ord_exec_level1,crude_ord_exec_level1 
         
    
    cfg.read(INI_FILE)
    
    tradeNFO = int(cfg.get("realtime", "tradeNFO"))                 # True = 1 (or non zero) False=0
    tradeMCX = int(cfg.get("realtime", "tradeMCX"))                 # True = 1 (or non zero) False=0
    enableBO2_nifty = int(cfg.get("realtime", "enableBO2_nifty"))   # True = 1 (or non zero) False=0
    enableBO3_nifty = int(cfg.get("realtime", "enableBO3_nifty"))   # True = 1 (or non zero) False=0
    enableBO2_crude = int(cfg.get("realtime", "enableBO2_crude"))   # True = 1 (or non zero) False=0 
    nifty_sl = float(cfg.get("realtime", "nifty_sl"))               #20.0
    crude_sl = float(cfg.get("realtime", "crude_sl"))               #15.0
    export_data = float(cfg.get("realtime", "export_data"))
    mtm_sl = float(cfg.get("realtime", "mtm_sl"))
    mtm_target  = float(cfg.get("realtime", "mtm_target"))
    #print(enableBO2,enableBO3,tradeNFO,tradeMCX,flush=True)
    sl_buffer = int(cfg.get("realtime", "sl_buffer"))
    nifty_ord_type = cfg.get("realtime", "nifty_ord_type")      # BO / MIS
    crude_ord_type = cfg.get("realtime", "crude_ord_type")      # MIS / BO
    nifty_ord_exec_level1 = float(cfg.get("realtime", "nifty_ord_exec_level1"))
    crude_ord_exec_level1 = float(cfg.get("realtime", "crude_ord_exec_level1"))

def savedata(flgUpdateConfigFile=True):
    '''flgUpdateConfigFile = True Updates datafilename in the .ini file for nextday reload.
    
     In case of intermediary exports you may not want to update the datafile in the .ini file'''

    iLog("In savedata(). Exporting dataframes to .csv files.",6)    # Log as activity

    try:
        ts_ext = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".csv"
        if enable_NFO_data:
            file_nifty = "./data/NIFTY_" + ts_ext 
            file_nifty_med = "./data/NIFTY_MED_" + ts_ext
            df_nifty.to_csv(file_nifty,index=False)
            df_nifty_med.to_csv(file_nifty_med,index=False)

        if enable_MCX_data:
            file_crude = "./data/CRUDE_" + ts_ext
            file_crude_med = "./data/CRUDE_MED_" + ts_ext
            df_crude.to_csv(file_crude,index=False)
            df_crude_med.to_csv(file_crude_med,index=False)

        # Save nifty and crude filenames for use in next day to load last 10 rows
        if flgUpdateConfigFile :
            if enable_NFO_data:
                cfg.set("info","file_nifty",file_nifty)
                cfg.set("info","file_nifty_med",file_nifty_med)
            
            if enable_MCX_data:
                cfg.set("info","file_crude",file_crude)
                cfg.set("info","file_crude_med",file_crude_med)

            with open('ab.ini', 'w') as configfile:
                cfg.write(configfile)
                configfile.close()

    except Exception as ex:
        iLog("In savedata(). Exception occured = " + str(ex),3)

def squareOff_MIS(buy_sell,ins_scrip,qty, order_type = OrderType.Market, limit_price=0.0):
    '''Square off MIS positions at EoD or when mtm limit is reached. Also used for placing Market orders. 
    buy_sell = TransactionType.Buy/TransactionType.Sell

    order_type = OrderType.StopLossLimit Default is Market order

    limit_price = limit price in case SL order needs to be placed 
    '''
    global alice

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
                         is_amo = False)

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
                         price = limit_price,
                         trigger_price = limit_price,
                         stop_loss = stop_loss_abs,
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

def buy_crude(strMsg):
    global df_crude

    df_crude.iat[-1,5]="B"  # v1.1 set signal column value

    lt_price, crude_sl = get_trade_price("CRUDE","BUY",crude_ord_exec_level1)   # Get trade price and SL for BO1 

    df_crude.iat[-1,6] = crude_sl   
    
    strMsg = strMsg + " Limit Price=" + str(lt_price) + " SL=" + str(crude_sl)

    if not tradeMCX:
        strMsg = strMsg + " In buy_crude(): tradeMCX=0. Order will not be executed."
        iLog(strMsg,2,sendTeleMsg=True)
        return

    if not check_trade_time_zone("CRUDE"):
        strMsg = strMsg + " In buy_crude(): No trade time zone. Order will not be executed."
        iLog(strMsg,2,sendTeleMsg=True)
        return

    # position_crude = get_position('CRUDE')
    # print("pos_crude=",pos_crude)

    if pos_crude > 0 :  # Position updated in MTM check
        strMsg = "buy_crude() BO1 Position already exists. " + strMsg    #do not buy if position already exists; 
    else:

        if trade_limit_reached("CRUDE"):
            strMsg = strMsg + "In buy_crude().Trade limit reached."
            iLog(strMsg,2,sendTeleMsg=True)
            return

        # if check_pending_orders("CRUDE","BUY"):
        #     iLog("Pending CRUDE BUY Order exists. Cancelling BUY Orders.")
        #     close_all_orders("NIFTY","BUY")
            
        # else:
        #     iLog("Cancelling and CRUDE SELL Orders if exists.")
        #     close_all_orders("CRUDE","SELL")

        close_all_orders("CRUDE")

        if crude_ord_type == "MIS" :
            #  If not first order, make it double qty
            if pos_crude == 0 :  
                crude_ord_qty = crude_bo1_qty 
            else:
                crude_ord_qty = crude_bo1_qty * 2

            #---- Intraday order (MIS)
            # order = buy_signal(ins_crude, crude_ord_qty, lt_price, crude_sl, crude_tgt1, crude_tsl,ProductType.Intraday)
            # Place a market type buy order using squareOff_MIS()
            order = squareOff_MIS(TransactionType.Buy, ins_crude,crude_ord_qty)

            if order['status'] == 'success':
                strMsg = strMsg + " MIS order_id=" + str(order['data']['oms_order_id'])
            else:
                strMsg = strMsg + ' buy_crude() MIS Order Failed.' + order['message']


        elif crude_ord_type == "BO" :
            #---- First Bracket order for initial target
            order = buy_signal(ins_crude, crude_bo1_qty, lt_price, crude_sl, crude_tgt1, crude_tsl)

            if order['status']=='success':
                # buy_order1_crude = order['data']['oms_order_id']
                strMsg = strMsg + " 1st BO order_id=" + str(order['data']['oms_order_id'])
            else:
                strMsg = strMsg + ' buy_crude() 1st BO Failed.'+ order['message']


            #---- Second Bracket order for open target
            if enableBO2_crude:
                lt_price, crude_sl = get_trade_price("CRUDE","BUY",crude_ord_exec_level2)   # Get trade price and SL for BO2
                order = buy_signal(ins_crude, crude_bo2_qty, lt_price, crude_sl, crude_tgt2, crude_tsl)
                strMsg = strMsg + " BO2 Limit Price=" + str(lt_price) + " SL=" + str(crude_sl)
                if order['status']=='success':
                    # buy_order2_crude = order['data']['oms_order_id']
                    strMsg = strMsg + " 2nd BO order_id=" + str(order['data']['oms_order_id'])
                else:
                    strMsg = strMsg + ' buy_crude() 2nd BO Failed.'+ order['message']

            #---- Third Bracket order for open target
            if enableBO3_crude:  
                lt_price, crude_sl = get_trade_price("CRUDE","BUY",crude_ord_exec_level3)   # Get trade price and SL for BO3
                order = buy_signal(ins_crude, crude_bo3_qty, lt_price, crude_sl, crude_tgt3, crude_tsl)
                strMsg = strMsg + " BO3 Limit Price=" + str(lt_price) + " SL=" + str(crude_sl)
                if order['status']=='success':
                    strMsg = strMsg + " 3rd BO order_id=" + str(order['data']['oms_order_id'])
                else:
                    strMsg=strMsg + ' buy_crude() 3rd BO Failed.' + order['message']
    
    
    iLog(strMsg,sendTeleMsg=True)

    # Not required as its already called above
    #-- Exit from sell order if any
    # close_all_orders("CRUDE","SELL")
    # strMsg = "CRUDE open SELL orders cancelled."
    # iLog(strMsg,sendTeleMsg=True)

def sell_crude(strMsg):
    
    global df_crude

    df_crude.iat[-1,5] = "S"  # v1.1 set signal column value

    lt_price, crude_sl = get_trade_price("CRUDE","SELL",crude_ord_exec_level1)   # Get trade price and SL for BO1 

    df_crude.iat[-1,6] = crude_sl  # v3.7 set sl column value. This is only for BO1; rest BOs will different SLs 

    strMsg = strMsg + " Limit Price=" + str(lt_price) + " SL=" + str(crude_sl) 

    if not tradeMCX:
        strMsg = strMsg + " In sell_crude(): tradeMCX=0. Order not initiated."
        iLog(strMsg,2,sendTeleMsg=True)
        return

    if not check_trade_time_zone("CRUDE"):
        strMsg = strMsg + " In sell_crude(): No trade time zone. Order not initiated."
        iLog(strMsg,2,sendTeleMsg=True)
        return
    
    # position_crude = get_position('CRUDE')
    print("pos_crude=",pos_crude)
    #---- First Bracket order for initial target
    if pos_crude < 0 :  # Position updated in MTM check
        strMsg = "sell_crude(): BO1 Position already exists. " + strMsg    #do not buy if position already exists; 
    else:

        if trade_limit_reached("CRUDE"):
            strMsg = strMsg + "In sell_crude(): Trade limit reached."
            iLog(strMsg,2,sendTeleMsg=True)
            return

        # if check_pending_orders("CRUDE","SELL"):
        #     iLog("Pending CRUDE SELL Order exists. Cancelling SELL Orders.")
        #     close_all_orders("NIFTY","SELL")
            
        # else:
        #     iLog("Cancelling and CRUDE BUY Orders if exists.")
        #     close_all_orders("CRUDE","BUY")

        close_all_orders("CRUDE")

        if crude_ord_type == "MIS" : 
            # If not first order, make it double qty
            if pos_crude == 0 :  
                crude_ord_qty = crude_bo1_qty
            else:
                crude_ord_qty = crude_bo1_qty * 2

            #---- Intraday order (MIS)
            # order = sell_signal(ins_crude,crude_ord_qty,lt_price,crude_sl,crude_tgt1,crude_tsl,ProductType.Intraday)
            # Place a market order using squareOff_MIS
            order = squareOff_MIS(TransactionType.Sell, ins_crude,crude_ord_qty)
            if order['status'] == 'success':
                strMsg = strMsg + " MIS order_id=" + str(order['data']['oms_order_id'])
            else:
                strMsg = strMsg + ' sell_crude() MIS Order Failed.' + order['message']


        elif crude_ord_type == "BO" :
            #---- First Bracket order for initial target
            order = sell_signal(ins_crude,crude_bo1_qty,lt_price,crude_sl,crude_tgt1,crude_tsl)
            if order['status']=='success':
                # sell_order1_crude = order['data']['oms_order_id']
                strMsg = strMsg + " 1st BO order_id=" + str(order['data']['oms_order_id'])
            else:
                strMsg = strMsg + ' sell_crude() 1st BO Failed.'+ order['message']
            

            #---- Second Bracket order for open target
            if enableBO2_crude:
                lt_price, crude_sl = get_trade_price("CRUDE","SELL",crude_ord_exec_level2)   # Get trade price and SL for BO2
                order = sell_signal(ins_crude,crude_bo2_qty,lt_price,crude_sl,crude_tgt2,crude_tsl)
                strMsg = strMsg + " BO2 Limit Price=" + str(lt_price) + " SL=" + str(crude_sl)

                if order['status']=='success':
                    # sell_order2_crude = order['data']['oms_order_id']
                    strMsg = strMsg + " 2nd BO order_id=" + str(order['data']['oms_order_id'])

                else:
                    strMsg = strMsg + ' sell_crude() 2nd BO Failed.'+ order['message']

            #---- Third Bracket order for open target
            if enableBO3_crude:
                lt_price, crude_sl = get_trade_price("CRUDE","SELL",crude_ord_exec_level3)   # Get trade price and SL for BO3
                order = sell_signal(ins_crude,crude_bo3_qty,lt_price,crude_sl,crude_tgt3,crude_tsl)
                strMsg = strMsg + " BO3 Limit Price=" + str(lt_price) + " SL=" + str(crude_sl)

                if order['status'] == 'success':
                    # sell_order2_crude = order['data']['oms_order_id']
                    strMsg = strMsg + " 3rd BO order_id=" + str(order['data']['oms_order_id'])

                else:
                    strMsg = strMsg + ' sell_crude() 3rd BO Failed.'+ order['message']


    iLog(strMsg,sendTeleMsg=True)

    # Not required as close_all_orders(CRUDE) is already called
    #-- Exit from buy order if any
    # close_all_orders("CRUDE","BUY")
    # strMsg = "CRUDE open BUY orders cancelled."
    # iLog(strMsg,sendTeleMsg=True)
       
    
    
    # #if position_crude>0:
    # try:
    #     strMsg="No crude buy order positions to cancel."
    #     if buy_order1_crude:
    #         cancel_status=alice.cancel_order(buy_order1_crude)
    #         strMsg="Cancelling CRUDE BUY OrderID="+buy_order1_crude+' cancel_status=' + cancel_status['status'] 
    #         buy_order1_crude=''
    #     if buy_order2_crude:
    #         cancel_status=alice.cancel_order(buy_order2_crude)
    #         strMsg=strMsg +", OrderID=" +  buy_order2_crude + " cancel_status=" + cancel_status['status'] 
    #         buy_order2_crude=''
    # except Exception as ex:
    #     strMsg='cancel_order() in sell_crude() failed.' + str(ex)

    # iLog(strMsg,sendTeleMsg=True)

def buy_nifty(strMsg):
   
    global df_nifty

    df_nifty.iat[-1,5] = "B"  # v1.1 set signal column value

    lt_price, nifty_sl = get_trade_price("NIFTY","BUY",nifty_ord_exec_level1)   # Get trade price and SL for BO1 
    
    df_nifty.iat[-1,6] = nifty_sl  # v3.7 set sl column value. This is only for BO1; rest BOs will different SLs 

    strMsg = strMsg + " Limit Price=" + str(lt_price) + " SL=" + str(nifty_sl) 
    
    if not tradeNFO:
        strMsg = strMsg + " buy_nifty(): tradeNFO=0. Order not initiated."
        iLog(strMsg,2,sendTeleMsg=True)
        return

    if not check_trade_time_zone("NIFTY"):
        strMsg = strMsg + " buy_nifty(): No trade time zone. Order not initiated."
        iLog(strMsg,2,sendTeleMsg=True)
        return

    # position_nifty = get_position('NIFTY')
    
    
    # if position_nifty!=0 : position_nifty=position_nifty/75     # Calculate Nifty number of Positions

    if pos_nifty > 0:   # Position updates in MTM check
        strMsg = "buy_nifty(): BO1 Position already exists. " + strMsg    #do not buy if position already exists; 
    else:

        if trade_limit_reached("NIFTY"):
            strMsg = strMsg + "buy_nifty(): NIFTY Trade limit reached."
            iLog(strMsg,2,sendTeleMsg=True)
            return

        # may not be required as in case of positions you have to cancel it 
        # and in case of pending also you have to cancel it and create fresh orders 
        # if check_pending_orders("NIFTY","BUY"):
        #     iLog("Pending BUY Order exists. Cancelling BUY Orders.")
        #     close_all_orders("NIFTY","BUY")
            
        # else:
        #     iLog("Cancelling any SELL Orders if exists.")
        #     close_all_orders("NIFTY","SELL")

        # Cancel pending buy orders and close existing sell orders if any
        close_all_orders("NIFTY")
        
        if nifty_ord_type == "MIS" : 
            if pos_nifty == 0 :
                nifty_ord_qty = nifty_bo1_qty
            else:
                nifty_ord_qty = nifty_bo1_qty * 2

            #---- Intraday order (MIS) , Market Order
            # order = buy_signal(ins_nifty,nifty_ord_qty,lt_price,nifty_sl,nifty_tgt1,nifty_tsl,ProductType.Intraday)    #SL to be float; 
            order = squareOff_MIS(TransactionType.Buy, ins_nifty,nifty_ord_qty)
            if order['status'] == 'success':
                # sell_order1_nifty = order1['data']['oms_order_id']
                strMsg = strMsg + " MIS order_id=" + str(order['data']['oms_order_id'])
            else:
                strMsg = strMsg + ' buy_nifty() MIS Order Failed.' + order['message']


        elif nifty_ord_type == "BO" :
            #---- First Bracket order for initial target
            order = buy_signal(ins_nifty,nifty_bo1_qty,lt_price,nifty_sl,nifty_tgt1,nifty_tsl)    #SL to be float; 
            if order['status'] == 'success' :
                # buy_order1_nifty = order['data']['oms_order_id']
                strMsg = strMsg + " 1st BO order_id=" + str(order['data']['oms_order_id'])
            else:
                strMsg = strMsg + ' buy_nifty() 1st BO Failed.' + order['message']

            #---- Second Bracket order for open target
            if enableBO2_nifty:
                lt_price, nifty_sl = get_trade_price("NIFTY","BUY",nifty_ord_exec_level2)   # Get trade price and SL for BO2
                order = buy_signal(ins_nifty,nifty_bo2_qty,lt_price,nifty_sl,nifty_tgt2,nifty_tsl)
                strMsg = strMsg + " BO2 Limit Price=" + str(lt_price) + " SL=" + str(nifty_sl)
                if order['status'] == 'success':
                    # buy_order2_nifty = order['data']['oms_order_id']
                    strMsg = strMsg + " 2nd BO order_id=" + str(order['data']['oms_order_id'])
                else:
                    strMsg=strMsg + ' buy_nifty() 2nd BO Failed.' + order['message']

            #---- Third Bracket order for open target
            if enableBO3_nifty:  
                lt_price, nifty_sl = get_trade_price("NIFTY","BUY",nifty_ord_exec_level3)   # Get trade price and SL for BO3
                order = buy_signal(ins_nifty,nifty_bo3_qty,lt_price,nifty_sl,nifty_tgt3,nifty_tsl)
                strMsg = strMsg + " BO3 Limit Price=" + str(lt_price) + " SL=" + str(nifty_sl)
                if order['status']=='success':
                    # buy_order3_nifty = order['data']['oms_order_id']
                    strMsg = strMsg + " 3rd BO order_id=" + str(order['data']['oms_order_id'])
                else:
                    strMsg=strMsg + ' buy_nifty() 3rd BO Failed.' + order['message']

    iLog(strMsg,sendTeleMsg=True)


    #-- Exit from sell order if any
    # close_all_orders("NIFTY","SELL")
    # strMsg = "NIFTY open SELL orders cancelled."
    # iLog(strMsg,sendTeleMsg=True)

def sell_nifty(strMsg):
    
    global df_nifty
    
    df_nifty.iat[-1,5] = "S"  # v1.1 set signal column value
    
    lt_price, nifty_sl = get_trade_price("NIFTY","SELL",nifty_ord_exec_level1)   # Get trade price and SL for BO1 

    df_nifty.iat[-1,6] = nifty_sl  # v3.7 set sl column value. This is only for BO1; rest BOs will different SLs 

    strMsg = strMsg + " Limit Price=" + str(lt_price) + " SL=" + str(nifty_sl) 

    if not tradeNFO:
        strMsg = strMsg + " In sell_nifty(): tradeNFO=0. Order not initiated."
        iLog(strMsg,2,sendTeleMsg=True)
        return

    if not check_trade_time_zone("NIFTY"):
        strMsg = strMsg + " In sell_nifty(): No trade time zone. Order not initiated."
        iLog(strMsg,2,sendTeleMsg=True)
        return

     # position_nifty = get_position('NIFTY')

    # if position_nifty!=0 : position_nifty=position_nifty/75

    if pos_nifty < 0 :  # Position updated in MTM check
        strMsg = "sell_nifty() BO1 Position already exists. "+strMsg    #do not buy if position already exists; 
    else:

        if trade_limit_reached("NIFTY"):
            strMsg = strMsg + "In sell_nifty(). NIFTY Trade limit reached."
            iLog(strMsg,2,sendTeleMsg=True)
            return

        # if check_pending_orders("NIFTY","SELL"):
        #     iLog("Pending SELL Order exists. Cancelling SELL Orders.")
        #     close_all_orders("NIFTY","SELL")
            
        # else:
        #     iLog("Cancelling any BUY Orders if exists.")
        #     close_all_orders("NIFTY","BUY")

        # Cancel pending buy orders and close existing sell orders if any
        close_all_orders("NIFTY")


        if nifty_ord_type == "MIS" :
            if pos_nifty == 0 :
                nifty_ord_qty = nifty_bo1_qty
            else:
                nifty_ord_qty = nifty_bo1_qty * 2
 
            #---- Intraday order (MIS) , Market Order
            # order = sell_signal(ins_nifty,nifty_ord_qty,lt_price,nifty_sl,nifty_tgt1,nifty_tsl,ProductType.Intraday)   #SL to be float
            order = squareOff_MIS(TransactionType.Sell, ins_nifty,nifty_ord_qty)
            if order['status'] == 'success':
                # sell_order1_nifty = order1['data']['oms_order_id']
                strMsg = strMsg + " MIS order_id=" + str(order['data']['oms_order_id'])
            else:
                strMsg = strMsg + ' sell_nifty() MIS Order Failed.' + order['message']


        elif nifty_ord_type == "BO" :
            #---- First Bracket order for initial target
            order = sell_signal(ins_nifty,nifty_bo1_qty,lt_price,nifty_sl,nifty_tgt1,nifty_tsl)   #SL to be float
            if order['status'] == 'success':
                # sell_order1_nifty = order1['data']['oms_order_id']
                strMsg = strMsg + " 1st BO order_id=" + str(order['data']['oms_order_id'])
            else:
                strMsg = strMsg + ' sell_nifty() 1st BO Failed.' + order['message']

            #---- Second Bracket order for 2nd target
            if enableBO2_nifty:
                lt_price, nifty_sl = get_trade_price("NIFTY","SELL",nifty_ord_exec_level2)   # Get trade price and SL for BO2 
                order = sell_signal(ins_nifty,nifty_bo2_qty,lt_price,nifty_sl,nifty_tgt2,nifty_tsl)
                strMsg = strMsg + " BO2 Limit Price=" + str(lt_price) + " SL=" + str(nifty_sl)

                if order['status'] == 'success':
                    # sell_order2_nifty = order['data']['oms_order_id']
                    strMsg = strMsg + " 2nd BO order_id=" + str(order['data']['oms_order_id']) 
                else:
                    strMsg = strMsg + ' sell_nifty() 2nd BO Failed.' + order['message']

            #---- Third Bracket order for open target
            if enableBO3_nifty:
                lt_price, nifty_sl = get_trade_price("NIFTY","SELL",nifty_ord_exec_level3)   # Get trade price and SL for BO3 
                order = sell_signal(ins_nifty,nifty_bo3_qty,lt_price,nifty_sl,nifty_tgt3,nifty_tsl)
                strMsg = strMsg + " BO3 Limit Price=" + str(lt_price) + " SL=" + str(nifty_sl)
                if order['status'] == 'success':
                    # sell_order3_nifty = order['data']['oms_order_id']
                    strMsg = strMsg + " 3rd BO order_id=" + str(order['data']['oms_order_id'])
                else:
                    strMsg = strMsg + ' sell_nifty() 3rd BO Failed.' + order['message']
    
    iLog(strMsg,sendTeleMsg=True)


    #-- Exit from buy order if any
    close_all_orders("NIFTY","BUY")
    strMsg = "NIFTY open BUY orders cancelled."
    iLog(strMsg,sendTeleMsg=True)

def subscribe_ins():
    global alice,ins_nifty,ins_crude

    try:
        if enable_NFO_data : alice.subscribe(ins_nifty, LiveFeedType.COMPACT)
        if enable_MCX_data : alice.subscribe(ins_crude, LiveFeedType.COMPACT)
    
    except Exception as ex:
        iLog("subscribe_ins(): Exception="+ str(ex),3)
    
    iLog("subscribe_ins().")

def close_all_orders(crude_nifty="ALL",buy_sell="ALL",ord_open_time=0):
    '''Cancel pending orders. crude_nifty=ALL/CRUDE/NIFTY , buy_sell = ALL/BUY/SELL'''
    # print(datetime.datetime.now(),"In close_all_orders().",crude_nifty,flush=True)

    #Square off CRUDE/NIFTY MIS Positions if any
    if crude_nifty=='NIFTY' and nifty_ord_type == "MIS":
        if pos_nifty > 0 :   
            squareOff_MIS(TransactionType.Sell, ins_nifty,pos_nifty)
        elif pos_nifty < 0 :
            squareOff_MIS(TransactionType.Buy, ins_nifty, abs(pos_nifty))

    if crude_nifty=='CRUDE' and crude_ord_type == "MIS":    
        # Squareoff CRUDE/NIFTY MIS Positions
        if pos_crude > 0 :
            squareOff_MIS(TransactionType.Sell, ins_crude, pos_crude)
        elif pos_crude < 0 :
            squareOff_MIS(TransactionType.Buy, ins_crude, abs(pos_crude))



    # Get pending orders
    try:
        orders = alice.get_order_history()['data']['pending_orders'] #Get all orders
        if not orders:
            # print(datetime.datetime.now(),"In close_all_orders(). No Pending Orders found.",crude_nifty,flush=True)
            iLog("close_all_orders(): No Pending Orders found for "+ str(crude_nifty))
            return    
        # Else is captured below exception
        
    except Exception as ex:
        orders = None
        # print("In close_all_orders(). Exception="+ str(ex),flush=True)
        iLog("close_all_orders(): Exception="+ str(ex),3)
        return

    if crude_nifty == "ALL":
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
            iLog("close_all_orders(): Cancelling all order " + c_order['oms_order_id'])
            alice.cancel_all_orders()
    else:
        for c_order in orders:
            #if c_order['leg_order_indicator']=='' then its actual pending order not leg order
            if crude_nifty == c_order['trading_symbol'][:5]:
                if buy_sell == "ALL" :
                    iLog("close_all_orders(): Cancelling order "+c_order['oms_order_id'])
                    alice.cancel_order(c_order['oms_order_id'])    

                elif buy_sell == c_order['transaction_type']:
                    iLog("close_all_orders(): Cancelling order "+c_order['oms_order_id'])
                    alice.cancel_order(c_order['oms_order_id'])


    iLog("close_all_orders(): crude_nifty={},buy_sell={},ord_open_time={}".format(crude_nifty,buy_sell,ord_open_time)) #6 = Activity/Task done

def check_MTM_Limit():
    ''' Checks and returns the current MTM and sets the trading flag based on the limit specified in the 
    ab.ini. This needs to be called before buy/sell signal generation in processing. 
    Also updates the postion counter for Nifty and Crude which are used in buy/sell procs.'''
    
    global tradeMCX, tradeNFO, pos_nifty, pos_crude

    trading_symbol = ""
    mtm = 0.0
    pos_crude = 0
    pos_nifty = 0

    try:    # Get daywise postions (MTM)
        pos = alice.get_daywise_positions()
        if pos:
            pos_crude = 0
            pos_nifty = 0
            for p in  pos['data']['positions']:
                mtm = float(p['m2m'].replace(",","")) + mtm
                # print("get_position()",p['trading_symbol'],p['net_quantity'],flush=True)
                trading_symbol = p['trading_symbol'][:5]
                if trading_symbol == 'NIFTY':
                    pos_nifty = pos_nifty + int(p['net_quantity'])

                elif trading_symbol == 'CRUDE':
                    pos_crude = pos_crude + int(p['net_quantity'])

    except Exception as ex:
        mtm = -1.0  # To ignore in calculations in case of errors
        print("check_MTM_Limit(): Exception=",ex, flush = True)
    
    # print(mtm,mtm_sl,mtm_target,flush=True)

    # Enable trade flags based on MTM limits set
    if (mtm < mtm_sl or mtm > mtm_target) and (tradeMCX==1 or tradeNFO==1): # or mtm>mtm_target:
        tradeMCX = 0
        tradeNFO = 0
        # Stop further trading and set both the trading flag to 0
        cfg.set("realtime","tradeNFO","0")
        cfg.set("realtime","tradeMCX","0")

        try:
            with open('ab.ini', 'w') as configfile:
                cfg.write(configfile)
                configfile.close()
            
            strMsg = "check_MTM_Limit(): Trade flags set to false. MTM={}, tradeNFO={}, tradeMCX={}".format(mtm,tradeNFO,tradeMCX)
            iLog(strMsg,6)  # 6 = Activity/Task done
            
        except Exception as ex:
            strMsg = "check_MTM_Limit(): Trade flags set to false. May be overwritten. Could not update ini file. Ex="+str(ex)
            iLog(strMsg,3)

        iLog("check_MTM_Limit(): MTM {} out of SL or Target range. Squareoff will be triggered for MIS orders...".format(mtm),2,sendTeleMsg=True)

        # Squareoff CRUDE/NIFTY MIS Positions if out of trade limit; Also used in CrudeEOD section
        if crude_ord_type == "MIS" and pos_crude > 0 :      # in Long position; Limit price is close of previous candle. Can be optimised for latest price minus something.
            if mtm > mtm_target :
                squareOff_MIS(TransactionType.Sell, ins_crude, pos_crude, OrderType.StopLossLimit, df_crude.close.iloc[-1])
            else:
                squareOff_MIS(TransactionType.Sell, ins_crude, pos_crude)

        elif crude_ord_type == "MIS" and pos_crude < 0 :    # in short position
            if mtm > mtm_target :
                squareOff_MIS(TransactionType.Buy, ins_crude, abs(pos_crude), OrderType.StopLossLimit, df_crude.open.iloc[-1] )
            else:
                squareOff_MIS(TransactionType.Buy, ins_crude, abs(pos_crude))

        if nifty_ord_type == "MIS" and pos_nifty > 0 :      # in Long position
            if mtm > mtm_target :
                squareOff_MIS(TransactionType.Sell, ins_nifty,pos_nifty, OrderType.StopLossLimit, df_nifty.close.iloc[-1])
            else:
                squareOff_MIS(TransactionType.Sell, ins_nifty,pos_nifty)

        elif nifty_ord_type == "MIS" and pos_nifty < 0 :    # in short position
            if mtm > mtm_target :
                squareOff_MIS(TransactionType.Buy, ins_nifty, abs(pos_nifty), OrderType.StopLossLimit, df_nifty.open.iloc[-1])
            else:
                squareOff_MIS(TransactionType.Buy, ins_nifty, abs(pos_nifty))


    return mtm

def premarket_tarde():
    global buy_order1_nifty, sell_order1_nifty

    sell_order2_nifty = ""
    buy_order2_nifty = ""
    advance_flag = 0
    decline_flag = 0
    qty_bo1, qty_bo2 =75, 75
    strMsg = ""
    advances = premarket_advance/50
    declines = premarket_decline/50
    
    # Set quantities for BO1 and BO2 
    if advances>0.90:
        advance_flag = 1
        qty_bo1 = 75
        qty_bo2 = 75
    elif advances>0.70:   
        advance_flag = 1
        qty_bo1 = 75
        qty_bo2 = 75
    elif declines>0.90:
        decline_flag = 1
        qty_bo1 = 75
        qty_bo2 = 75
    elif declines>0.70:   
        decline_flag = 1
        qty_bo1 = 75
        qty_bo2 = 75

    if advance_flag:
        #BO1
        nifty_ltp=lst_nifty_ltp[-1]
        order1=buy_signal(ins_nifty,qty_bo1,nifty_ltp,nifty_sl,nifty_tgt1,nifty_tsl)
        if order1['status']=='success':
            buy_order1_nifty=order1['data']['oms_order_id']
            strMsg="NIFTY PREMARKET BO1 BUY Limit Price=" + str(nifty_ltp) + " SL=" + str(nifty_sl) + "ORB Ord ID=" + buy_order1_nifty
        else:
            strMsg="NIFTY PREMARKET BO1 BUY failed!"
        
        iLog(strMsg)

        #BO2
        if enableBO2_nifty:
            nifty_ltp=lst_nifty_ltp[-1]
            order1=buy_signal(ins_nifty,qty_bo2,nifty_ltp,nifty_sl,nifty_tgt2,nifty_tsl)
            if order1['status']=='success':
                buy_order2_nifty=order1['data']['oms_order_id']
                strMsg= strMsg + " NIFTY PREMARKET BO2 BUY Limit Price=" + str(nifty_ltp) + " SL=" + str(nifty_sl) + "ORB Ord ID=" + buy_order2_nifty
            else:
                strMsg= strMsg + "NIFTY PREMARKET BO2 BUY failed!"
        else:
            strMsg=strMsg + " NIFTY PREMARKET BO2 not enabled"
        
        iLog(strMsg)

    elif decline_flag:
        #BO1
        nifty_ltp=lst_nifty_ltp[-1]
        order1=sell_signal(ins_nifty,qty_bo1,nifty_ltp,nifty_sl,nifty_tgt1,nifty_tsl)   #SL to be float
        strMsg=strMsg+ " Limit Price=" + str(nifty_ltp)
        if order1['status']=='success':
            sell_order1_nifty=order1['data']['oms_order_id']
            strMsg=strMsg + " NIFTY PREMARKET SELL 1st BO order_id=" + sell_order1_nifty
        else:
            strMsg=strMsg + " NIFTY PREMARKET SELL 1st BO Failed." + order1['message']

        iLog(strMsg)

        #BO2
        if enableBO2_nifty:
            nifty_ltp=lst_nifty_ltp[-1]
            order1=sell_signal(ins_nifty,qty_bo2,nifty_ltp,nifty_sl,nifty_tgt1,nifty_tsl)   #SL to be float
            strMsg=strMsg+ " Limit Price=" + str(nifty_ltp)
            if order1['status']=='success':
                sell_order2_nifty=order1['data']['oms_order_id']
                strMsg=strMsg + " NIFTY PREMARKET SELL 2nd BO order_id=" + sell_order2_nifty
            else:
                strMsg=strMsg + " NIFTY PREMARKET SELL 2nd BO Failed." + order1['message']
        else:
            strMsg="NIFTY PREMARKET BO2 not enabled"

        iLog(strMsg)

    else:
        strMsg = "premarket_tarde(). No premarket opportunity found."
        iLog(strMsg)

    iLog(strMsg,sendTeleMsg=True)
    iLog("advances={} declines={} qty_bo1={} qty_bo2={}".format(advances,declines,qty_bo1,qty_bo2))

def get_trade_price(crude_nifty,buy_sell,bo_level=1):
    '''Returns the trade price and stop loss abs value for crude/nifty=CRUDE/NIFTY
    buy_sell=BUY/SELL, bo_level or Order execution level = 1(default means last close),2,3 and 0 for close -1 for market order
    '''

    atr = 0
    sl = 20.0

    if crude_nifty == "NIFTY":

        # 1. Set atr
        # 2020-sep-03 ignore addition of atr value for high volatility
        if df_nifty.TR.iloc[-1] < 25 :
            # atr = round(df_nifty.ATR.iloc[-1] * bo_level * 0.5 )
            atr = round(df_nifty.ATR.iloc[-1] * bo_level)   # removed multiplication with 0.5. Multiplication factor to be set in bo_level

        # 2. Set default limit price
        lt_price = round(df_nifty.close.iloc[-1]) # Set Default trade price

        if buy_sell == "BUY":
            # Only in Nifty            
            if bo_level == -1 :  # Place market order
                lt_price = lt_price + 10       # Low was close
                sl = round(lt_price - df_nifty_med.ST.iloc[-1]) + sl_buffer
            else:
                lt_price = lt_price - atr
                sl = round(lt_price - df_nifty_med.ST.iloc[-1]) + sl_buffer

            # # Check if order is triggered due to override, if override SL will be ST of medium timeframe
            # elif df_nifty.STX.iloc[-1] == 'down':  
            #     lt_price = lt_price - atr       # Low was close
            #     sl = round(lt_price - df_nifty_med.ST.iloc[-1]) + sl_buffer
            
            # else:
            #     lt_price = round(df_nifty.open.iloc[-1] - atr)       # Low was open
            #     sl = round(lt_price - df_nifty.ST.iloc[-1]) + sl_buffer
        
        elif buy_sell=="SELL":
            # Only in Nifty
            if bo_level == -1 :  # Place market order
                lt_price = lt_price - 10      # Low was close
                sl = round(df_nifty_med.ST.iloc[-1] - lt_price) + sl_buffer
            else:
                lt_price = lt_price + atr      # high was close
                sl = round(df_nifty_med.ST.iloc[-1] - lt_price) + sl_buffer

            # # Check if order is triggered due to override, if override SL will be ST of medium timeframe
            # elif df_nifty.STX.iloc[-1] == 'up':
            #     lt_price = lt_price + atr      # high was close
            #     sl = round(df_nifty_med.ST.iloc[-1] - lt_price) + sl_buffer
            
            # else:
            #     lt_price = lt_price + atr      # high was open
            #     sl = round(df_nifty.ST.iloc[-1] - lt_price) + sl_buffer

        # Set SL limits
        if (sl < 1  or sl > nifty_sl) :
            iLog("Calculated SL={}".format(sl))
            sl = nifty_sl
    
        print("atr={}, df_nifty.close={},df_nifty.ATR={},df_nifty.STX={},bo_level={}".format(atr, df_nifty.close.iloc[-1], df_nifty.ATR.iloc[-1],df_nifty.STX.iloc[-1],bo_level),flush=True)
    
    elif crude_nifty=="CRUDE":

        lt_price = df_crude.close.iloc[-1]  # Default trade price
        
        if df_crude.TR.iloc[-1] < 20 :
            atr = round(df_crude.ATR.iloc[-1] * bo_level)

        if buy_sell == "BUY":
            lt_price = lt_price - atr
            sl = round(lt_price - df_crude_med.ST.iloc[-1]) + sl_buffer
            # # Check if order is triggered due to override, if override SL will be ST of medioum timeframe
            # if df_crude.STX.iloc[-1] == 'down':  
            #     sl = round(lt_price - df_crude_med.ST.iloc[-1]) + sl_buffer
            # else:
            #     sl = round(lt_price - df_crude.ST.iloc[-1]) + sl_buffer
        
        elif buy_sell=="SELL":
            lt_price = lt_price + atr
            sl = round(df_crude_med.ST.iloc[-1] - lt_price) + sl_buffer
            # # Check if order is triggered due to override, if override SL will be ST of medium timeframe
            # if df_crude.STX.iloc[-1] == 'up':
            #     sl = round(df_crude_med.ST.iloc[-1] - lt_price) + sl_buffer
            # else:
            #     sl = round(df_crude.ST.iloc[-1] - lt_price) + sl_buffer

        if (sl < 1 or sl > crude_sl) :
            iLog("Calculated SL={}".format(sl))
            sl = crude_sl
        
        print("atr={},df_crude.close={},df_crude.ATR={},df_crude.STX={},bo_level={}".format(atr, df_crude.close.iloc[-1], df_crude.ATR.iloc[-1], df_crude.STX.iloc[-1],bo_level),flush=True)
    
    return lt_price,sl

def trade_limit_reached(crude_nifty="NIFTY"):
    # Check if completed order can work here
    '''Check if number of trades reached/crossed the parameter limit . Return true if reached or crossed else false.
     Dont process the Buy/Sell order if returns true
     crude_nifty=CRUDE/NIFTY '''
    
    trades_cnt = 0  # Number of trades, needs different formula in case of nifty / crude
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
        iLog("trade_limit_reached(): No Trades found for "+ str(crude_nifty))
        return False        # No trades, hence go ahead

    for c_trade in trades:
        if crude_nifty == c_trade['trading_symbol'][:5]:
            if c_trade['transaction_type'] == "BUY" :
                buy_cnt = buy_cnt + 1
            elif c_trade['transaction_type'] == "SELL" :
                 sell_cnt = sell_cnt + 1

    iLog("trade_limit_reached(): buy_cnt={}, sell_cnt={}".format(buy_cnt,sell_cnt))            
    
    if buy_cnt > sell_cnt:
        trades_cnt = buy_cnt
    else:
        trades_cnt = sell_cnt

    if trades_cnt >= no_of_trades_limit:
        return True
    else:
        return False

def set_config_value(section,key,value):
    '''Set the config file (ab.ini) value. Applicable for setting only one parameter value. 
    All parameters are string

    section=info/realtime,key,value
    '''
    cfg.set(section,key,value)
    try:
        with open('ab.ini', 'w') as configfile:
            cfg.write(configfile)
            configfile.close()
    except Exception as ex:
        iLog("Exception writing to config. section={},key={},value={},ex={}".format(section,key,value,ex),2)

def check_trade_time_zone(crude_nifty="NIFTY"):
    ''' Returns false if the current time (HHMM) falls in no trade zone
    '''
    result = False

    cur_time = int(datetime.datetime.now().strftime("%H%M"))

    if crude_nifty=="CRUDE" and (cur_time > mcx_trade_start_time and cur_time < mcx_trade_end_time) :
        result = True
    elif crude_nifty=="NIFTY" and (cur_time > nifty_trade_start_time and cur_time < nifty_trade_end_time) :
        result = True
        if any(lower <= cur_time <= upper for (lower, upper) in nifty_no_trade_zones):
            result = False

    return result


########################################################################
#       Events
########################################################################
def event_handler_quote_update(message):
    global lst_crude_ltp, lst_nifty_ltp

    if(message['exchange']=='MCX'): 
        lst_crude_ltp.append(message['ltp'])
    elif(message['exchange']=='NFO'):
        lst_nifty_ltp.append(message['ltp'])

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
access_token = getAccessToken()

# Connect to AliceBlue and download contracts
alice = AliceBlue(username=susername, password=spassword, access_token=access_token, master_contracts_to_download=['NFO','MCX'])

# Get Nifty and Crude instrument objects
if enable_NFO_data : ins_nifty = alice.get_instrument_by_symbol('NFO', nifty_symbol)
if enable_MCX_data : ins_crude = alice.get_instrument_by_symbol('MCX', crude_symbol)


# Code Test area, can be above access_token generation if testing under maintenance window.
# sell_crude("Testing")
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

# 2020-08-13 moved back here
subscribe_ins()    #This is called in the socket open event now to address missing ticks while websocket failure/reconnect. Previously was called here
strMsg = "Starting tick processing."
iLog(strMsg,sendTeleMsg=True)


# Process tick data/indicators and generate buy/sell and execute orders
while True:
    # Process as per start of market timing
    cur_HHMM = int(datetime.datetime.now().strftime("%H%M"))
    # print("cur_HHMM=",cur_HHMM,flush=True)
    if cur_HHMM == 915 and premarket_flag == 1:
        premarket_flag = 0
        cfg.read(INI_FILE)      # As the previous values will be stale and read around 9:00 AM
        nifty_last_close = float(cfg.get("info", "nifty_last_close"))
        gap = abs(nifty_last_close - float(lst_nifty_ltp[-1]))
        if gap < 50:  
            premarket_tarde()
        else:
            strMsg = "Premarket trade will not be executed. Gap between last close and todays open high = "+str(gap) + " Points."
            iLog(strMsg)

    if cur_HHMM > 859:

        cur_min = datetime.datetime.now().minute 

        # Below if block will run after every time interval specifie in the .ini file
        if( cur_min % interval == 0 and flg_min != cur_min):

            flg_min = cur_min     # Set the minute flag to run the code only once post the interval
            t1 = time.time()      # Set timer to record the processing time of all the indicators
            
            # Can include the below code to work in debug mode only
            strMsg = "C=" + str(len(lst_crude_ltp))
            # if len(df_crude.index) > 0 : strMsg = strMsg + " "+str(df_crude.close.iloc[-1]) 

            strMsg = strMsg +  " N="+ str(len(lst_nifty_ltp))
            # if len(df_nifty.index) > 0 : strMsg = strMsg + " "+str(df_nifty.close.iloc[-1]) 


            # Check MTM and stop trading if limit reached; This can be parameterised to % gain/loss
            MTM = check_MTM_Limit()
           
            
            if len(lst_crude_ltp) > 1:    #CRUDE Candle
                tmp_lst = lst_crude_ltp.copy()  #Copy the ticks to a temp list
                lst_crude_ltp.clear()           #reset the ticks list; There can be gap in the ticks during this step ???
                #print(f"CRUDE: cur_min = {cur_min},len(tmp_lst)={len(tmp_lst)},i={i}",flush=True)
                #Formation of candle
                df_crude.loc[df_crude_cnt, df_cols]=[cur_HHMM, tmp_lst[0], max(tmp_lst), min(tmp_lst), tmp_lst[-1],"",0]
                df_crude_cnt = df_crude_cnt + 1 
                # open = df_crude.close.tail(3).head(1)  # First value  
                flg_med_crude = 0
                strMsg = strMsg + " " + str(tmp_lst[-1])      #Crude close 

                if cur_min % 6 == 0 :
                    df_crude_med.loc[df_crude_med_cnt,df_cols] = [cur_HHMM, df_crude.open.tail(3).head(1).iloc[0], df_crude.high.tail(3).max(), df_crude.low.tail(3).min(), df_crude.close.iloc[-1], "",0 ] 
                    df_crude_med_cnt = df_crude_med_cnt + 1
                    # print(df_crude_med,flush=True )
                    flg_med_crude = 1
                    
            if len(lst_nifty_ltp) > 1 and cur_HHMM > 914 and cur_HHMM < 1531:    #Nifty Candle
                tmp_lst = lst_nifty_ltp.copy()  #Copy the ticks to a temp list
                lst_nifty_ltp.clear()           #reset the ticks list
                #print(f"NIFTY: cur_min = {cur_min},len(tmp_lst)={len(tmp_lst)},j={j}",flush=True)
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

            strMsg = strMsg + " POS="+ str(pos_nifty) + " MTM=" + str(MTM)

            iLog(strMsg,sendTeleMsg=True)

            # =======================================
            #           CRUDE Order Generation
            # ======================================
            if df_crude_cnt > 6: #Calculate Crude indicators and buy/sell 
                
                # Indicator Calculations - Low level (2min) timeframe calc
                SuperTrend(df_crude)
                RSI(df_crude)
                super_trend = df_crude.STX.values
                SuperTrend(df_crude_med)            # Medium level (6min) timeframe calculations
                 
                strMsg="Crude: #={}, ST_LOW={}, ST_LOW_SL={}, ATR={}, ST_MED={}, ST_MED_SL={}".format(df_crude_cnt, super_trend[-1], round(df_crude.ST.iloc[-1]), round(df_crude.ATR.iloc[-1],1), df_crude_med.STX.iloc[-1], round(df_crude_med.ST.iloc[-1]) )
                iLog(strMsg)

                # -- ST LOW
                #--BUY---BUY---BUY---BUY---BUY---BUY---BUY---BUY---BUY---BUY
                if super_trend[-1]=='up' and super_trend[-2]=='down' and super_trend[-3]=='down' and super_trend[-4]=='down' and super_trend[-5]=='down' and super_trend[-6]=='down':
                    #Buy only if both medium and lower ST is in buy zone
                    if df_crude_med.STX.iloc[-1] == 'down':
                        strMsg="CRUDE ST=up, ST_MEDIUM=down. Sell order to be placed.Deactivated"
                        # sell_crude(strMsg)
                        iLog(strMsg,sendTeleMsg=True)
                        close_all_orders('CRUDE')

                    elif df_crude.RSI.iloc[-1] > rsi_buy_param and df_crude.RSI.iloc[-1] < rsi_sell_param:
                        c1 = round((df_crude.RSI.iloc[-2] - df_crude.RSI.iloc[-3]) / df_crude.RSI.iloc[-3], 3)
                        c2 = round((df_crude.RSI.iloc[-1] - df_crude.RSI.iloc[-2]) / df_crude.RSI.iloc[-2], 3)

                        iLog("CRUDE ST=up - RSI Rate of change c2(latest)={},c1(previous)={}".format(c2,c1))

                        if c2 > c1: #percent Rate of change is increasing 
                            strMsg="CRUDE ST=up, RSI BUY=" + str(df_crude.RSI.iloc[-1])
                            buy_crude(strMsg)
                        else:
                            strMsg="CRUDE ST=up - RSI Rate of change not as per trend"
                            iLog(strMsg,sendTeleMsg=True)
                    else:
                        strMsg="CRUDE ST=up, close=" + str(df_crude.close.iloc[-1]) +", RSI NOBUY=" + str(df_crude.RSI.iloc[-1])
                        iLog(strMsg,sendTeleMsg=True)                 
                
                #---SELL---SELL---SELL---SELL---SELL---SELL---SELL---SELL
                elif super_trend[-1]=='down' and super_trend[-2]=='up' and super_trend[-3]=='up' and super_trend[-4]=='up' and super_trend[-5]=='up' and super_trend[-6]=='up':
                    #print("SELL super_trend[-2]=",super_trend[-2],flush=True)
                    # Sell only if both medium and lower ST is in sell zone
                    if df_crude_med.STX.iloc[-1]=='up':
                        strMsg="CRUDE ST=down, ST_MEDIUM=up. Buy order to be placed.Deactivated"
                        # buy_crude(strMsg)
                        iLog(strMsg,sendTeleMsg=True)
                        close_all_orders('CRUDE')
                        
                    elif df_crude.RSI.iloc[-1] < rsi_sell_param and df_crude.RSI.iloc[-1] > rsi_buy_param:
                        c1 = round((df_crude.RSI.iloc[-2] - df_crude.RSI.iloc[-3]) / df_crude.RSI.iloc[-3], 3)
                        c2 = round((df_crude.RSI.iloc[-1] - df_crude.RSI.iloc[-2]) / df_crude.RSI.iloc[-2], 3)
                        iLog("CRUDE ST=down - RSI Rate of change c2(latest)={},c1(previous)={}".format(c2,c1))
                        if c2 < c1: #percent Rate of change is decreasing
                            strMsg = "CRUDE ST=down, RSI SELL=" + str(df_crude.RSI.iloc[-1])
                            sell_crude(strMsg)
                        else:
                            strMsg = "CRUDE ST=down - RSI Rate of change not as per trend"
                            iLog(strMsg,sendTeleMsg=True)

                    else:
                        strMsg = "CRUDE ST=down " + str(df_crude.close.iloc[-1]) +", RSI NOSELL=" + str(df_crude.RSI.iloc[-1])
                        iLog(strMsg,sendTeleMsg=True)

                # ST MEDIUM
                #--BUY---BUY---BUY
                elif df_crude_med.STX.iloc[-1]=='up' and df_crude_med.STX.iloc[-2]=='down' and df_crude_med.STX.iloc[-3]=='down' and df_crude_med.STX.iloc[-4]=='down':
                    # Ensure both are in same direction
                    if super_trend[-1]=='up':
                        if flg_med_crude :
                            strMsg = "CRUDE ST_MEDIUM=up, ST=up. Buy Order to be placed. "
                            buy_crude(strMsg)
                        else:    
                            iLog("CRUDE ST_MEDIUM=up, ST=up. Consecutive Buy Order Skipped.")


                    else:
                        strMsg = "CRUDE ST_MEDIUM=up, ST=down. Buy not triggered. Need Investigation."
                        iLog(strMsg,sendTeleMsg=True)

                #---SELL---SELL---SELL
                elif df_crude_med.STX.iloc[-1]=='down' and df_crude_med.STX.iloc[-2]=='up' and df_crude_med.STX.iloc[-3]=='up' and df_crude_med.STX.iloc[-4]=='up':
                    # Ensure both are in same direction
                    if super_trend[-1]=='down':
                        if flg_med_crude :
                            strMsg = "CRUDE ST_MEDIUM down, ST=down. Sell Order to be placed. "
                            sell_crude(strMsg)
                        else:
                            iLog("CRUDE ST_MEDIUM down, ST=down. Consecutive SELL Order Skipped.")

                    else:
                        strMsg = "CRUDE ST_MEDIUM=down, ST=up. Sell not triggered. Need Investigation."
                        iLog(strMsg)

            if df_nifty_cnt == -10 and cur_HHMM == 916:    # Opening Range Breakout; disabled, need to be optimised, j==1
                #if open==high - sell
                # print(datetime.datetime.now(),"ORB open,high,low:",df_nifty.open.iloc[-1],df_nifty.high.iloc[-1],df_nifty.low.iloc[-1],flush=True)
                strMsg = "ORB open,high,low:{} {} {}".format(df_nifty.open.iloc[-1],df_nifty.high.iloc[-1],df_nifty.low.iloc[-1])
                iLog(strMsg)
                try:
                    if df_nifty.open.iloc[-1]==df_nifty.high.iloc[-1]:
                        #Set SL; Can be tricky if there is huge movement
                        sl = round(df_nifty.open.iloc[-1]-df_nifty.close.iloc[-1])+5.0
                        if sl<30:
                            order1=sell_signal(ins_nifty,75,df_nifty.close.iloc[-1],sl,nifty_tgt1,nifty_tsl)
                            if order1['status']=='success':
                                sell_order1_nifty=order1['data']['oms_order_id']
                                strMsg="NIFTY ORB SELL Limit Price=" + str(df_nifty.close.iloc[-1]) + " SL=" + str(sl) + "ORB Ord ID=" + sell_order1_nifty
                            else:
                                strMsg="NIFTY ORB SELL failed!"
                        else:
                            strMsg="NIFTY ORB not triggred. SL too high " + str(sl)

                    elif df_nifty.open.iloc[-1]==df_nifty.low.iloc[-1]:
                        #ins_scrip,qty,limit_price,stop_loss_abs,target_abs,trailing_sl_abs
                        sl=round(df_nifty.close.iloc[-1]-df_nifty.open.iloc[-1])+5.0
                        if sl<30:
                            order1=buy_signal(ins_nifty,75,df_nifty.close.iloc[-1],sl,nifty_tgt1,nifty_tsl)
                            if order1['status']=='success':
                                buy_order1_nifty=order1['data']['oms_order_id']
                                strMsg="NIFTY ORB BUY Limit Price=" + str(df_nifty.close.iloc[-1]) + " SL=" + str(sl) + "ORB Ord ID=" + buy_order1_nifty
                            else:
                                strMsg="NIFTY ORB BUY failed!"
                        else:
                            strMsg="NIFTY ORB not triggred. SL too high " + str(sl)
                    else:
                        strMsg="No ORB opportunity found."
                    iLog(strMsg)

                except Exception as ex:
                    strMsg="ORB Exception=" + str(ex)
                    iLog(strMsg,3)

                # print(strMsg,flush=True)   
                
                iLog(strMsg,sendTeleMsg=True)
            
            # Nifty - Only 5 ST values checked in condition as compared to crude
            # Orders to be pushed only till 3:10 PM; can be parameterised
            # ////////////////////////////////////////
            #           NIFTY Order Generation
            # ////////////////////////////////////////
            if df_nifty_cnt > 6 and cur_HHMM > 914 and cur_HHMM < 1531:        # Calculate Nifty indicators and call buy/sell

                SuperTrend(df_nifty)                    # Low level (2/3min) timeframe calculations
                RSI(df_nifty,period=10)                 # RSI Calculations
                super_trend_n = df_nifty.STX.values     # Get ST values into a list
                SuperTrend(df_nifty_med)                # Medium level (6min) timeframe calculations

                strMsg="Nifty: #={}, ST_LOW={}, ST_LOW_SL={}, ATR={}, ST_MED={}, ST_MED_SL={}".format(df_nifty_cnt, super_trend_n[-1], round(df_nifty.ST.iloc[-1]), round(df_nifty.ATR.iloc[-1],1), df_nifty_med.STX.iloc[-1], round(df_nifty_med.ST.iloc[-1]) )
                iLog(strMsg)

                # -- ST LOW
                #--BUY---BUY---BUY---BUY---BUY---BUY---BUY---BUY---BUY---BUY
                if super_trend_n[-1]=='up' and super_trend_n[-2]=='down' and super_trend_n[-3]=='down' and super_trend_n[-4]=='down' and super_trend_n[-5]=='down' and super_trend_n[-6]=='down':
                    #print("Nifty close=",df_nifty.close.iloc[-1],flush=True)
                    #print("RSI[-1]=",df_nifty.RSI.iloc[-1],flush=True)
                    #Buy only if both medium and lower ST is in buy zone
                    if df_nifty_med.STX.iloc[-1] == 'down':
                        strMsg = "NIFTY ST=up, ST_MEDIUM=down. Sell order to be placed - Deactivated"
                        iLog(strMsg,sendTeleMsg=True)
                        close_all_orders('NIFTY')

                        # sell_nifty(strMsg)
                        # Experiment
                        # Buy 
                    elif df_nifty.RSI.iloc[-1] > rsi_buy_param and df_nifty.RSI.iloc[-1] < rsi_sell_param:

                        c1 = round((df_nifty.RSI.iloc[-2] - df_nifty.RSI.iloc[-3]) / df_nifty.RSI.iloc[-3], 3 )
                        c2 = round((df_nifty.RSI.iloc[-1] - df_nifty.RSI.iloc[-2]) / df_nifty.RSI.iloc[-2], 3 )

                        iLog("NIFTY ST=up - RSI Rate of change c2(latest)={},c1(previous)={}".format(c2,c1))
                        if c2 > c1: #percent Rate of change is increasing 
                            strMsg = "NIFTY ST=up, RSI BUY=" + str(df_nifty.RSI.iloc[-1])
                            buy_nifty(strMsg)
                        else:
                            strMsg = "NIFTY ST=up - RSI Rate of change not as per trend"
                            iLog(strMsg,sendTeleMsg=True)
                    else:
                        strMsg = "NIFTY ST=up, close=" + str(df_nifty.close.iloc[-1]) + ", RSI NOBUY=" + str(df_nifty.RSI.iloc[-1])    
                        iLog(strMsg,sendTeleMsg=True)

                # -- ST LOW        
                #---SELL---SELL---SELL---SELL---SELL---SELL---SELL---SELL---SELL        
                elif super_trend_n[-1]=='down' and super_trend_n[-2]=='up' and super_trend_n[-3]=='up' and super_trend_n[-4]=='up' and super_trend_n[-5]=='up' and super_trend_n[-6]=='up':
                    #Sell only if both medium and lower ST is in sell zone
                    if df_nifty_med.STX.iloc[-1] == 'up':
                        strMsg = "NIFTY ST=down, ST_MEDIUM='up'. Buy Order to be placed - Deactivated "
                        iLog(strMsg,sendTeleMsg=True)
                        # buy_nifty(strMsg)
                        close_all_orders('NIFTY')

                    elif df_nifty.RSI.iloc[-1] < rsi_sell_param and df_nifty.RSI.iloc[-1] > rsi_buy_param:
                        
                        c1 = round( ( df_nifty.RSI.iloc[-2] - df_nifty.RSI.iloc[-3] ) / df_nifty.RSI.iloc[-3] , 3 )
                        c2 = round( ( df_nifty.RSI.iloc[-1] - df_nifty.RSI.iloc[-2] ) / df_nifty.RSI.iloc[-2] , 3 )
                        
                        iLog("NIFTY ST=down - RSI Rate of change c2(latest)={},c1(previous)={}".format(c2,c1))
                        
                        if c2 < c1: # percent Rate of change is decreasing
                            strMsg = "NIFTY ST=down, RSI SELL=" + str(df_nifty.RSI.iloc[-1])
                            sell_nifty(strMsg)
                        else:
                            strMsg = "NIFTY ST=down - RSI Rate of change not as per trend"
                            iLog(strMsg,sendTeleMsg=True)
                    else:
                        strMsg = "NIFTY ST=down close=" + str(df_nifty.close.iloc[-1]) +", RSI NOSELL=" + str(df_nifty.RSI.iloc[-1])   
                        iLog(strMsg,sendTeleMsg=True)

                # ST MEDIUM
                #--BUY---BUY---BUY
                elif df_nifty_med.STX.iloc[-1]=='up' and df_nifty_med.STX.iloc[-2]=='down' and df_nifty_med.STX.iloc[-3]=='down' and df_nifty_med.STX.iloc[-4]=='down':
                    # Ensure both are in same direction
                    if super_trend_n[-1] == 'up':
                        if flg_med_nifty :
                            strMsg = "NIFTY ST_MEDIUM=up, ST=up. Buy Order to be placed. "
                            buy_nifty(strMsg)
                        else:
                            iLog("NIFTY ST_MEDIUM=up, ST=up. Consecutive nifty buy order skipped.")


                    else:
                        strMsg="NIFTY ST_MEDIUM=up, ST=down. Buy not triggered. Need Investigation."
                        iLog(strMsg,sendTeleMsg=True)

                #---SELL---SELL---SELL
                elif df_nifty_med.STX.iloc[-1]=='down' and df_nifty_med.STX.iloc[-2]=='up' and df_nifty_med.STX.iloc[-3]=='up' and df_nifty_med.STX.iloc[-4]=='up':
                    # Ensure both are in same direction
                    if super_trend_n[-1] == 'down':
                        if flg_med_nifty :
                            strMsg = "NIFTY ST_MEDIUM=down, ST=down. Sell Order to be placed. "
                            sell_nifty(strMsg)
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

            #-- Cancel Nifty open orders and save data
            if cur_HHMM > nifty_sqoff_time and not processNiftyEOD: 
                close_all_orders('NIFTY')
                processNiftyEOD = True    # Set this flag so that we don not repeatedely process this
 
            
            #-- Cancel all open Crude orders after 11:10 PM, time can be parameterised
            if cur_HHMM > crude_sqoff_time and not processCrudeEOD:
                close_all_orders('CRUDE')
                processCrudeEOD = True

            #-- Export data on demand
            if export_data:     
                savedata(False) # Export dataframe data, both crude and nifty
                export_data = 0   # Reset config value to 0 in both file and variable
                set_config_value("realtime","export_data","0")

            
            #-- Check if any open order greater than pending_ord_limit_mins and cancel the same 
            close_all_orders(ord_open_time=pending_ord_limit_mins)

        if cur_HHMM > 1530 and cur_HHMM < 1532 :   # Exit the program post NSE closure
            if enable_MCX :
                pass
            else:
                if enable_NFO : 
                    iLog("Enabling NFO trading...")
                    set_config_value("realtime","tradenfo","1")

                savedata()      # Export dataframe data, both 
                iLog("Shutter down... Calling sys.exit() @ " + str(cur_HHMM),1,True)
                sys.exit()
        
        if cur_HHMM > 2330 and cur_HHMM < 2332 :   # Exit the program post MCX closure
            # Reset trading flag for crude if crude is enabled on the instance
            if enable_MCX : 
                iLog("Enabling MCX trading...")    
                set_config_value("realtime","trademcx","1")
            
            # Reset trading flag for nifty if nifty is enabled on the instance
            if enable_NFO : 
                iLog("Enabling NFO trading...")
                set_config_value("realtime","tradenfo","1")
            
            savedata()      # Export dataframe data, both 
            iLog("Shutter down... Calling sys.exit() @ " + str(cur_HHMM))
            sys.exit()

    time.sleep(6)   # May be reduced to accomodate the processing delay

# Reference code
# Write multiple sheets to excel
# import pandas as pd

# # Create a Pandas Excel writer using XlsxWriter as the engine.
# writer = pd.ExcelWriter('e:\\test.xlsx', engine='xlsxwriter')

# # Write each dataframe to a different worksheet. you could write different string like above if you want
# df1.to_excel(writer, sheet_name='Sheet1')
# df2.to_excel(writer, sheet_name='Sheet2')

# # Close the Pandas Excel writer and output the Excel file.
# writer.save()