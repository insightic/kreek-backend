"""
User info management (login, register, check_login, etc)
"""
import random
import string
import json
from datetime import datetime
import os
from django.http import HttpResponse
import json
from functools import wraps
from .dbconfig import *
from bson import json_util
from .tools import *
from .const import *
from django.core.cache import cache
from .emails import send_mail
import requests




def hello(request):
    return json_wrap({"msg": "Hello world!"}, no_log=True)


def S04(request, exception):  # 404页面
    return json_wrap({"msg": "404!"}, no_log=True)


def S500(request):
    import traceback
    error = str(traceback.format_exc())
    return json_wrap({"status": 500, "msg": "Server Internal Error!", "info": error}, no_log=True)


# 查找参数是否在请求中
def check_parameters(paras):
    def _check_parameter(f):
        @wraps(f)
        def inner(request, *arg, **kwargs):
            for para in paras:
                if para in request.GET or para in request.POST:
                    continue
                else:
                    return NoLogHTTPResponse(
                        json.dumps({"status": 400, "msg": "Not specify required parameters: " + para + "!"}),
                        content_type="application/json")
            return f(request, *arg, **kwargs)

        return inner

    return _check_parameter


# @check_parameters(["uid", "nickname"])
def login(request):
    try:
        uid = request.POST['uid']
        nickname = request.POST['nickname']
        result = myauths.find({"uid": uid})
        r = list(result)
    except Exception as e:
        print(e)
        return NoLogHTTPResponse(
                        json.dumps({"status": 400, "msg": e}),
                        content_type="application/json")
    
    if len(r) == 0:  # 没找到值
        user = {
            "uid": uid, 
            "nickname": nickname,
            "chain_addresses": [],
            "balances": {
                            "bep20_btc": 0,
                            "bep20_eth": 0,
                            "bep20_xrp": 0
                        },
            "invest_plans": []
        }
        myauths.insert_one(user)

        try:
            params = {
                "uid": uid,
                "chain": "BEP20 (BSC)"
            }
            # print(params)
            # r = requests.get('http://currency.naibo.wang:8081/currency_backend/testDelay?type='+type, timeout=10)
            r = requests.post(WEB3_BACKEND_URL + "createAddress", data=params,timeout=600)
            res = json.loads(r.text)
            if res["status"] == 0:
                return NoLogHTTPResponse(
                        json.dumps({"status": 400, "msg": "createAddress error!"}),
                        content_type="application/json")

        except requests.exceptions.Timeout as e:
            print(e)
            return NoLogHTTPResponse(
                        json.dumps({"status": 400, "msg": e}),
                        content_type="application/json")

        try:
            params = {
                "uid": uid,
                "chain": "BEP20 (BSC)",
                "BNBAmount": 10000000000000000,
            }
            # print(params)
            # r = requests.get('http://currency.naibo.wang:8081/currency_backend/testDelay?type='+type, timeout=10)
            r = requests.post(WEB3_BACKEND_URL + "autoTopUp", data=params,timeout=600)
            res = json.loads(r.text)
            if not res:
                return NoLogHTTPResponse(
                        json.dumps({"status": 400, "msg": "autoTopUp error!"}),
                        content_type="application/json")
        except requests.exceptions.Timeout as e:
            print(e)
            return NoLogHTTPResponse(
                        json.dumps({"status": 400, "msg": e}),
                        content_type="application/json")

        user = list(myauths.find({"uid": uid}))[0]
        user["chain_addresses"][0]["privateKey"] = ""
        user = json_util.dumps(user)

        return HttpResponse(json.dumps({"status": 200, "result": user}),
                            content_type="application/json")
    else:
        user = r[0]
        user = json_util.dumps(user)
        
        return HttpResponse(json.dumps({"status": 200, "result": user}),
                            content_type="application/json")



def changeNickname(request):
    try:
        uid = request.POST["uid"]
        nickname = request.POST["nickname"]
    except Exception as e:
        print(e)
        return NoLogHTTPResponse(
                        json.dumps({"status": 400, "msg": e}),
                        content_type="application/json")

    try:
        myauths.update_one({"uid": uid}, {'$set': {"nickname": nickname}})
        return HttpResponse(json.dumps({"status": 200, "msg": "Success"}),
                            content_type="application/json")
    except requests.exceptions.Timeout as e:
        print(e)
        return NoLogHTTPResponse(
                        json.dumps({"status": 400, "msg": "No such user"}),
                        content_type="application/json")

