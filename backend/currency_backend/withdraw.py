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


def withdraw(request):
    params = request.POST
    
    uid = params["uid"]
    token = params["token"]
    chain = params["chain"]
    addressTo = params["addressTo"]
    amount = float(params['amount']) * (10 ** 18)

    output = {"status": 200, "code":200, "msg": "withdrawing"}
    try:
        params = {
            "uid": uid,
            "token": token,
            "chain": chain,
            "addressTo": addressTo,
            "amount": amount
        }
        r = requests.post('http://localhost:8080/withdraw/', data=params, timeout=600)
        # print(r.text)
    except requests.exceptions.Timeout as e:
        print(e)
        output["code"] = 500
        output["msg"] = "Sorry, we cannot process the withdraw request now!"

    return json_wrap(output)
