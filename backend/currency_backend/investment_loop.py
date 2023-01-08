import copy
import random
import string

import os
import json
from functools import wraps
from dbconfig import *
from bson import json_util
from tools import *
import datetime
import random
import requests
import copy

scheme_template = {
    "id": 0,
    "username": "",
    "create_time": "",
    "start_time": "",
    "invest_cycle": 0, # 以秒为单位的timestamp
    "invest_amount": 0,
}

# dic to store the invest amount of each crypto pair
T0 = {}
T0["bep20_usdt"] = {}

T0["bep20_usdt"]["bep20_btc"] = 0
T0["bep20_usdt"]["bep20_eth"] = 0
T0["bep20_usdt"]["bep20_xrp"] = 0

timestamp_zero = int(timestamp_now() / DAY) * DAY

def swapTokenCHW(tokenSpent, tokenGet, tokenSpentAmount):
    try:
        if tokenSpentAmount == 0:
            return 0

        params = {
            "tokenSpent": tokenSpent,
            "tokenGet": tokenGet,
            "amount": tokenSpentAmount
        }
        # print(params)
        # r = requests.get('http://currency.naibo.wang:8081/currency_backend/testDelay?type='+type, timeout=10)
        r = requests.post('http://localhost:8080/swapTokenCHW/', data=params,timeout=600)
        res = json.loads(r.text)
        if res["status"] == 0:
            print("swapTokenCHW error!")
            return 0
        tokenGetAmount = int(res["getAmount"])
        return tokenGetAmount
    except requests.exceptions.Timeout as e:
        print(e)
        return 0

