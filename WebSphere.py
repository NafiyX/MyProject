# -*- coding:utf-8 -*-
import requests
from bs4 import BeautifulSoup


def login(userId, userPwd):
    print("登陆报表系统....")
    global s
    s = requests.session()
    login_url = 'http://21.123.22.101:9088/ODWEKWeb/ODLogon'
    post_header = {
        'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
        'Accept': 'text/html, application/xhtml+xml, */*',
        'Accept-Language': 'zh-CN',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'http://21.123.22.101:9088/ODWEKWeb/login.jsp'
                  }
    logindata = {'_user': userId, '_password': userPwd}
    print('用户名：' + userId)
    loginweb = s.post(login_url, data=logindata, headers=post_header)
    return loginweb.status_code


def login_off():
    exit_url = 'http://21.123.22.101:9088/ODWEKWeb/ODLogoff'
    post_header = {
        'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
        'Accept': 'text/html, application/xhtml+xml, */*',
        'Accept-Language': 'zh-CN',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'http://21.123.22.101:9088/ODWEKWeb/ODlogin'
                  }
    s.get(exit_url, headers=post_header)


def search(data_name, orgid, strdate, enddate):
    print('查询报表：' + data_name + ' 日期：' + strdate + '---' + enddate)
    search_url = 'http://21.123.22.101:9088/ODWEKWeb/ODSearch'
    search_post = {
        'folderName': '01.'+data_name,
        'orgid': 'Equal to',
        'orgidinput': orgid,
        'rptid': 'Equal to',
        'rptidinput': '',
        'dat': 'Between',
        'datinput1': strdate,
        'datinput': enddate,
        'sorgid': 'Equal to',
        'sorgidinput': '',
        'andOr': 'AND',
        'submit1': '查询'
                }
    post_header = {
        'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
        'Accept': 'text/html, application/xhtml+xml, */*',
        'Accept-Language': 'zh-CN',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'http://21.123.22.101:9088/ODWEKWeb/ODGetCriteria',
        'Accept-Encoding': 'gzip, deflate'
                  }
    search = s.post(search_url, data=search_post, headers=post_header)
    bsobj = BeautifulSoup(search.text, 'lxml')
    td_tags = bsobj.find_all('td', {'align': 'CENTER'})
    chick1 = ''
    now_selected = ''
    for td in td_tags:
        if td.find(id='chick1'):
            now_selected = now_selected + ',' + str(td.find(id='chick1')['value'])
            chick1 = chick1 + 'chick1=' + td.find(id='chick1')['value'] + '&'
    chick1 = chick1[:-1]
    all_selected_url = 'http://21.123.22.101:9088/ODWEKWeb/ODSelectAllHits2Session'
    all_selected = s.post(all_selected_url, headers=post_header)
    #  text = batch_download(data_name, all_selected, now_selected, chick1)
    return all_selected, now_selected, chick1


def batch_download(data_name, all_selected, now_selected, chick1):
    print('下载' + data_name + '报表')
    download_url = 'http://21.123.22.101:9088/ODWEKWeb/ODDocumentBatchDownload'
    post_header = {
        'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
        'Accept': 'text/html, application/xhtml+xml, */*',
        'Accept-Language': 'zh-CN',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'http://21.123.22.101:9088/ODWEKWeb/ODSearch',
        'Accept-Encoding': 'gzip, deflate'
    }
    batch_download = {
        'folderName': '01.'+data_name,
        'all_selected': all_selected,
        'now_selected': now_selected,
        'no_selected': ''
        }
    download_post = ''
    for key in batch_download:
        download_post = download_post + key + '=' + str(batch_download[key]) + '&'
    download_post = download_post + chick1
    data = s.post(download_url, data=download_post, headers=post_header)
    data.encoding = 'gb18030'
    return data.text


def download(data_name):
    print('开始下载' + data_name + '报表')
    download_url = 'http://21.123.22.101:9088/ODWEKWeb/ODDocumentDownload'
    post_header = {
        'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
        'Accept': 'text/html, application/xhtml+xml, */*',
        'Accept-Language': 'zh-CN',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'http://21.123.22.101:9088/ODWEKWeb/ODSearch',
        'Accept-Encoding': 'gzip, deflate'
    }
    download_post = {'folderName': '01.'+data_name, 'hitsIndex': '0'}
    data = s.post(download_url, data=download_post, headers=post_header)
    data.encoding = 'gb18030'
    return data.text


def store(data, orgid, data_name, date):
    filepath = r'RawData\WebSphere\\'
    if not orgid == '':
        orgid = 'HQ'
        filename = orgid + data_name[4:] + '-' + date
    else:
        filename = data_name + '-' + date
    with open(filepath + filename, 'w', encoding='gb18030') as f:
        f.write(data)
    return filename
