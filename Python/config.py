import os
import json
import time
import datetime
import logging


def main(args):
    structure()
    MYLOGGER = create_logfile()
    get_config(args.console)
    return (MYLOGGER, ROOT_DIR, CONFIG_PATH, MAIN_DIR, SCRIPT_LOGS, SCRIPT_OUTPUT, CONSOLEURL, SDLURL,
            HEADERS, SDLHEADERS, TODAY, THIS_DAY, APITOKEN)

def structure():
    global ROOT_DIR, CONFIG_PATH, MAIN_DIR, SCRIPT_LOGS,  SCRIPT_OUTPUT

    onedrive = os.environ['ONEDRIVE']
    script_path_name = 'MDR_Scripts'
    package_name = 'Parser Info'

    ROOT_DIR = os.path.join(onedrive, script_path_name)
    MAIN_DIR = os.path.join(ROOT_DIR, package_name)
    CONFIG_PATH = os.path.join(ROOT_DIR, 'Config')
    SCRIPT_OUTPUT = os.path.join(MAIN_DIR, 'Output')
    SCRIPT_LOGS = os.path.join(MAIN_DIR, 'Logs')


    if not os.path.exists(ROOT_DIR):
        os.makedirs(ROOT_DIR)
        # print("Created:\t{}".format(root_dir))
    else:
        pass
        # print("Exists:\t\t{}".format(root_dir))

    if not os.path.exists(CONFIG_PATH):
        os.makedirs(CONFIG_PATH)
        # print("Created:\t{}".format(config_path))
    else:
        pass
        # print("Exists:\t\t{}".format(config_path))

    if not os.path.exists(MAIN_DIR):
        os.makedirs(MAIN_DIR)
        # print("Created:\t{}".format(main_dir))
    else:
        pass
        # print("Exists:\t\t{}".format(main_dir))

    if not os.path.exists(SCRIPT_LOGS):
        os.makedirs(SCRIPT_LOGS)
        # print("Created:\t{}".format(script_logs))
    else:
        pass
        # print("Exists:\t\t{}".format(script_logs))

    if not os.path.exists(SCRIPT_OUTPUT):
        os.makedirs(SCRIPT_OUTPUT)
        # print("Created:\t{}".format(script_ouput))
    else:
        pass
        # print("Exists:\t\t{}".format(script_ouput))

    #return ROOT_DIR, CONFIG_PATH, MAIN_DIR, SCRIPT_LOGS,  SCRIPT_OUTPUT

def get_config(console_input):
    """Sets global variables based on commandline flags"""

    console = console_input.upper()
    global CONSOLEURL, SDLURL, HEADERS, SDLHEADERS, TODAY, THIS_DAY, APITOKEN

    # reads information from config file and sets results as global variables
    config_file = os.path.join(CONFIG_PATH, 'config.json')

    with open(config_file) as json_config:
        config = json.load(json_config)
    try:
        CONSOLEURL = config[console]['console']
        SDLURL = config[console]['sdl_console']
        APITOKEN = config[console]['token']
    except KeyError:
        mylogger.info("Invalid Console Identifier. Please try again.")
        exit()

    for k, v in config[console].items():
        if v:
            pass
        else:
            mylogger.info("NO API Token for this console. Please try again")
            exit()
    HEADERS = {"Content-type": "application/json", "Authorization": "APIToken " + APITOKEN}
    SDLHEADERS = {"Content-type": "application/json", "Authorization": "Bearer " + APITOKEN}
    TODAY = datetime.datetime.now()
    THIS_DAY = datetime.datetime.today().date()
    mylogger.info("Script Initialized...")

def create_logfile():
    global mylogger
    timestr = time.strftime("%Y%m%d%H%M%S")
    outfile = timestr + "_FDS.log"
    log_file = os.path.join(SCRIPT_LOGS, outfile)
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(filename=log_file, encoding='utf-8', level=logging.INFO, format='%(asctime)s.%(msecs)02d | %(message)s', filemode='w',
                        datefmt='%Y-%m-%d %H:%M:%S')
    mylogger = setup_logger('mylogger', log_file)
    return mylogger

def setup_logger(logger_name, logfile):
    """Provides standardized logging for the Script Family"""
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    fh = logging.FileHandler(logfile)
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch_formatter = logging.Formatter(f'%(asctime)s.%(msecs)02d | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    fh_formatter = logging.Formatter(f'%(asctime)s.%(msecs)02d | %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    fh.setFormatter(fh_formatter)
    ch.setFormatter(ch_formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

if __name__ == "__main__":
    main()