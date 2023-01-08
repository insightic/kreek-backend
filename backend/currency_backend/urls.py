"""currency_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from . import user, plan, withdraw


def path_c(pt, func):
    return path("currency_backend/" + pt, func)


urlpatterns = [
    path_c('test', plan.test),
    path('', user.hello),
    path('', user.hello),
    path_c('', user.hello),
    path_c('login', user.login),
    path_c('changeNickname', user.changeNickname),
    path_c('newInvestPlan', plan.newInvestPlan),
    path_c('changeInvestPlan', plan.changeInvestPlan),
    path_c('getInvestPlans', plan.getInvestPlans),
    path_c('withdraw', withdraw.withdraw),
    path_c('getLogs', plan.getLogs)
]

handler404 = user.S04
handler500 = user.S500
