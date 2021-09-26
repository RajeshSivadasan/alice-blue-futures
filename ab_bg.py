# pylint: disable=unused-wildcard-import
# Backgroung process to update ab.ini through external interface resulting in passing commands to the main trade program ab.py
# v1.0 created 
# v1.1 updated help section
# v1.2 included get and set config parameter implementation. Not fully tested though.
# v1.3 get log file contents, other corrections, get files
# v1.4 exception= name 'text' is not defined issue fixed
# v1.5 Get log no of lines defaulted to 10
# v1.6 removed import telegram
# v1.7 Added back telegram, needed for sending file :). Used subprocess module for running linux command 
# v1.8 added support for get/set of token section as well  

# Info
# Once Telegram menubuilder is used, webhook gets created and it does not go away with the deletion of menubuilder bot
# you need to call deleteWebhook method like below to get the getUpdates method working
# https://api.telegram.org/<bottoken>/deleteWebhook
# currently all messages will only go to the chat id configured in ab.ini tokens section. Any other user(s) will not receive any messages although they can send messages
# This was not enabled mainly to restrict others from setting the ab.ini values which can tamper with the system.
# Readonly mode can be planned for other users. 

import ab_lib
from ab_lib import *
import sys
import time
import telegram
import subprocess

# Enable logging to file 
sys.stdout = sys.stderr = open(r"./log/ab_bg_" + datetime.datetime.now().strftime("%Y%m%d") +".log" , "a")


######################################
#       Initialise variables
######################################

# Load parameters from the config file
cfg = configparser.ConfigParser()
cfg.read("ab.ini")

# Exit if the background process is disabled 
if int(cfg.get("tokens", "enable_bg_process")) == 0:
    strMsg = "Background process not enabled. Exiting program."
    iLog(strMsg,sendTeleMsg=True)
    sys.exit()

# Set user profile; Access token and other user specific info from ab.ini will be pulled from this section
ab_lib.strChatID = cfg.get("tokens", "chat_id")
ab_lib.strBotToken = cfg.get("tokens", "bot_token")    #Bot include bot prefix in the token
strMsg = "Initialising " + __file__ + " for " + cfg.get("tokens", "uid")
iLog(strMsg,sendTeleMsg=True)

#############################
####    FUNCTIONS   #########
#############################

def save_configfile():
    try:
        with open('ab.ini', 'w') as configfile:
            cfg.write(configfile)
            configfile.close()
    except Exception as ex:
        iLog("Exception in resetting export data flag." + str(ex),2)

def sendTeleFile(attachFile):
    # iLog(ab_lib.strBotTokenWObot)
    iLog("Sending File " + attachFile, sendTeleMsg=True )
    try:
        bot = telegram.Bot(ab_lib.strBotTokenWObot)
        bot.sendDocument(chat_id=ab_lib.strChatID, document=open(attachFile, 'rb'))
    except Exception as ex:
        print("ex=",ex,flush=True)


