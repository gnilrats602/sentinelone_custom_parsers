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
    global MYLOGGER, ROOT_DIR, CONFIG_PATH, MAIN_DIR, SCRIPT_LOGS, SCRIPT_OUTPUT, account_dict
    global CONSOLEURL, SDLURL, HEADERS, SDLHEADERS, TODAY, THIS_DAY, APITOKEN
    (MYLOGGER, ROOT_DIR, CONFIG_PATH, MAIN_DIR, SCRIPT_LOGS, SCRIPT_OUTPUT, CONSOLEURL, SDLURL, HEADERS, SDLHEADERS,
     TODAY, THIS_DAY, APITOKEN) = cfg.main(args)
    try:
        big_parser_list = []
        account_dict = {}
        get_sdl_accounts()

        for account_id, account_data in account_dict.items():
            parser_list = get_account_parser_info(account_id, account_data)
            big_parser_list.extend(parser_list)

        df = pd.DataFrame(big_parser_list, columns=["Account ID", "Account Name", "Parser Config"])
        print(df)
        user_input = input('\nSend output to Excel?  [Y]es or [N]o ')
        print()
        if user_input.upper() == 'Y':
            timestr = time.strftime("%Y%m%d%H%M%S")
            outfile = timestr + "_Parser_Configs.xlsx"
            fullpath = os.path.join(SCRIPT_OUTPUT, outfile)
            df.to_excel(fullpath, index=False)
        elif user_input.upper() == 'N':
            print("Exiting Script...")
            exit()


    except KeyboardInterrupt:
        print("CTRL+C detected. Exiting...")
        sys.exit(0)



def get_account_parser_info(account_id, account_data):
    parser_list = []
    has_next_page = True
    after_cursor = None
    get_query = "/sdl/v2/graphql"
    query_path = "queries/get_account_parser_info.graphql"
    url = CONSOLEURL + get_query
    query = load_query(query_path)
    GQLHEADERS = {"Content-type": "application/json", "Authorization": "Bearer " + APITOKEN, "S1-Scope": account_id}
    transport = RequestsHTTPTransport(url=url, verify=True, headers=GQLHEADERS, retries=0)
    client = Client(transport=transport, fetch_schema_from_transport=False)
    #variables = { "account_id": account_id }
    response = client.execute(query, get_execution_result=False)
    files = response['configFiles']
    for fileinfo in files:
        if 'logParsers' in fileinfo['name']:
            my_tuple = account_id, account_data['Account Name'], fileinfo['name']
            parser_list.append(my_tuple)
    return parser_list

def get_sdl_accounts():
    get_accounts = "/web/api/v2.1/accounts"
    limit_url = "&limit=1000"
    sort_url = "&sortBy=activeAgents&sortOrder=desc"
    url = CONSOLEURL + get_accounts + "?states=active" + limit_url + sort_url
    response = requests.get(url, headers=HEADERS).json()
    nextcursor = response['pagination']['nextCursor']
    account_data = response['data']
    for account in account_data:
        active_agents = account['activeAgents']
        account_id = account['id']
        account_name = account['name']
        bundles = account['licenses']['bundles']
        for bundle in bundles:
            if bundle['name'] == 'singularity_data_lake':
                acct_dict = {"Account Name": account_name, "Active Agents": active_agents}
                account_dict[account_id] = acct_dict
        while not (nextcursor is None):
            nexturl = url + "&cursor=" + nextcursor
            response = requests.get(nexturl, headers=HEADERS).json()
            nextcursor = response['pagination']['nextCursor']
            account_data = response['data']
            if nextcursor:
                for account in account_data:
                    active_agents = account['activeAgents']
                    account_id = account['id']
                    account_name = account['name']
                    bundles = account['licenses']['bundles']
                    for bundle in bundles:
                        if bundle['name'] == 'singularity_data_lake':
                            acct_dict = {"Account Name": account_name, "Active Agents": active_agents}
                            account_dict[account_id] = acct_dict
            else:
                response = requests.get(nexturl, headers=HEADERS).json()
                account_data = response['data']
                for account in account_data:
                    active_agents = account['activeAgents']
                    account_id = account['id']
                    account_name = account['name']
                    bundles = account['licenses']['bundles']
                    for bundle in bundles:
                        if bundle['name'] == 'singularity_data_lake':
                            acct_dict = {"Account Name": account_name, "Active Agents": active_agents}
                            account_dict[account_id] = acct_dict



def load_query(filepath):
    with open(filepath, "r") as f:
        return gql(f.read())

def get_mdr_accounts():
    #?query=mdr&sortBy=activeAgents&sortOrder=desc
    account_dict = {}
    get_accounts = "/web/api/v2.1/accounts"
    #url = CONSOLEURL + get_accounts + "?query=mdr" + "&sortBy=activeAgents&sortOrder=desc" + "&limit=1000"
    url = CONSOLEURL + get_accounts + "?query=mdr" + "&limit=1000"
    response = requests.get(url, headers=HEADERS).json()
    count = response['pagination']['totalItems']
    response_data = response['data']
    for account in response_data:
        account_id = account['id']
        account_name = account['name']
        active_agents = account['activeAgents']
        mdr_status = mdr_status_check(account_name)
        if mdr_status is True and active_agents != 0:
            temp_dict = {
                "Account Name": account_name,
                "Active Agents": active_agents
            }
            account_dict[account_id] = temp_dict
    return account_dict

def mdr_status_check(account_name):
    if 'DNM' in account_name.upper():
        mdr_status = False
    elif ' IR ' in account_name.upper():
        mdr_status = False
    elif 'APAC' in account_name.upper():
        mdr_status = False
    elif 'TT-' in account_name.upper():
        mdr_status = False
    elif 'EXP' in account_name.upper():
        mdr_status = False
    else:
        mdr_status = True
    return mdr_status

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Version: 0.1 - This script gets alerts')
    required = parser.add_argument_group('Required Arguments')
    parser.add_argument("-a", "--account", dest="account", help="Account", required=False, default='ALL')
    parser.add_argument("-c", "--console", dest="console", help="Input Console i.e. EU, US", required=False, default="US")
    args = parser.parse_args()
    main(args)