while True:
    print(timestamp_now())

    # sleep until the next day
    sleep_time = DAY - (timestamp_now() % DAY)
    time.sleep(sleep_time)
    timestamp_zero += DAY
    print(timestamp_zero)

    # start investment
    T = copy.deepcopy(T0)

    all_plans = list(plans.find({},
                                {
                                    "invest_ID": 1,
                                    "uid": 1, 
                                    "invest_amount": 1, 
                                    "crypto_spent": 1,
                                    "crypto_get": 1,
                                    "chain": 1,
                                    "start_date": 1,
                                    "end_condition": 1,
                                    "frequency": 1,
                                    "invest_cycle": 1,
                                }))


    # find all the plans that invest today
    plans_today = []
    for item in all_plans:
        # check the end date
        end_condition_arr = item["end_condition"].split(" ")
        if end_condition_arr[0] == "endDate":
            end_date = int(end_condition_arr[1])
            if timestamp_zero >= end_date:
                continue

        if item["frequency"] == "byDay":
            time_interval = timestamp_zero - item["start_date"]
            if time_interval > 0 and time_interval % (item["invest_cycle"] * DAY) == 0:
                
                # call web3 txn to tranfer the token to the hot wallet
                try:
                    params = {
                        "uid": item["uid"],
                        "chain": "BEP20 (BSC)",
                        "token": item["crypto_spent"],
                        "amount": item["invest_amount"]
                    }
                    r = requests.post('http://localhost:8080/sendTokenToCHW/', data=params, timeout=600)
                    res = r.text
                    if res == "true":
                        plans_today.append(item)
                        T[item["crypto_spent"]][item["crypto_get"]] += item["invest_amount"]
                    else:
                        print(item["uid"] + " send token byDay error!")

                    
                except requests.exceptions.Timeout as e:
                    print(item["uid"] + " send token byDay error!")

                

        if item["frequency"] == "byMonth":
            start_date = datetime.datetime.fromtimestamp(item["start_date"])
            current_date = datetime.datetime.fromtimestamp(timestamp_zero)

            if start_date.day == current_date.day:
                if ((current_date.year - start_date.year) * 12 + (current_date.month - start_date.month)) % item["invest_cycle"] == 0:
                    
                    # call web3 txn to tranfer the token to the hot wallet
                    output = {"status": 200, "msg": "Transferring USDT to the Creek hot wallet"}
                    try:
                        params = {
                            "uid": item["uid"],
                            "chain": "BEP20 (BSC)",
                            "token": item["crypto_spent"],
                            "amount": item["invest_amount"]
                        }
                        r = requests.post('http://localhost:8080/sendTokenToCHW/', data=params, timeout=600)
                        res = r.text
                        if res:
                            plans_today.append(item)
                            T[item["crypto_spent"]][item["crypto_get"]] += item["invest_amount"]
                        else:
                            print(item["uid"] + " send token byMonth error!")
                            
                    except requests.exceptions.Timeout as e:
                        print(item["uid"] + " send token byMonth error!")

                    

    approve_flag = True
    # approve token amount for today
    for srcToken in T.keys():
        approveAmount = 0
        for dstToken in T[srcToken].keys():
            approveAmount += T[srcToken][dstToken]
            
        output = {"status": 200, "msg": "Approving srcToken to pancake_router"}
        try:
            if approveAmount == 0:
                continue
            params = {
                "token": srcToken,
                "amount": approveAmount
            }
            r = requests.post('http://localhost:8080/approveTokenCHW/', data=params, timeout=600)
            res = r.text
            if not res:
                approve_flag = False
                print("approve error!")
            # print(r.text)
        except requests.exceptions.Timeout as e:
            print(e)
            print("approve error!")
            approve_flag = False

    if not approve_flag:
        continue


    # swapToken, call web3_backend
    # t = T["bep20_usdt"]["bep20_btc"] * 0.999
    tokenGetAmount = copy.deepcopy(T0)

    # 0AM + rand(0, 4)
    time_buy_0 = int(random.uniform(0, 4) * HOUR) + timestamp_zero
    sleep_time_0 = time_buy_0 - timestamp_now()
    if sleep_time_0 > 0:
        time.sleep(sleep_time_0)

    for srcToken in T.keys():
        for dstToken in T[srcToken].keys():
            swapResult = swapTokenCHW("bep20_usdt", dstToken, int(T["bep20_usdt"][dstToken] / 4))
            tokenGetAmount["bep20_usdt"][dstToken] += swapResult
            log = {
                "spent_amount": int(T["bep20_usdt"][dstToken] / 4), 
                "get_amount": swapResult, 
                "crypto_spent": srcToken,
                "crypto_get": dstToken,
                "timestamp": time_buy_0
            }

    # 0AM + rand(4, 8)
    time_buy_1 = int(random.uniform(4, 8) * HOUR) + timestamp_zero
    sleep_time_1 = time_buy_1 - timestamp_now()
    if sleep_time_1 > 0:
        time.sleep(sleep_time_1)

    for srcToken in T.keys():
        for dstToken in T[srcToken].keys():
            swapResult = swapTokenCHW("bep20_usdt", dstToken, int(T["bep20_usdt"][dstToken] / 4))
            tokenGetAmount["bep20_usdt"][dstToken] += swapResult
            log = {
                "spent_amount": int(T["bep20_usdt"][dstToken] / 4), 
                "get_amount": swapResult, 
                "crypto_spent": srcToken,
                "crypto_get": dstToken,
                "timestamp": time_buy_1
            }

    # 0AM + rand(8, 12)
    time_buy_2 = int(random.uniform(8, 12) * HOUR) + timestamp_zero
    sleep_time_2 = time_buy_2 - timestamp_now()
    if sleep_time_2 > 0:
        time.sleep(sleep_time_2)

    for srcToken in T.keys():
        for dstToken in T[srcToken].keys():
            swapResult = swapTokenCHW("bep20_usdt", dstToken, int(T["bep20_usdt"][dstToken] / 4))
            tokenGetAmount["bep20_usdt"][dstToken] += swapResult
            log = {
                "spent_amount": int(T["bep20_usdt"][dstToken] / 4), 
                "get_amount": swapResult, 
                "crypto_spent": srcToken,
                "crypto_get": dstToken,
                "timestamp": time_buy_2
            }

    # 0AM + rand(12, 16)
    time_buy_3 = int(random.uniform(12, 16) * HOUR) + timestamp_zero
    sleep_time_3 = time_buy_3 - timestamp_now()
    if sleep_time_3 > 0:
        time.sleep(sleep_time_3)

    for srcToken in T.keys():
        for dstToken in T[srcToken].keys():
            swapResult = swapTokenCHW("bep20_usdt", dstToken, int(T["bep20_usdt"][dstToken] / 4))
            tokenGetAmount["bep20_usdt"][dstToken] += swapResult
            log = {
                "spent_amount": int(T["bep20_usdt"][dstToken] / 4), 
                "get_amount": swapResult, 
                "crypto_spent": srcToken,
                "crypto_get": dstToken,
                "timestamp": time_buy_3
            }







    for plan in plans_today:

        # update the new balance
        tokenGetIncrement = int((plan["invest_amount"] / T[plan["crypto_spent"]][plan["crypto_get"]]) * tokenGetAmount[plan["crypto_spent"]][plan["crypto_get"]])
        user = list(myauths.find({"uid": plan["uid"]}))[0]
        newBalance = user["balances"][plan["crypto_get"]] + tokenGetIncrement
        myauths.update_one({"uid": plan["uid"]}, {'$set': {"balances." + plan["crypto_get"]: newBalance}})

        # record the log for this plan
        log = {
            "invest_amount": plan["invest_amount"], 
            "get_amount": tokenGetIncrement, 
            "crypto_spent": plan["crypto_spent"],
            "crypto_get": plan["crypto_get"],
            "chain": plan["chain"],
            "timestamp": timestamp_zero
        }
        plans.update_one({"invest_ID": plan["invest_ID"]}, 
                {'$push': {"logs": log}})

        

