# -*- coding:utf-8 -*-
import requests
import datetime
import csv
import os
import re
from bs4 import BeautifulSoup


# 登录
def login():
    print("登录反洗钱系统....")
    global s
    s = requests.session()
    loginurl = 'http://11.4.17.176/amlmasrt/login.do'
    post_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Referer': 'http://11.4.17.176/amlmasrt/login.do',
                'Content-Language': 'zh-CN'
                  }
    userId = '1407193A'
    userPwd = 'xif745622'
    logindata = {'userId': userId, 'userPwd': userPwd, 'bankid': 'null', 'force': 'true'}
    print('用户名：' + userId)
    loginaml = s.post(loginurl, data=logindata, headers=post_header)
    return loginaml.status_code


def login_off():
    exit_url = 'http://11.4.17.176/amlmasrt/logout.do?uniqueuserid=1407193A'
    post_header = {
        'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
        'Accept': 'text/html, application/xhtml+xml, */*',
        'Accept-Language': 'zh-CN',
        'Accept-Encoding': 'gzip, deflate, peerdist',
        'Referer': 'http://11.4.17.176/amlmasrt/login.do'
                  }
    s.get(exit_url, headers=post_header)
    print('登出反洗钱系统')


# 获取列表
def getlist(strdate, enddate, sysid, bizno=''):
    total = 10
    if sysid == 'BANCS' or sysid == 'CIPSS' or sysid == 'RCPSR':
        location = 'A0021'
    else:
        location = ''
    listurl = 'http://11.4.17.176/amlmasrt/sanctionCaseListTrans.do'
    post_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Referer': 'http://11.4.17.176/amlmasrt/preSanctionCaseListTrans.do?pageflag=24&uniqueuserid=1407193',
                'Content-Language': 'zh-CN'
                }
    listdata = {'query_cadtype': '3',  # 案例类型
                'query_desc': '在线检索',  # 案例描述
                'orgno': '00001',  # 当前用户机构号
                'checkuserid': '',  # 复核柜员
                'operateresult': '',
                'caseOperType': '',  # 历史交易标识his
                'query_status': '4',  # 案例状态
                'query_casGenStartDt': strdate,  # 案例生成开始日期
                'query_casGenEndDt': enddate,  # 案例生成结束日期
                'query_sysid': sysid,  # 来源系统
                'query_caseid': '',  # 案例号
                'query_location': location,  # 查询机构
                'query_entityid': '',  # 客户号
                'query_custtype': '',  # 客户类型
                'query_entityname': '',  # 客户名称
                'query_idnumber': '',  # 客户证件号
                'query_gts_businessno': '',  # GTS业务编号
                'query_uniquereqid': bizno,  # 交易请求号(业务编号)
                'query_serialno': '',
                'query_tellerid': '',
                'query_isrejected': '',
                'query_isdealy': '',
                'query_20code': '',  # 20场编号
                'query_amount': '',
                'query_currency': '',
                'query_cad_txndate': '',
                'query_cad_valuedt': '',
                'query_is_locked': '',
                'query_next_assignee': '',
                'query_isofac': '',
                'query_ismt110': '',
                'query_mid': '',
                'page': '1',
                'rows': total
                }
    getlist = s.post(listurl, data=listdata, headers=post_header)
    san_list = getlist.json()
    total = san_list['total']
    listdata['rows'] = total
    getlist = s.post(listurl, data=listdata, headers=post_header)
    san_list = getlist.json()
    return san_list


