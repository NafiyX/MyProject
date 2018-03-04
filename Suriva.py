# -*- coding:utf-8 -*-
import requests
import json
import csv
import os
import re
from bs4 import BeautifulSoup

# 登录
def login():
    print("登录监控系统....")
    global s
    s = requests.session()
    login_url = 'http://21.152.2.72:8080/default/coframe/auth/login/org.gocom.components.coframe.auth.login.login.flow'
    login_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0',
                'Accept': 'text/html, application/xhtml+xml, */*',
                'Accept-Language': 'zh-CN',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': 'http://21.152.2.72:8080/default/coframe/auth/login/login.jsp',
                'Content-Language': 'zh-CN'
                }
    userId = '1407193'
    password = 'xif745655'
    login_data = {
            'userId': userId,
            'password': password
              }
    print('用户名：' + userId)
    login_sys = s.post(login_url, data=login_data, headers=login_header)
    return login_sys

def get_info(sysid):
    BANCS_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN',
                'Content-Type': 'application/json; charset=UTF-8',
                'Referer': 'http://21.152.2.72:8080/default//zfqsjk/ywsjcx/ywcx/gjhccx.jsp',
                'Content-Language': 'zh-CN',
                'Content-Length': '399'
                }
    BANCS_url = 'http://21.152.2.72:8080/default//zfqsjk/ywsjcx/ywcx/com.primeton.eos.zfqsjk.ywsjcx_ywcx.getgjhccx.biz.ext'
    BANCS_data = {"filename":"国际汇出查询",
               "_criteria_/orgId":"21",
               "orgname":"中国银行广西壮族自治区分行",
               "_criteria_/business_no":"",
               "_criteria_/pay_curr":"",
               "_criteria_/pay_amt":"",
               "_criteria_/benf_no":"",
               "_criteria_/acct_no":"",
               "_criteria_/tranTime_begin":"20180201",
               "_criteria_/tranTime_end":"20180213",
               "pageIndex":0,
               "pageSize":20,
               "sortField":"",
               "sortOrder":"",
               "page": {
                        "begin":0,
                        "length":20
                        }
               }
    post_data = json.dumps(BANCS_data, separators=(',', ':'), ensure_ascii=False)
    post_data = bytes(post_data, 'utf-8')
    BANCS = s.post(BANCS_url, data=post_data, headers=BANCS_header)
    mylist = BANCS.json()

with open(r'd:\tmp.json','w') as j:
    json.dump(mylist, j)
print(mylist)
