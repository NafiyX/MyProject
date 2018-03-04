# -*- coding:utf-8 -*-
import requests, csv, re
from bs4 import BeautifulSoup

#定义变量
s = requests.session()
loginurl = 'http://11.4.17.176/amlmasrt/login.do'
listurl = 'http://11.4.17.176/amlmasrt/sanctionCaseListTrans.do'
userId = '1407193A'
userPwd = 'xif745622'
strdate = '2018/01/10'
enddate = '2018/01/10'
total = 10
#定义POST字典
logindata = dict(userId=userId, userPwd=userPwd, bankid='null', force='true')
listdata = {'query_cadtype':'3',                    #案例类型
            'query_desc':'在线检索',                #案例描述
            'orgno':'00001',                        #当前用户机构号
            'checkuserid':'',                       #复核柜员
            'operateresult':'',
            'caseOperType': '',
            'query_status':'',                      #案例状态
            'query_casGenStartDt': strdate,         #案例生成开始日期
            'query_casGenEndDt':enddate,            #案例生成结束日期
            'query_sysid':'BANCS',                  #来源系统
            'query_caseid':'',                      #案例号
            'query_location':'A0021',                    #查询机构
            'query_entityid':'',                    #客户号
            'query_custtype':'',                    #客户类型
            'query_entityname':'',                  #客户名称
            'query_idnumber':'',                    #客户证件号
            'query_gts_businessno':'',              #GTS业务编号
            'query_uniquereqid':'',                 #交易请求号(业务编号)
            'query_serialno':'',
            'query_tellerid':'',
            'query_isrejected':'',
            'query_isdealy':'',
            'query_20code':'',                      #20场编号
            'query_amount':'',
            'query_currency':'',
            'query_cad_txndate':'',
            'query_cad_valuedt':'',
            'query_is_locked':'',
            'query_next_assignee':'',
            'query_isofac':'',
            'query_ismt110':'',
            'query_mid':'',
            'page':'1',
            'rows':800
            }
detaildata = {}
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
          'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
          'Referer': 'http://11.4.17.176/amlmasrt/login.do',
          'Content-Language': 'zh-CN'}

#登陆AML及查询列表
login = s.post(loginurl, data=logindata, headers=header)
header['Referer'] = 'http://11.4.17.176/amlmasrt/preSanctionCaseListTrans.do?pageflag=24&uniqueuserid=1407193A'
getlist = s.post(listurl, data=listdata, headers=header)
sanlist = getlist.json()
print('共' + str(sanlist['total']) + '笔')
#将获得的列表写入Sanlist.CSV，并提取CASEID
caseidlist = []
i = 0       # 提取CASEID
while i <= len(sanlist['rows'])-1:
    caseidlist.append(sanlist['rows'][i]["CAD_CASEID"])
    i = i+1
headers = []
print(caseidlist)
for header in sanlist['rows'][0].keys():  # 字段名写入headers
    headers.append(header)
with open('d:\CaseList_Out_'+ strdate[5:7] + '.csv','w',newline='', errors='ignore') as f:  # 字段名和值写入CSV
    f_csv = csv.DictWriter(f, headers)
    f_csv.writeheader()
    f_csv.writerows(sanlist['rows'])

# 将提取的CASEID作为参数GET，获取命中名单详细信息
lreg = re.compile(".*：")
rreg = re.compile("：.*")
caseheader = []
caseinforows = []
blackheader = ['caseid', 'uid', 'hitfield', 'key', 'score', 'listname', 'datsysid', 'keyid']
blackrows = []
detailheader = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
          'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
          'Referer': 'http://11.4.17.176/amlmasrt/preSanctionCaseListTrans.do?pageflag=24&uniqueuserid=1407193',
          'Content-Language': 'zh-CN'}
caseinfo_H = ['案例号', '省行信息', '机构信息', '案例状态', '描述', '', '经办柜员号', '经办人姓名', '经办意见', '', '复核柜员号', '复核人姓名', '复核意见', 'MODIFYTIME1', 'OPERATE1', 'MODIFYTIME2', 'OPERATE2', '源系统名称', '交易请求号', '请求序列号', 'PMT', 'REC', '21', '30', '32B', '32A', '50K', '52A', '52D', '53A', '56A', '57A', '57D', '58A', '59', '70', '72']
i = 0