# 爬取案例
def getcase(caseid, sysid,i):
    post_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'Referer': 'http://11.4.17.176/amlmasrt/preSanctionCaseListTrans.do?pageflag=24&uniqueuserid=1407193',
                    'Content-Language': 'zh-CN'
                  }
    black_title = ['CASEID', 'BUSSNO', 'HITFIELD', 'KEYWORD', 'SCORE', 'LSTNM', 'SYSID', 'KEYID']
    black_row = {}
    case_row = {}
    case_title = []
    col0 = []
    col3 = []
    case_url = 'http://11.4.17.176/amlmasrt/sancCaseInfoTrans.do?cid=' + caseid + '&infopagetype=view' # + '&caseOperType=his'
    case = s.get(case_url, headers=post_header)
    bsobj = BeautifulSoup(case.text, 'lxml')
    titles = bsobj.find_all('th', {'class': 'td_title_sancase'}, limit=13)  # 案例处理字段名
    data = bsobj.find_all('td', {'class': 'td_content_sancase'}, limit=13)  # 案例处理信息
    table = bsobj.find('table', {'id': 'table'})  # 报文信息
    # 爬取案例详情页面表格
    x = 0
    for title in titles:
        case_title.append(title.get_text(strip=True))
        x = x + 1
    x = 0
    for dat in data:
        case_row[case_title[x]] = dat.get_text(strip=True)
        x = x + 1
    case_row[case_title[0]] = caseid
    x = 0
    for td in table.find_all('tr'):
        cells = td.find_all('td')
        # 判断该场次是否命中
        if td.find(class_='listbtn'):
            black_list = td.find(class_='listbtn')['onclick']
            # 获取black_listDetail里的字符坐标
            listnameX = black_list.index("'", 18)
            listnameY = black_list.index("'", listnameX + 1)
            keyX = black_list.index("'", listnameY + 1)
            keyY = black_list.index("'", keyX + 1)
            scoreX = black_list.index("'", keyY + 1)
            scoreY = black_list.index("'", scoreX + 1)
            datsysidX = black_list.index("'", scoreY + 1)
            datsysidY = black_list.index("'", datsysidX + 1)
            uidX = black_list.index("'", datsysidY + 1)
            uidY = black_list.index("'", uidX + 1)
            keyid = black_list.rindex(",")
            black_row[black_title[0]] = caseid
            black_row[black_title[1]] = black_list[uidX + 1:uidY]
            black_row[black_title[2]] = cells[0].get_text(strip=True)
            black_row[black_title[3]] = black_list[keyX + 1:keyY]
            black_row[black_title[4]] = black_list[scoreX + 1:scoreY]
            black_row[black_title[5]] = black_list[listnameX + 1:listnameY]
            black_row[black_title[6]] = black_list[datsysidX + 1:datsysidY]
            black_row[black_title[7]] = black_list[keyid + 2:-2]

        # 爬取报文信息
        if 0 < x < 4:
            cellstr = cells[0].get_text()
            cellK = cellstr.index('：')
            cellV = cellstr.rindex('：')
            case_row[cellstr[:cellK]] = cellstr[cellV + 1:]
        elif x > 4:
            if sysid == 'BANCS':
                if cells[3].get_text(strip=True):
                    col0.append(cells[0].get_text(strip=True))
                    col3.append(cells[3].get_text(strip=True))
                if not cells[1].get_text(strip=True):
                    x = x + 1
                    continue
                elif cells[0].get_text(strip=True) == '59' and re.search('57[AD]', str(case_row.keys())):
                    if cells[1].get_text(strip=True) != case_row[re.search('57[AD]', str(case_row.keys())).group()]:
                        case_row[cells[0].get_text(strip=True)] = cells[1].get_text(strip=True)
                else:
                    case_row[cells[0].get_text(strip=True)] = cells[1].get_text(strip=True)
            elif sysid == 'RCPSR':
                if cells[0].get_text(strip=True) =='中介机构行号' or cells[0].get_text(strip=True)\
                        == '中介机构行名' or cells[0].get_text(strip=True) == '清算行行号':
                    col3.append(cells[3].get_text(strip=True))
                else:
                    case_row[cells[0].get_text(strip=True)] = cells[3].get_text(strip=True, separator='$$')
            else:
                case_row[cells[0].get_text(strip=True)] = cells[3].get_text(strip=True, separator='$$')
        x = x + 1
    if len(col0) != 0:
        y = 0
        while y <= len(col0) - 1:
            if col0[y] in case_row.keys() and not '70' in case_row.keys():
                case_row[col0[y]] = col3[y] + '$$' + case_row[col0[y]]
            else:
                case_row[col0[y]] = col3[y]
            y = y + 1
    h_url = 'http://11.4.17.176//amlmasrt/sancCaseHistoryTrans.do?caseid=' + caseid # +&CAD_SYSID= + sysid
    history = s.get(h_url, headers=post_header)
    h_table = BeautifulSoup(history.text, 'lxml').find('table', {'class': 'findnaTable'})
    x = 0
    for tr in h_table.find_all('tr'):
        x = x + 1
    j = 0
    for tr in h_table.find_all('tr'):
        if j == x - 2:
            y = 0
            for td in tr.find_all('td'):
                if y == 1:
                    case_row['MODIFYTIME1'] = td.get_text(strip=True)
                if y == 4:
                    case_row['OPERATE1'] = td.get_text(strip=True)
                y = y + 1
        if j == x - 1:
            y = 0
            for td in tr.find_all('td'):
                if y == 1:
                    case_row['MODIFYTIME2'] = td.get_text(strip=True)
                if y == 4:
                    case_row['OPERATE2'] = td.get_text(strip=True)
                y = y + 1
        j = j + 1
    case_row['VALUEDT'] = san_list['rows'][i]['CAD_VALUEDT']
    case_row['CURRENCY'] = san_list['rows'][i]['CAD_CURRENCY']
    case_row['AMOUNT'] = san_list['rows'][i]['CAD_AMOUNT']
    case_row['BRID'] = san_list['rows'][i]['CAD_LOCATION']
    case_row['TXNDATE'] = san_list['rows'][i]['CAD_TXNDATE']
    case_row['ISOFAC'] = san_list['rows'][i]['CAD_ISOFAC']
    case_row['ISMT110'] = san_list['rows'][i]['CAD_ISMT110']
    del case_row['']
    title_trans(case_row)
    return case_row, black_row


