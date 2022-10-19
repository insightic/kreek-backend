import copy
import random
import string

import os
from django.http import HttpResponse
import json
from functools import wraps
from .dbconfig import *
from .const import *
from bson import json_util
from .tools import *
from django.core.cache import cache
import datetime
from .user import check_parameters
import requests

# invset_plan = {
#     "invest_ID": 2022_0729_000232_0,
#     "user_ID": "xiehou_0",
#     "invest_amount": 1000000000000000000000,
#     "crypto_spent": "bep20_usdt",
#     "crypto_get": "bep20_btc",
#     "chain": "BEP20 (BSC)",
#     "start_date": "1659024000",
#     "end_date": "1798732800", // optional
#     "recurrence_rule": {
#         "frequency": "by_day",
#         "by_day": 7,
#         "by_month": null
#     }
# }



#test
def test(request):
    username = "xiehou_"
    pswd = "123456"
    
    for i in range(0, 7):
        user = {"username": username + str(i),
            "pswd": pswd,
            "nickname": username + str(i),
            "role": "user",
            "profile": "user.png",
            "status": True,
            "btc_amount": 0,
            "chainAddresses": []}
        myauths.insert_one(user)
        
    return json_wrap({"status": 200, "data": "test"}, no_response=True)

def test2(request):
    username = "xiehou_"
    create_time = timestamp_now()
    start_time = (int(create_time / DAY) + 1) * DAY
    
    for i in range(0, 7):
        invest_cycle = ((i % 7) + 1) * DAY
        plan = {"username": username + str(i),
            "create_time": create_time,
            "start_time": start_time,
            "invest_cycle": invest_cycle,
            "invest_amount": 1000000000000} # wei
        plans.insert_one(plan)
        
    return json_wrap({"status": 200, "data": "test"}, no_response=True)


# @check_parameters(["invest_ID", "uid", "invest_amount", "crypto_spent", "crypto_get", "chain", "start_date", "end_condition", "frequency", "invest_cycle"])
def newInvestPlan(request):
    # print(request.POST)
    params = request.POST

    create_time = timestamp_now()
    invest_ID = params["invest_ID"]
    uid = params["uid"]
    plan_name = params["plan_name"]
    invest_amount = float(params['invest_amount']) * (10 ** 18)
    crypto_spent = params["crypto_spent"]
    crypto_get = params["crypto_get"]
    chain = params["chain"]
    start_date = int(params["start_date"])
    end_condition = params["end_condition"]
    frequency = params["frequency"]
    invest_cycle = int(params['invest_cycle'])

    plan = {"invest_ID": invest_ID,
            "uid": uid,
            "plan_name": plan_name,
            "invest_amount": invest_amount,
            "crypto_spent": crypto_spent,
            "crypto_get": crypto_get,
            "chain": chain,
            "start_date": start_date,
            "end_condition": end_condition,
            "frequency": frequency,
            "invest_cycle": invest_cycle,
            "create_time": create_time,
            "logs":[]}
    plans.insert_one(plan)

    return json_wrap({"status": 200, "msg": "Invest Plan has been successfully submitted, please wait for our platform to adjust your account!"})



def changeInvestPlan(request):
    # print(request.POST)
    params = request.POST

    invest_ID = params["invest_ID"]
    uid = params["uid"]
    plan_name = params["plan_name"]
    invest_amount = float(params['invest_amount']) * (10 ** 18)
    crypto_spent = params["crypto_spent"]
    crypto_get = params["crypto_get"]
    chain = params["chain"]
    start_date = int(params["start_date"])
    end_condition = params["end_condition"]
    frequency = params["frequency"]
    invest_cycle = int(params['invest_cycle'])

    try:
        plans.update_one({"invest_ID": invest_ID}, {'$set': {
                                                                "plan_name": plan_name,
                                                                "invest_amount": invest_amount,
                                                                "crypto_spent": crypto_spent,
                                                                "crypto_get": crypto_get,
                                                                "chain": chain,
                                                                "start_date": start_date,
                                                                "end_condition": end_condition,
                                                                "frequency": frequency,
                                                                "invest_cycle": invest_cycle,
                                                            }})
        return HttpResponse(json.dumps({"status": 200, "code": 200, "msg": "Success"}),
                            content_type="application/json")
    except requests.exceptions.Timeout as e:
        print(e)
        return NoLogHTTPResponse(
                        json.dumps({"status": 200, "code": 400, "msg": "No such plan"}),
                        content_type="application/json")



def getInvestPlans(request):
    # print(request.POST)
    uid = request.POST['uid']

    result = list(plans.find({"uid": uid},
                                {
                                    "invest_ID": 1,
                                    "uid": 1, 
                                    "plan_name": 1,
                                    "invest_amount": 1, 
                                    "crypto_spent": 1,
                                    "crypto_get": 1,
                                    "chain": 1,
                                    "start_date": 1,
                                    "end_condition": 1,
                                    "frequency": 1,
                                    "invest_cycle": 1,
                                }))

    result = json_util.dumps(result)
    return json_wrap({"status": 200, "result": result})



def getLogs(request):
    invest_ID = request.POST['invest_ID']

    try:
        result = list(plans.find({"invest_ID": invest_ID}, {"logs": 1}))[0]
    except Exception as e:
        return NoLogHTTPResponse(
                        json.dumps({"status": 400, "msg": "No such plan"}),
                        content_type="application/json")

    result = json_util.dumps(result)
    return json_wrap({"status": 200, "result": result})