def parseCommand(text,chat_id):
    '''Parses the text for commands and updates the ab.ini file for actions.
    Does not directly do any actions on the trading account or linux instance.
     '''
    # More validations can be done based on the enable_nfo and enable_mcx params
    global cfg

    flg_start = 0
    flg_stop = 0
    flg_nfo = 0
    flg_mxc = 0
    flg_update_config = 0
    strMsg = ""

    strStart = ['START','ENABLE']
    strStop = ['STOP','DISABLE']
    strTrade = ['TRADE','TRADING']
    strExportData = ['EXPORT','SAVE']
    strNFO = ['NFO','NIFTY']
    strMCX = ['MCX','CRUDE']
    strHelp = ['HELP']
    strGetParam = ['GET PARAM']
    strSetParam = ['SET PARAM']
    strGetLog = ['GET LOG']
    strGetFile = ['GET FILE']
    strCMD = ['CMD']

    # Read and print config file parameter values
    if any(x in text.upper() for x in strGetParam):
        if len(text.upper().split(' ')) > 2 :
            if text.upper().split(' ')[2] =='SEC':
                sec = text.upper().split(' ')[3]
                if sec.upper() == 'ALL':
                    strMsg = "Section [realtime]:\n" + str(cfg.items('realtime'))
                    iLog(strMsg,sendTeleMsg=True)
                    strMsg = "Section [info]:\n" + str(cfg.items('info'))
                    iLog(strMsg,sendTeleMsg=True)
                elif sec.upper() == 'REALTIME':
                    strMsg = "Section [realtime]:\n" + str(cfg.items('realtime'))
                    iLog(strMsg,sendTeleMsg=True)
                elif sec.upper() == 'INFO':
                    strMsg = "Section [info]:\n" + str(cfg.items('info'))
                    iLog(strMsg,sendTeleMsg=True)
                elif sec.upper() == 'TOKENS':
                    strMsg = "Section [tokens]:\n" + str(cfg.items('tokens'))
                    iLog(strMsg,sendTeleMsg=True)                
                else:
                    strMsg = "Section " + sec + " not found or no read permission." 
                    iLog(strMsg,sendTeleMsg=True)
            else:
                strMsg = "Invalid GET command.\nUsage: GET PARAM SEC <section name(info/realtime/All)>" 
                iLog(strMsg,sendTeleMsg=True)
        else:
            strMsg = "Invalid GET command.\nUsage: GET PARAM SEC <section name(info/realtime/All)>" 
            iLog(strMsg,sendTeleMsg=True)
        
        return

    # Set config file parameter values
    if any(x in text.upper() for x in strSetParam):
        # Set commands can be only executed by Rajesh as of now
        if chat_id == '670221062':     # RajeshSivadasan
            if len(text.split(' ')) > 2 :
                if text.upper().split(' ')[2] == 'SEC':
                    sec = text.lower().split(' ')[3]
                    if sec in ['realtime','info','tokens']:
                        param = text.split(' ')[4]
                        param_val = text.split( param )[1].strip()
                        cfg.set(sec.lower(), param, param_val)
                        save_configfile()    
                        strMsg = "Section " + sec + " parameter " + param + " updated with value " + param_val
                    else:
                        strMsg = "Section or parameter not found."

                    iLog(strMsg,sendTeleMsg=True)
               
                else:
                    strMsg = "Invalid SET command.\nUsage: SET PARAM SEC <section name(tokens/info/realtime> <key> <value>" 
                    iLog(strMsg,sendTeleMsg=True)
            
            else:
                strMsg = "Should not come here. Invalid SET command.\nUsage: SET PARAM SEC <section name(tokens/info/realtime> <key> <value>" 
                iLog(strMsg,sendTeleMsg=True)


        else:
            strMsg = "Invalid SET command.\nUsage: SET PARAM SEC <section name(info/realtime> <key> <value>" 
            iLog(strMsg,sendTeleMsg=True)
        
        return
    
    # Get Log file contents 
    if any(x in text.upper() for x in strGetLog):
        # print(len(text.split(' ')),flush=True)
        if len(text.split(' ')) > 2 :
            no_of_lines =  text.split(' ')[2]
            # print("no_of_lines=",no_of_lines,flush=True)
            if no_of_lines.isnumeric() :
                # Send the last n lines, set to default 10
                if no_of_lines == "" : no_of_lines = 10
                strMsg = ""
                fname = "./log/ab_" + datetime.datetime.now().strftime("%Y%m%d") +".log"
                iLog("Sending last " + no_of_lines + " lines from file " + fname,sendTeleMsg=True)
                with open(fname) as file: 
                    for line in (file.readlines() [ -1*int(no_of_lines) :]): 
                        strMsg = strMsg + line.replace("#","Cnt")
                
            iLog(strMsg,sendTeleMsg=True)
 
        elif text.strip().upper()=="GET LOG":
            # Send the log file
            fname = "./log/ab_" + datetime.datetime.now().strftime("%Y%m%d") +".log"
            sendTeleFile(fname)

        return

    if any(x in text.upper() for x in strGetFile):
        fname = text.split(' ')[2]
        iLog("fname=" + fname)
        sendTeleFile(fname)
        return

    if any(x in text.upper() for x in strCMD):
        # Send output of the linux command
        strCMD = text.split(' ',1)[1]
        lstCMD = strCMD.strip().split(' ') 
        print("lstCMD=",lstCMD)
        result = subprocess.run(lstCMD, stdout=subprocess.PIPE,stderr=subprocess.STDOUT).stdout.decode('utf-8')
        iLog(result,sendTeleMsg=True)
        return

    # Start/Stop Nifty/Crude
    if any(x in text.upper() for x in strStart):
        flg_start = 1
    
    elif any(x in text.upper() for x in strStop ):
        flg_stop = 1        

    
    if any(x in text.upper() for x in strNFO):
        flg_nfo = 1
    elif any(x in text.upper() for x in strMCX ):
        flg_mxc = 1        
    

    if flg_nfo:
        if flg_stop:
            cfg.set("realtime","tradenfo","0")
            flg_update_config = 1
        elif flg_start:
            cfg.set("realtime","tradenfo","1")
            flg_update_config = 1

    if flg_mxc:
        if flg_stop:
            cfg.set("realtime","trademcx","0")
            flg_update_config = 1
        elif flg_start:
            cfg.set("realtime","trademcx","1")
            flg_update_config = 1


    # Save/Export data
    if any(x in text.upper() for x in strExportData):
        cfg.set("realtime","export_data","1")
        flg_update_config = 1


    # Action and response of the parsed text
    if flg_update_config and chat_id == '670221062':     # RajeshSivadasan:
        save_configfile()
        iLog( text  + " triggered by updating the config file.",sendTeleMsg=True)
        return
    
    if any(x in text.upper() for x in strHelp):
        strMsg="You can ask me following:\n" + \
        "To START NIFTY trading if its disabled: START NIFTY\n" + \
        "To STOP NIFTY trading if its enabled: STOP NIFTY\n" + \
        "Similarly do for CRUDE.\n" + \
        "To export or save current ohlc data: EXPORT/SAVE\n"+ \
        "To get config parameter values: GET PARAM SEC <section name(tokens/info/realtime/All)>\n"+ \
        "To set config parameter values: SET PARAM SEC <section name(tokens/info/realtime> <key> <value>\n"+ \
        "To get Log file rows: GET LOG <No Of Rows> \n"+ \
        "To get File: GET FILE <Filename with path e.g ./log/ab_20200801.log>\n"+ \
        "To run linux command and get output: CMD <linux command>"
        iLog(strMsg,sendTeleMsg=True)

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


baseURL = "https://api.telegram.org/" + ab_lib.strBotToken +  "/getUpdates?timeout=100"
url =  baseURL
offset = None
text = ""
# iLog("url = " + url)

# Loop through the telegram message to commands
while True:
    if offset:
        url = baseURL + "&offset={}".format(offset)
    
    try:
        resp = requests.get(url)
        updates = resp.json()
        
        # iLog("updates=" + str(updates)) 
        chat_id = ""

        if len(updates["result"]) > 0:
            offset = get_last_update_id(updates) + 1

        for update in updates["result"]:
            if update["message"]["from"]["is_bot"]:
                text = ""
            else:
                text = update["message"]["text"]
                chat_id = update["message"]["chat"]["id"]  # username not commming for all user types 

        if len(text)>0:
            iLog("chat_id=" + str(chat_id)  +" text="+text)
            parseCommand(text,str(chat_id))
            text=""
    
    except Exception as e:
        print("exception=",e,flush=True)

    time.sleep(10)