# 更换字段名
def title_trans(case_info):
    filepath = 'Title\TitleTrans.txt'
    title = {}
    try:
        with open(filepath, encoding='utf-8') as f:
            for line in f:
                (key, value) = line.strip().split(':')
                title[key] = value
    except IOError:
        print(filepath + ' 文件不存在')
        os._exit(0)

    for key in title.keys():
        if key in case_info.keys():
            case_info[title[key]] = case_info.pop(key)
    #print(case_info)
    return case_info


# 储存
def store(date, sysid, black_rows, case_rows):
    filepath = r'RawData\AML\\'
    file_title = r'Title\\' + sysid + '.txt'
    san_title = []
    black_title = []
    case_title = []
    for title in san_list['rows'][0].keys():
        san_title.append(title)
    for title in black_rows[0].keys():
        black_title.append(title)

    with open(file_title, encoding='utf-8') as t:
        for line in t:
            value = line.strip().split(',')
            case_title.append(value[0])

    with open(filepath + 'CaseList' + '_' + sysid + '_' + date + '.csv', 'w', newline='', errors='ignore') as f:  # 字段名和值写入CSV
        f_csv = csv.DictWriter(f, san_title)
        f_csv.writeheader()
        f_csv.writerows(san_list['rows'])

    with open(filepath + 'BlackInfo' + '_' + sysid + '_' + date + '.csv', 'w', newline='', errors='ignore') as f:
        f_csv = csv.DictWriter(f, black_title)
        f_csv.writeheader()
        f_csv.writerows(black_rows)

    with open(filepath + 'CaseInfo' + '_' + sysid + '_' + date + '.csv', 'w', newline='', errors='ignore') as f:
        f_csv = csv.DictWriter(f, case_title)
        f_csv.writeheader()
        f_csv.writerows(case_rows)
    print('写入CSV文件完成，文件地址：' + filepath)


#def log():



# 程序入口
def main():
    strdate = '2018/02/01'
    enddate = '2018/02/28'
    sysids = ['BANCS', 'GPG', 'CIPSS', 'CIPSR', 'RCPSR', 'GUPP']
    flag = int(input('输入系统标识(1-BANCS(汇出-GX)，2-BANCS(汇入-HQ), 3-BCIPS(汇出-GX),'
                     ' 4-BCIPS(汇入-HQ), 5-RCPS(汇入-GX)：'))
    while flag > 5:
            print('输入有误请重新输入')
            flag = int(input('输入系统标识(1-BANCS(汇出-GX)，2-BANCS(汇入-HQ), 3-BCIPS(汇出-GX),'
                     ' 4-BCIPS(汇入-HQ), 5-RCPS(汇入-GX)：'))
    sysid = sysids[flag-1]
    #strdate = str(input('输入开始日期：'))
    #enddate = str(input('输入结束日期：'))
    loginaml = login()
    if loginaml == 200:
        print('登录成功')
    else:
        print('登录不成功，程序终止')
        os._exit(0)
    getlist(strdate, enddate, sysid)
    print(sysid + '——' + strdate + '——' + enddate + '---共' + str(san_list['total']) + '笔案例')

    case_rows = []
    black_rows = []
    i = 0
    while i <= len(san_list['rows'])-1:
        caseid = san_list['rows'][i]['CAD_CASEID']
        case_info = getcase(caseid, sysid, i)
        case_rows.append(case_info[0])
        black_rows.append(case_info[1])
        i = i + 1
        print(i)
    print('抓取案例完成')
    login_off()
    store('201802', sysid, black_rows, case_rows)


def main1():
    ystday = datetime.date.today() + datetime.timedelta(-1)
    sysids = ['BANCS', 'CIPSS']     # BANCS(汇出-GX)，BANCS(汇入-HQ),BCIPS(汇出-GX),BCIPS(汇入-HQ),RCPS(汇入-GX
    loginaml = login()
    if loginaml == 200:
        print('登录成功!')
    else:
        print('登录不成功，程序终止!')
        os._exit(0)

    for sysid in sysids:
        total = getlist(ystday, ystday, sysid)
        if total == 0:
            print(sysid + '***'+str(ystday) + '***无业务发生')
            continue
        print(sysid + '***' + str(ystday) + '***' + str(san_list['total']) + '笔案例,开始抓取...')
        case_rows = []
        black_rows = []
        i = 0
        while i <= len(san_list['rows'])-1:
            caseid = san_list['rows'][i]['CAD_CASEID']
            case_info = getcase(caseid, sysid, i)
            case_rows.append(case_info[0])
            black_rows.append(case_info[1])
            i = i + 1
            #print(i)
        print('抓取' + sysid + '案例完成,开始写入文件...')
        store(str(ystday.strftime('%Y%m%d')), sysid, black_rows, case_rows)
    login_off()
    print('程序结束！')


if __name__ == '__main__':
    main1()