while i <= len(sanlist['rows'])-1:
    print(i+1)
    caseinforow = {}
    blackrow = {}
    col0 = []
    col3 = []
    detailurl = 'http://11.4.17.176/amlmasrt/sancCaseInfoTrans.do?cid=' + caseidlist[i] + '&infopagetype=view'
    detail = s.get(detailurl, headers=detailheader)
    bsobj = BeautifulSoup(detail.text, 'lxml')
    titles = bsobj.find_all('th', {'class': 'td_title_sancase'}, limit=13)  # 案例处理字段名
    data = bsobj.find_all('td', {'class': 'td_content_sancase'}, limit=13)  # 案例处理信息
    table = bsobj.find('table', {'id': 'table'})# 报文信息
    # 循环爬取案例详情页面表格
    x = 0
    for dat in data:
        caseinforow[caseinfo_H[x]] = dat.get_text(strip=True)
        x = x + 1
    caseinforow[caseinfo_H[0]] = caseidlist[i]

    x = 0
    print(table)
    for td in table.find_all('tr'):
        cells = td.find_all('td')
        # 判断该场次是否命中
        if td.find(class_='listbtn'):
            blacklist = td.find(class_='listbtn')['onclick']
            # 获取blacklistDetail里的字符坐标
            listnameX = blacklist.index("'", 18)
            listnameY = blacklist.index("'", listnameX + 1)
            keyX = blacklist.index("'", listnameY + 1)
            keyY = blacklist.index("'", keyX + 1)
            scoreX = blacklist.index("'", keyY + 1)
            scoreY = blacklist.index("'", scoreX + 1)
            datsysidX = blacklist.index("'", scoreY + 1)
            datsysidY = blacklist.index("'", datsysidX + 1)
            uidX = blacklist.index("'", datsysidY + 1)
            uidY = blacklist.index("'", uidX + 1)
            keyid = blacklist.rindex(",")
            blackrow[blackheader[0]] = caseidlist[i]
            blackrow[blackheader[1]] = blacklist[uidX + 1:uidY]
            blackrow[blackheader[2]] = cells[0].get_text(strip=True)
            blackrow[blackheader[3]] = blacklist[keyX + 1:keyY]
            blackrow[blackheader[4]] = blacklist[scoreX + 1:scoreY]
            blackrow[blackheader[5]] = blacklist[listnameX + 1:listnameY]
            blackrow[blackheader[6]] = blacklist[datsysidX + 1:datsysidY]
            blackrow[blackheader[7]] = blacklist[keyid + 2:-2]
            blackrows.append(blackrow.copy())
        # 爬取报文信息
        if 0 < x < 4:
            cellstr = cells[0].get_text()
            cellK = cellstr.index('：')
            cellV = cellstr.rindex('：')
            #caseinfo_H.append(cellstr[:cellK])
            caseinforow[cellstr[:cellK]] = cellstr[cellV+1:]
        elif x > 4:
            #TI,CIPS,RCPS caseinforow[cells[0].get_text(strip=True)] = cells[3].get_text(strip=True, separator='$$')
            #caseinforow[cells[0].get_text(strip=True)] = cells[3].get_text(strip=True, separator='$$')
            if cells[3].get_text(strip=True):
                col0.append(cells[0].get_text(strip=True))
                col3.append(cells[3].get_text(strip=True))
            if not cells[1].get_text(strip=True):
                x = x +1
                continue
            elif cells[0].get_text(strip=True) == '59' and re.search('57[AD]', str(caseinforow.keys())):
                    if cells[1].get_text(strip=True) != caseinforow[re.search('57[AD]', str(caseinforow.keys())).group()]:
                        caseinforow[cells[0].get_text(strip=True)] = cells[1].get_text(strip=True)
            else:caseinforow[cells[0].get_text(strip=True)] = cells[1].get_text(strip=True)
        x = x +1
    if len(col0) != 0:
        y = 0
        while y <= len(col0)-1:
            if col0[y] in caseinforow.keys() and not '70' in caseinforow.keys():
                caseinforow[col0[y]] = col3[y] + '$$' + caseinforow[col0[y]]
            else:
                caseinforow[col0[y]] = col3[y]
            y = y + 1
    #if '70' in caseinforow.keys() and re.match(".*\$",caseinforow['70']):
        #caseinforow['70'] = caseinforow['70'][:caseinforow['70'].index('$')]
    historyurl = 'http://11.4.17.176//amlmasrt/sancCaseHistoryTrans.do?caseid=' + caseidlist[i] # +&CAD_SYSID= + sysid
    history = s.get(historyurl, headers=detailheader)
    h_table = BeautifulSoup(history.text, 'lxml').find('table', {'class': 'findnaTable'})
    x = 0
    for tr in h_table.find_all('tr'):
        x = x +1
    print(x)
    j = 0
    for tr in h_table.find_all('tr'):
        if j == x -2:
            y = 0
            for td in tr.find_all('td'):
                if y == 1:
                    caseinforow['MODIFYTIME1'] = td.get_text(strip=True)
                if y == 4:
                    caseinforow['OPERATE1'] = td.get_text(strip=True)
                y = y + 1
        if j == x -1:
            y = 0
            for td in tr.find_all('td'):
                if y == 1:
                    caseinforow['MODIFYTIME2'] = td.get_text(strip=True)
                if y == 4:
                    caseinforow['OPERATE2'] = td.get_text(strip=True)
                y = y + 1
        j = j + 1
    print(caseinforow)
    caseinforows.append(caseinforow.copy())
    i = i + 1

with open('D:\BlackInfo_Out_' + strdate[5:7] + '.csv', 'w', newline='', errors='ignore') as f:  # 案例信息写入SanInfo_Out.csv
    f_csv = csv.DictWriter(f, blackheader)
    f_csv.writeheader()
    f_csv.writerows(blackrows)
with open('D:\CaseInfo_Out_' + strdate[5:7] + '.csv', 'w', newline='', errors='ignore') as f:  # 黑名单信息写入
    f_csv = csv.DictWriter(f, caseinfo_H)
    f_csv.writeheader()
    f_csv.writerows(caseinforows)

