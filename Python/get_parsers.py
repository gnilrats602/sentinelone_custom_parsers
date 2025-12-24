import os
import sys
import time
import json
import datetime
import logging
import requests
import argparse
import config as cfg
import pandas as pd
from pathlib import Path
from gql import gql, Client
from prettyprinter import cpprint
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.exceptions import TransportProtocolError, TransportServerError, TransportQueryError


def main(args):
    script_start_time = time.perf_counter()
    global MYLOGGER, ROOT_DIR, CONFIG_PATH, MAIN_DIR, SCRIPT_LOGS, SCRIPT_OUTPUT
    global CONSOLEURL, SDLURL, HEADERS, SDLHEADERS, TODAY, THIS_DAY, APITOKEN
    (MYLOGGER, ROOT_DIR, CONFIG_PATH, MAIN_DIR, SCRIPT_LOGS, SCRIPT_OUTPUT, CONSOLEURL, SDLURL, HEADERS, SDLHEADERS,
     TODAY, THIS_DAY, APITOKEN) = cfg.main(args)
    try:
        print(args)



    except KeyboardInterrupt:
        print("CTRL+C detected. Exiting...")
        sys.exit(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Version: 0.1 - This script gets alerts')
    required = parser.add_argument_group('Required Arguments')
    parser.add_argument("-a", "--account", dest="account", help="Account", required=False, default='ALL')
    parser.add_argument("-c", "--console", dest="console", help="Input Console i.e. EU, US", required=False, default="US")
    args = parser.parse_args()
    main(args)
